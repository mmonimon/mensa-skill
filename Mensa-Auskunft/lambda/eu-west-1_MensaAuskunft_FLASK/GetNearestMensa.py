import requests
from ask_sdk_core.utils import is_intent_name
import lambda_utility as utility
from prompts import ERROR_PROMPT2
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_model.ui import AskForPermissionsConsentCard

############## GetNearestMensaIntent ########################

class GetNearestMensaHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("GetNearestMensaIntent")(handler_input)
    def handle(self, handler_input):
        """Der Intent gibt die vom Standort des Nutzers aus nächste Mensa und ihre Adresse zurück. 
        Dafür muss der Benutzer seinen Standort für den Skill freigegeben haben. 

        Um die nächste Mensa berechnen zu können, werden die Koordinaten des Nutzers extrahiert. 
        Anschließend wird mithilfe der Haversine-Formel die zum Benutzer nächstgelegene Mensa berechnet.
        Es wird also die Mensa mit der kleinsten Luftlinie zum Nutzer zurückgegeben. 

        Die Koordinaten des Nutzer werden folgendermaßen extrahiert:
            a) Falls der Benutzer ein mobiles Gerät verwendet, werden die aktuellen Koordinaten aus 
            dem GPS-Sensor des Geräts des Nutzers aus dem von Alexa an das Backend gesendete 
            Request-JSON-Objekt extrahiert.
            b) Falls der Benutzer ein stationäres Gerät verwendet, wird die vom Benutzer in der Alexa-App
            bzw. angegebene Adresse aus der Alexa-API extrahiert. Anschließend werden die Koordinaten
            des Nutzers anhand seiner Postleitzahl aproximiert. (Die NominatimAPI wurde entfernt, da
            sie nicht garantiert werden kann, dass sie schnell genug eine Response liefert!
            (Die API erlaubt nur eine Anfrage pro Sekunde.))

        Um dies zu ermöglichen, muss der Nutzer Zugriff auf seinen aktuellen Standort 
        bzw. auf seine Adressdaten in der Alexa-App erlauben.

        Wenn der Benutzer seinen Standort nicht freigegeben hat oder dieser gerade nicht extrahierbar ist, 
        weil z.B. kein GPS-Signal verfügbar ist, werden je nach Errortype unterschiedliche Fehlermeldungen 
        ausgegeben.

        :param handler_input: HandlerInput
        :type handler_input: (HandlerInput) -> Response
        :return: Gibt die vollständige Skill-Antwort zurück
        :rtype: Response
        """
        print("In GetNearestMensaIntent")

        system_context = handler_input.request_envelope.context.system
        # check if mobile device (to get current coordinates of user)
        if system_context.device.supported_interfaces.geolocation:
            geo_location = handler_input.request_envelope.context.geolocation
            # check if coordinates are available
            if geo_location:
                user_coordinates = (float(geo_location.coordinate.latitude_in_degrees),
                                    float(geo_location.coordinate.longitude_in_degrees))
                print('User Coordinates:', user_coordinates)

            # coordinates not available
            else:
                # check if user gave skill permissions to read location data
                if system_context.user.permissions.scopes['alexa::devices:all:geolocation:read'].status.to_str() == "'GRANTED'":
                    # check if location sharing is turned on on user's mobile device
                    if geo_location:
                        
                        # location is turned on -> something else must have gone wrong
                        print("ERROR: Cannot get location although turned on and permission available.")
                        handler_input.response_builder.set_should_end_session(True)
                        return handler_input.response_builder.speak("Oh je. Es scheint, als hätte ich zurzeit Probleme, \
                                deinen Standort ausfindig zu machen. Bitte versuche es später noch einmal. ").response

                    # location sharing is turned off on user's device -> ask to turn on
                    else:
                        print("Location sharing is turned off on device.")
                        handler_input.response_builder.set_should_end_session(True)
                        return handler_input.response_builder.speak("Ich kann nicht auf deinen Standort zugreifen. \
                                Bitte gehe in die Einstellungen deines Geräts und erlaube das Teilen deines Standorts. ").response

                # user did not give permission to skill to share location data -> ask for permission
                else:
                    print("Alexa has no permission to get user's location.")
                    handler_input.response_builder.speak("Um die nächste Mensa zu finden, benötige ich Deinen Standort. \
                                                        Bitte öffne die Alexa-App, um deinen Standort mit mir zu teilen. ")
                    handler_input.response_builder.set_card(AskForPermissionsConsentCard(permissions=['alexa::devices:all:geolocation:read']))
                    handler_input.response_builder.set_should_end_session(True)
                    return handler_input.response_builder.response

        # if not mobile device, check if user has permitted to use their address
        else:
            device_id = system_context.device.device_id
            alexa_api = "https://api.eu.amazonalexa.com/v1/devices/{}/settings/address".format(device_id)

            api_access_token = system_context.api_access_token
            http_header = {'Accept' : 'application/json',
                        'Authorization' : 'Bearer {}'.format(api_access_token)}

            try:
                # retrieve user's address from Alexa API
                address = utility.http_get(alexa_api, headers=http_header)
                print(address)
            except requests.exceptions.HTTPError as e:
                # user has not permitted to use their address -> ask for permission
                if '403 Client Error' in str(e):
                    print("Alexa has no permission to get user's address.")
                    handler_input.response_builder.speak("Um die nächste Mensa zu finden, benötige ich Deine Adresse. \
                                                        Bitte öffne die Alexa-App, um deine Adresse mit mir zu teilen. ")
                    handler_input.response_builder.set_card(AskForPermissionsConsentCard(permissions=['read::alexa:device:all:address']))
                    handler_input.response_builder.set_should_end_session(True)
                    return handler_input.response_builder.response
                # some error ocurred while trying to retrieve user's address
                else:
                    print("ERROR: Alexa has permission but still can't get user's address.")
                    print(e)
                    return handler_input.response_builder.speak(ERROR_PROMPT2).set_should_end_session(True).response
            # user has permitted to use their address, but hasn't filled in address information -> ask to fill in
            except ValueError as e:
                print("Alexa has permission to get user address, but there is no address information.")
                print(e)
                handler_input.response_builder.set_should_end_session(True)
                return handler_input.response_builder.speak("Um die nächste Mensa für Dich zu finden, benötige ich Deine Adresse. \
                        Bitte füge sie in der Alexa-App hinzu. ").response
            # some error ocurred while trying to retrieve user's address
            except Exception as e:
                print("ERROR: Alexa has permission but still can't get user's address.")
                print(e)
                return handler_input.response_builder.speak(ERROR_PROMPT2).set_should_end_session(True).response

            # get approximation of user's coordinates through postal code
            user_coordinates = utility.get_coordinates_from_postcode(address)
            print('Coordinates:', user_coordinates)
            # could not extract user coorddinates (Address could be from a not supported country)
            if user_coordinates is None:
                handler_input.response_builder.speak("Die von dir in der Alexa-App eingegebene Adresse wird leider nicht \
                                                    für die Suche der nächsten Mensa unterstützt!")
                handler_input.response_builder.set_should_end_session(True)
                return handler_input.response_builder.response

        # calculate nearest mensa with haversine formula (airline distance)
        try:
            api_url_base = "https://openmensa.org/api/v2/canteens"
            all_mensas = utility.http_get_iterate(api_url_base)
            nearest_mensa_name, nearest_mensa_address = utility.calculate_nearest_mensa(user_coordinates, all_mensas)
        except Exception as e:
            print(e)
            return handler_input.response_builder.speak(ERROR_PROMPT2).set_should_end_session(True).response

        nearest_mensa_speech = "Die nächste Mensa ist {} in {}.".format(nearest_mensa_name, nearest_mensa_address)
        nearest_mensa_speech = utility.convert_acronyms(nearest_mensa_speech)
        return handler_input.response_builder.speak(nearest_mensa_speech).set_should_end_session(True).response