# -*- coding: utf-8 -*-

import logging
import requests
import six
import random
from datetime import datetime
import lambda_utility as utility

from ask_sdk_core.skill_builder import SkillBuilder
# from ask_sdk.standard import StandardSkillBuilder
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model.slu.entityresolution import StatusCode
from ask_sdk_model import Response

from ask_sdk_model.ui import AskForPermissionsConsentCard
from haversine import haversine

####### LOGGER ##########
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# handler = logging.StreamHandler()
# handler.setLevel(logging.INFO)
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# handler.setFormatter(formatter)
# logger.addHandler(handler)
#########################

# Skill Builder object
# sb = StandardSkillBuilder(table_name="Mensa-Auskunft", auto_create_table=True)
sb = SkillBuilder()

##################################################
# DATA  ##########################################
##################################################

### PROMPTS
ERROR_PROMPT = "Sorry, das kann Mensa-Auskunft leider nicht verstehen. Bitte formuliere deine Frage anders. "
ERROR_PROMPT2 = "Oh je. Es scheint, als würde dieser Service zurzeit nicht funktionieren. Bitte versuche es später noch einmal! "
# SAMPLES1 = "Frag zum Beispiel: Gibt es morgen vegane Gerichte in der Mensa Golm? Oder: Welche Mensen gibt es in Berlin? "
# SAMPLES2 = "Sag zum Beispiel: Gib mir den Essensplan! Oder: Finde Gerichte ohne Fleisch! "
# SAMPLES3 = "Frag zum Beispiel: Wie ist die Adresse der Mensa Golm? Oder: Lies mir den Plan für Montag vor! "

### DATA
api_url_base = "https://openmensa.org/api/v2/canteens"
all_mensas = utility.http_get_iterate(api_url_base)

##################################################
# Request Handler classes ########################
##### OUR OWN SKILL INTENTS ######################
##################################################


############## DetailsIntent ########################

@sb.request_handler(can_handle_func=lambda input: is_intent_name("DetailsIntent")(input))
def details_intent_handler(handler_input):
    """Der Intent listet die Details zu einem bestimmten Gericht auf.

    (Alle verfügbaren Informationen der OpenMensa API.)

    Dazu gehören:
        - Der vollständige Titel des Gerichts
        - Die Preise für Studenten, Angestellte und Andere
        - Die Kategorie des Gerichts
        - Die zusätzlichen Notes
    Der Benutzeranfrage und den bereitgestellten Slot Values werden folgende Daten entnommen:
        - Gerichtnummer

    Über die Session-Attributes müssen folgende Daten abgerufen werden:
        - Daten zu den gespeicherten Gerichten:
            - 'name'
            - 'price'
            - 'category'
            - 'notes'

    :param handler_input: HandlerInput
    :type handler_input: (HandlerInput) -> Response
    :return: Gibt die vollständige Skill-Antwort zurück
    :rtype: Response
    """
    # type: 
    print("In DetailsIntent")
    # extract slot values
    filled_slots = handler_input.request_envelope.request.intent.slots
    # get previous response from session attributes 
    session_attr = handler_input.attributes_manager.session_attributes
    user_groups_de = ['Angestellte', 'Andere', 'Schüler', 'Studenten']

    if 'all_dishes' not in session_attr:
        return handler_input.response_builder.speak("Du musst zuerst Gerichte erfragen,\
                bevor du Details erfahren kannst. ").set_should_end_session(True).response
    
    # extract slot values
    filled_slots = handler_input.request_envelope.request.intent.slots
    slot_values = utility.get_slot_values(filled_slots)
    print(slot_values)
    print(session_attr)
    current_number = slot_values['number']['resolved']
    
    # try to get dish by index
    try:
        dish_name = session_attr['all_dishes'][int(current_number)-1]['name']
        dish_prices = session_attr['all_dishes'][int(current_number)-1]['prices']
        dish_cat = session_attr['all_dishes'][int(current_number)-1]['category']
        dish_notes = session_attr['all_dishes'][int(current_number)-1]['notes']
        user_groups = list(dish_prices.keys())
        speech = "Du hast das Gericht {} ausgewählt. ".format(dish_name)
        speech += "Es kostet "
        # read all prices for each available user group
        for i in range(len(user_groups)):
            price = dish_prices[user_groups[i]]
            if price == None:
                continue
            speech += utility.build_price_speech(price, user_groups_de[i])
        speech += '. Es gehört zur Kategorie: {} und enthält bzw. ist, '.format(dish_cat)
        for i in range(len(dish_notes)):
            if i == len(dish_notes)-2:
                speech += dish_notes[i] + 'und '
            else:
                speech += dish_notes[i] + ', '
        speech += '. '


    # dish cannot be found any more: user may have used a higher number
    except Exception as e:
        speech = "Nanu! Das Gericht Nummer {} konnte nicht wiedergefunden werden. Bitte versuche es erneut. ".format(current_number)
        print("Intent: {}: message: {}".format(handler_input.request_envelope.request.intent.name, str(e)))
    return handler_input.response_builder.speak(speech).set_should_end_session(True).response



############## ListDishesIntent ########################

@sb.request_handler(can_handle_func=lambda input: is_intent_name("ListDishesIntent")(input))
def list_dishes_intent_handler(handler_input):
    """
    Der Intent listet alle verfügbaren Gerichte auf, die nach verschiedenen Mustern gesucht werden:

        1. Zunächst wird eine Mensa und ein Datum festgelegt. Die Slots werden elizitiert, 
        wenn die Nutzeranfrage diese noch nicht enthält.
        2. Die Suchanfrage kann spezifiziert werden, indem der User zusätzlich bis zu zwei Zutaten mit angeben kann,
        die entweder im Gericht enthalten sind oder nicht im Gericht enthalten sein sollen.

    Der Benutzeranfrage und den bereitgestellten Slot Values werden folgende Daten entlockt:
        - Tag bzw. Datum der Suchanfrage (erforderlich)
        - Mensaname (erforderlich)
        - (nicht) erwünschte Zutaten (optional)

    Anschließend wird eine Suchanfrage mithilfe der Mensa-ID und dem Datum gestartet und 
    die Daten von der OpenMensa API erfragt. 
    Diese werden ebenfalls in den Session-Attributes gespeichert.

    Gibt es zusätzlich Zutaten in der Nutzeranfrage, werden die API-Daten gefiltert.

    Zuletzt werden die Ergebnisse in einen String überführt, für den Chunking benutzt wird,
    um die Antwort von Alexa kurz zu halten (siehe lambda_utility.py).

    Außerdem werden bei jedem Turn nur vier Gerichte ausgegeben. Will der Nutzer mehr Gerichte erfahren, 
    muss er nach \"weiteren Gerichten\" fragen.

    :param handler_input: HandlerInput
    :type handler_input: (HandlerInput) -> Response
    :return: Gibt die vollständige Skill-Antwort zurück
    :rtype: Response
    """
    # type: (HandlerInput) -> Response
    print("In ListDishesIntent")
    # extract slot values
    filled_slots = handler_input.request_envelope.request.intent.slots
    slot_values = utility.get_slot_values(filled_slots)

    # extract (un)desired ingredients
    ingredients = {}
    ingredients['first'] = slot_values['first_ingredient']['resolved']
    ingredients['first_prep'] = slot_values['first_prep']['resolved']
    ingredients['second'] = slot_values['second_ingredient']['resolved']
    ingredients['second_prep'] = slot_values['second_prep']['resolved']    

    # assigning session attributes to the mensa_name slot values
    session_attr = handler_input.attributes_manager.session_attributes
    session_attr['current_date'] = slot_values['date']['resolved']
    session_attr['mensa_name'] = slot_values['mensa_name']['resolved']
    session_attr['mensa_id'] = slot_values['mensa_name']['id']
    print(slot_values)

    # Easteregg :P
    if str(ingredients['first']).lower() == 'schlangen' or str(ingredients['second']).lower() == 'schlangen':
        speech = "<say-as interpret-as=\"interjection\">ähm </say-as> <break time=\"0.25s\"/> Herr Schlangen ist nicht zum Verzehr geeignet! "
        return handler_input.response_builder.speak(speech).set_should_end_session(True).response

    # set state for AMAZON.NextIntent
    session_attr['next_intent_state'] = "ListDishes"

    # Mensa does not exist => return error prompt
    if session_attr['mensa_id'] is None:
        speech = "Sorry, Essenspläne für {} habe ich leider nicht im Angebot. ".format(session_attr['mensa_name'])
        return handler_input.response_builder.speak(speech).set_should_end_session(True).response

    # # saving session attributes to persistent attributes
    # #handler_input.attributes_manager.persistent_attributes = session_attr
    # persistent_attr = handler_input.attributes_manager.persistent_attributes
    # # persistent_attr['mensa_name'] = session_attr['mensa_name']
    # persistent_attr['mensa_id'] = session_attr['mensa_id']
    # handler_input.attributes_manager.save_persistent_attributes()
    # print('Persistent attributes: ', persistent_attr)

    # create API link
    try:
        mensa_url = utility.create_mensa_url(mensa_id=session_attr['mensa_id'], date=session_attr['current_date'])
        # request mensa plan from API
        api_response = utility.http_get(mensa_url)
    # No dishes found for requested date or API is down 
    except Exception as e:
        speech = "Sorry, für den ausgewählten Tag {} gibt es leider keinen Essensplan für {}. ".format(session_attr['current_date'], session_attr['mensa_name'])
        print("Intent: {}: message: {}".format('ListDishesIntent', str(e)))
        return handler_input.response_builder.speak(speech).set_should_end_session(True).response

    # try to find matching dishes
    session_attr['all_dishes'] = utility.find_matching_dishes(api_response, ingredients)
    # build speech for dish list
    dish_speech, session_attr['last_idx'] = utility.build_dish_speech(session_attr['all_dishes'], 0)
    ingredients_pre, ingredients_post = utility.build_preposition_speech(ingredients)
    # back up question in case it there is no dish_speech
    question = 'Kann ich sonst noch helfen? '
    # dishes found: build speech with a list of dishes
    if dish_speech:
        if session_attr['last_idx'] < len(session_attr['all_dishes']):
            question = 'Möchtest du mehr Gerichte hören oder Details? '
        else: 
            question = 'Möchtest du Details zu einem dieser Gerichte erfahren? \
                        Sag zum Beispiel: \
                        Details. \
                        oder: Wie viel kostet Gericht Nummer 2 für Studenten. '

        speech = 'Es gibt {} {} Gerichte {} zur Auswahl: {}. {}'.format(len(session_attr['all_dishes']),
                                                                        ingredients_pre,
                                                                        ingredients_post,
                                                                        dish_speech,
                                                                        question)

    # no dishes found, e.g. there is no dish containing the requested ingredients
    else:
        if ingredients_post or ingredients_pre:
            speech = 'Leider gibt es keine passenden {} Gerichte {}. '.format(ingredients_pre,
                                                                             ingredients_post)
        else:
            speech = 'Es gibt leider keine passenden Gerichte zu deiner Anfrage. '
        speech += question
    print('Session attributes: ',session_attr)
    return handler_input.response_builder.speak(speech).ask(question).response


############## PriceIntent ########################

@sb.request_handler(can_handle_func=lambda input: is_intent_name("PriceIntent")(input))
def price_intent_handler(handler_input):
    """Der Intent gibt den Preis für ein bestimmtes Gericht zurück. 
    Der Benutzer muss dabei die Nummer des Gerichts angeben und kann optional eine Zielgruppe
    (Studenten, Angestellte, Andere) definieren.

    Der Benutzeranfrage und den bereitgestellten Slot Values werden folgende Daten entlockt:
        - Nummer des Gerichts (erforderlich)
        - Zielgruppe (optional)

    Über die Session-Attributes müssen folgende Daten abgerufen werden:
        - Daten zu den gespeicherten Gerichten:
            - 'name'
            - 'prices'

    :param handler_input: HandlerInput
    :type handler_input: (HandlerInput) -> Response
    :return: Gibt die vollständige Skill-Antwort zurück
    :rtype: Response
    """
    # type: (HandlerInput) -> Response
    print("In PriceIntent")

    # get previous response from session attributes 
    session_attr = handler_input.attributes_manager.session_attributes
    if 'all_dishes' not in session_attr:
        return handler_input.response_builder.speak("Du musst zuerst Gerichte erfragen,\
                bevor du einen Preis erfahren kannst. ").set_should_end_session(True).response
    
    # define user group names
    user_groups_de = ['Angestellte', 'Andere', 'Schüler', 'Studenten']

    # extract slot values
    filled_slots = handler_input.request_envelope.request.intent.slots
    slot_values = utility.get_slot_values(filled_slots)
    print(slot_values)
    current_number = slot_values['number']['resolved']
    current_usergroup_id = slot_values['user_group']['id']
    current_user = slot_values['user_group']['resolved']

    # try to get dish by index
    try:
        dish_name = session_attr['all_dishes'][int(current_number)-1]['name']
        dish_prices = session_attr['all_dishes'][int(current_number)-1]['prices']
        user_groups = list(dish_prices.keys())
        speech = "Das Gericht {} kostet ".format(dish_name)
        # if user asked for a specific user group, only read this price
        if current_usergroup_id:
            price = dish_prices[current_usergroup_id]
            speech += utility.build_price_speech(price, current_user)
        # if not: read all prices for each available user group
        else:
            for i in range(len(user_groups)):
                price = dish_prices[user_groups[i]]
                if price == None:
                    continue
                speech += utility.build_price_speech(price, user_groups_de[i])
        speech += '. '

    # dish cannot be found any more: user may have used a higher number
    except Exception as e:
        speech = "Nanu! Das Gericht Nummer {} konnte nicht wiedergefunden werden. Bitte versuche es erneut. ".format(current_number)
        print("Intent: {}: message: {}".format(handler_input.request_envelope.request.intent.name, str(e)))
    
    return handler_input.response_builder.speak(speech).set_should_end_session(True).response


############## AddressIntent ########################

@sb.request_handler(can_handle_func=lambda input: is_intent_name("AddressIntent")(input))
def address_intent_handler(handler_input) :
    """Der Intent gibt die Adresse einer Mensa zurück. Benötigt wird der Name der Mensa.
    Ist dieser im Katalog, wird die Adresse zurückgegeben.
    Ist dieser nicht vorhanden, wird eine Fehlermeldung zurückgegeben.

    Der Benutzeranfrage und den bereitgestellten Slot Values werden folgende Daten entlockt:
        - Name und ID der Mensa (erforderlich)

    :param handler_input: HandlerInput
    :type handler_input: (HandlerInput) -> Response
    :return: Gibt die vollständige Skill-Antwort zurück
    :rtype: Response
    """
    # type: (HandlerInput) -> Response
    print("In AddressIntent")
    filled_slots = handler_input.request_envelope.request.intent.slots
    slot_values = utility.get_slot_values(filled_slots)
    print(slot_values)
    current_mensa_id = slot_values['mensa_name']['id']
    current_mensa_name = slot_values['mensa_name']['resolved']
    try:
        name_address = [(j['name'], j['address']) for j in all_mensas if j['id'] == int(current_mensa_id)]
        speech = "Die Adresse der {} lautet {}".format(name_address[0][0], name_address[0][1])
        speech = utility.convert_acronyms(speech)
    except Exception as e:
        speech = "Die Adresse der angefragten Mensa {} konnte leider nicht gefunden werden. ".format(current_mensa_name)
        speech = utility.convert_acronyms(speech)
        print("Intent: {}: message: {}".format(handler_input.request_envelope.request.intent.name, str(e)))
    
    return handler_input.response_builder.speak(speech).set_should_end_session(True).response

@sb.request_handler(can_handle_func=lambda input: is_intent_name("ListMensasIntent")(input))
def list_mensas_intent_handler(handler_input):
    """Der Intent gibt eine Liste mit Mensen in einer Stadt zurück. Benötigt wird der Name der Stadt.
    Sind Mensen vorhanden, werden diese zurückgegeben; gibt es keine oder ist die Stadt nicht in der
    Datenbank, wird eine Fehldermeldung zurückgegeben.

    Bei jedem Turn werden nur vier Mensen ausgegeben. Will der Nutzer mehr Mensen erfahren, muss er 
    nach \"weiteren Mensen\" fragen.

    Der Benutzeranfrage und den bereitgestellten Slot Values werden folgende Daten entlockt:
        - Stadt (erforderlich)

    :param handler_input: HandlerInput
    :type handler_input: (HandlerInput) -> Response
    :return: Gibt die vollständige Skill-Antwort zurück
    :rtype: Response
    """

    # type: (HandlerInput) -> Response
    print("In ListMensasIntent")
    # set state for AMAZON.NextIntent
    session_attr = handler_input.attributes_manager.session_attributes
    session_attr['next_intent_state'] = "ListMensas"
    session_attr['last_idx_mensas'] = 0

    filled_slots = handler_input.request_envelope.request.intent.slots
    slot_values = utility.get_slot_values(filled_slots)
    print(slot_values)
    city = slot_values['city']['resolved']
    city_mensas = [d['name'] for d in all_mensas if d['city'].lower() == city]

    # mensas found: build speech with a list of mensas
    if city_mensas:
      if len(city_mensas) == 1:
        speech = "Ich habe eine Mensa in {} gefunden: {}".format(city, city_mensas[0])
      else:
        session_attr['city_mensas'] = city_mensas
        first_mensas, session_attr['last_idx'] = utility.build_mensa_speech(city_mensas, 0)
        speech = "Ich habe {} Mensen in {} gefunden: {}".format(len(city_mensas), city, first_mensas)
        speech = utility.convert_acronyms(speech)
        if session_attr['last_idx_mensas'] < len(city_mensas):
            question = "Möchtest du mehr Mensen hören? "
            return handler_input.response_builder.speak(speech+question).ask(question).response

    # no mensas found
    else:
        speech = "Leider keine Mensen in {} gefunden.Du kannst eine andere Stadt in Deutschland wählen. ".format(city)

    return handler_input.response_builder.speak(speech).set_should_end_session(True).response


############## GetNearestMensaIntent ########################

@sb.request_handler(can_handle_func=lambda input: is_intent_name("GetNearestMensaIntent")(input))
def get_nearest_mensa_intent_handler(handler_input):
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
           der extrahierten Adresses mithilfe der Nominatim-API ermittelt.

    Um dies zu ermöglichen, muss der Nutzer Zugriff auf seinen aktuellen Standort 
    bzw. auf seine Adressdaten in der Alexa-App erlauben.

    Wenn der Benutzer seinen Standort nicht freigegeben hat oder dieser gerade nicht extrahierbar ist, 
    weil z.B. kein GPS-Signal verfügbar ist, werden je nach Errortype unterschiedliche Fehlermeldungen 
    ausgegeben.

    Es kann vorkommen, dass die NominatimAPI (z.B. weil sie gerade sehr ausgelastet ist) zu lange braucht,
    um die Anfrage des Skills nach den Koordinaten des Nutzers zu beantworten. Ist dies der Fall, so springt
    der Skill in den SessionEndedRequestHandler.

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

        # get coordinates of user's address using nominatim api
        address_string = "{},{},{},{}".format(address['addressLine1'], address['postalCode'], address['city'], address['countryCode'])
        nominatim_api = "https://nominatim.openstreetmap.org/search/{}?format=json&limit=1".format(address_string)
        try:
            location_data = utility.http_get(nominatim_api)[0]
            user_coordinates = (float(location_data['lat']), float(location_data['lon']))
            print("User Coordinates:", user_coordinates)
        except Exception as e:
            print(e)
            return handler_input.response_builder.speak(ERROR_PROMPT2).set_should_end_session(True).response

    # calculate nearest mensa with haversine formula (airline distance)
    try:
       nearest_mensa_name, nearest_mensa_address = utility.calculate_nearest_mensa(user_coordinates, all_mensas)
    except Exception as e:
        print(e)
        return handler_input.response_builder.speak(ERROR_PROMPT2).set_should_end_session(True).response

    nearest_mensa_speech = "Die nächste Mensa ist {} in {}.".format(nearest_mensa_name, nearest_mensa_address)
    nearest_mensa_speech = utility.convert_acronyms(nearest_mensa_speech)
    return handler_input.response_builder.speak(nearest_mensa_speech).set_should_end_session(True).response


################################################
# Request and Response Loggers #################
################################################

@sb.global_response_interceptor()
def log_response(handler_input, response):
    """Response logger."""
    # type: (HandlerInput, Response) -> None
    logger.info("Response: {}".format(response))

@sb.global_request_interceptor()
def log_request(handler_input):
    """Request logger."""
    # type: (HandlerInput) -> None
    logger.info("Request Envelope: {}".format(
                handler_input.request_envelope))

##################################################
# Request Handler classes ########################
##### BUILT IN INTENTS ###########################
##################################################

## AMAZON.WelcomeIntent
@sb.request_handler(can_handle_func=lambda input: is_request_type("LaunchRequest")(input))
def launch_request_handler(handler_input):
    """Der Intent wird beim Öffnen des Skills durch Modal-Launchphrasing getriggert. 
    Er gibt eine Willkommensnachricht zurück.

    :param handler_input: HandlerInput
    :type handler_input: (HandlerInput) -> Response
    :return: Gibt die vollständige Skill-Antwort zurück
    :rtype: Response
    """

    # type: (HandlerInput) -> Response
    print("In LaunchRequestHandler")
    # persist_attr = handler_input.attributes_manager.persistent_attributes
    # print(persist_attr)
    # if persist_attr:
    #     handler_input.attributes_manager.session_attributes = persist_attr
    #     session_attr = handler_input.attributes_manager.session_attributes
    #     session_attr['mensa_name'] = [mensa['name'] for mensa in all_mensas if int(persist_attr['mensa_id']) == mensa['id']][0]
    #     print('Previous Mensa:', session_attr['mensa_name'])
    #     reprompt = 'Möchtest du wieder den Tagesplan für {} hören? '.format(session_attr['mensa_name'])
    #     speech = "Willkommen bei der Mensa-Auskunft! " + reprompt
    #     return handler_input.response_builder.speak(speech).ask(reprompt).response
    speech = "Willkommen bei der Mensaauskunft! Wenn du Hilfe bei der Bedienung brauchst, \
            sag bitte HILFE. Was möchtest du wissen? "
    return handler_input.response_builder.speak(speech).ask("Suchst du nach dem Tagesplan, \
                                                            der Adresse einer Mensa oder eine Auflistung \
                                                            aller Mensen in deiner Stadt? ").response

# ## AMAZON.YesIntent
# @sb.request_handler(can_handle_func=lambda input: is_intent_name("AMAZON.YesIntent")(input))
# def yes_intent_handler(handler_input):
#     # type: (HandlerInput) -> Response
#     print("In YesIntentHandler")
#     session_attr = handler_input.attributes_manager.session_attributes
#     print(session_attr)

#     if not session_attr:
#         speech = "Du musst zuerst eine Mensa auswählen! " + random_phrase([SAMPLES1, SAMPLES2, SAMPLES3])
#         return handler_input.response_builder.speak(speech).ask(speech).response
    
#     # current date should be today => TODO: maybe tomorrow? maybe asking the user again?
#     current_date = datetime.now().strftime("%Y-%m-%d")
#     print(current_date)
#     try:
#         speech, question = list_dishes(session_attr, current_date)
#         print(speech, question)
#     except Exception as e:
#         speech = "Sorry, für den ausgewählten Tag {} gibt es leider keinen Essensplan für {}. ".format(current_date, session_attr['mensa_name'])
#         question = REPROMPT
#         print("Intent: {}: message: {}".format(handler_input.request_envelope.request.intent.name, str(e)))
#     return handler_input.response_builder.speak(speech).ask(question).response

## AMAZON.NoIntent
@sb.request_handler(can_handle_func=lambda input: is_intent_name("AMAZON.NoIntent")(input))
def no_intent_handler(handler_input):
    """
    Der Intent wird ausgelöst, wenn der Benutzer eine Rückfrage des Skills verneint.
    Er gibt eine Verabschiedung zurück und beendet den Skill.

    :param handler_input: HandlerInput
    :type handler_input: (HandlerInput) -> Response
    :return: Gibt die vollständige Skill-Antwort zurück
    :rtype: Response
    """

    # type: (HandlerInput) -> Response
    print("In NoIntentHandler")
    # speech = 'Okay, was möchtest du tun? ' + random_phrase([SAMPLES1, SAMPLES2, SAMPLES3])
    # handler_input.response_builder.speak(speech).ask(REPROMPT)
    return handler_input.response_builder.speak('Okay, tschüss!').set_should_end_session(True).response

## AMAZON.NextIntent
@sb.request_handler(can_handle_func=lambda input: is_intent_name("AMAZON.NextIntent")(input))
def next_intent_handler(handler_input):
    """
    Der Intent führt den ListDishesIntent weiter und listet weitere Gerichte auf.
    Die benötigten Daten werden aus den Session-Attributes entnommen.

    Jeder Turn gibt nur vier Gerichte aus. Will der Nutzer mehr Gerichte erfahren, 
    muss er nach \"weiteren Gerichten\" fragen.

    :param handler_input: HandlerInput
    :type handler_input: (HandlerInput) -> Response
    :return: Gibt die vollständige Skill-Antwort zurück
    :rtype: Response
    """

    # type: (HandlerInput) -> Response
    print("In AMAZON.NextIntent")

    # get previous response from session attributes 
    session_attr = handler_input.attributes_manager.session_attributes

    # if dialogue state for NextIntent not set, unvalid intent
    if 'next_intent_state' not in session_attr:
        speech = "Du musst zuerst eine Suche starten, bevor du weitere Gerichte oder Mensen hören kanst. "
        return handler_input.response_builder.speak(speech).set_should_end_session(True).response
    
    # dialogue state for NextIntent in ListDishes
    if session_attr['next_intent_state'] == 'ListDishes':
        more_dish_speech, session_attr['last_idx'] = utility.build_dish_speech(session_attr['all_dishes'], session_attr['last_idx'])
        if session_attr['last_idx'] < len(session_attr['all_dishes']):
            question = 'Möchtest du mehr Gerichte hören oder Details? '
        else:
            question = 'Möchtest du Details zu einem dieser Gerichte erfahren? \
                    Sag zum Beispiel: \
                    Details. \
                    oder: Wie viel kostet Gericht Nummer 2 für Studenten. '
        return handler_input.response_builder.speak(more_dish_speech+question).ask(question).response

    # dialogue state for NextIntent in ListMensas
    elif session_attr['next_intent_state'] == 'ListMensas':
        more_mensa_speech, session_attr['last_idx_mensas'] = utility.build_mensa_speech(session_attr['city_mensas'], session_attr['last_idx'])
        more_mensa_speech = utility.convert_acronyms(more_mensa_speech)
        if session_attr['last_idx_mensas'] < len(session_attr['city_mensas']):
            question = "Möchtest du mehr Mensen hören?"
            return handler_input.response_builder.speak(more_mensa_speech+question).ask(question).response
        else:
            goodbye = "<say-as interpret-as=\"interjection\">zum wohl</say-as>."
            return handler_input.response_builder.speak(more_mensa_speech+goodbye).set_should_end_session(True).response

    # undefined dialogue state
    else:
        print("Undefined Dialogue State {} in NextIntent".format(session_attributes['next_intent_state']))
        speech = "Du musst zuerst eine Suche starten, bevor du weitere Gerichte oder Mensen hören kanst. "
        return handler_input.response_builder.speak(speech).set_should_end_session(True).response


## AMAZON.HelpIntent
@sb.request_handler(can_handle_func=lambda input: is_intent_name("AMAZON.HelpIntent")(input))
def help_intent_handler(handler_input):
    """
    Der Intent unterstützt den Nutzer bei der Bedienung des Skills. 
    Er informiert den Nutzer über den Umfang des Skills und gibt Beispielanfragen zurück.
    
    :param handler_input: HandlerInput
    :type handler_input: (HandlerInput) -> Response
    :return: Gibt die vollständige Skill-Antwort zurück
    :rtype: Response
    """

    # type: (HandlerInput) -> Response
    print("In HelpIntentHandler")
    speech = "Mensaauskunft kann dir dabei helfen, passende Gerichte in deiner Mensa zu finden! \
            Du kannst nach dem Tagesplan, nach Mensen in deiner Nähe, Adressen und nach einem Gericht mit Zutaten deiner Wahl suchen. \
            Sag zum Beispiel: \
            Alexa, Frage Mensaauskunft, wo die nächste Mensa ist. \
            Alexa, Sag Mensaauskunft, ich brauche die Adresse der Mensa Golm. \
            Alexa, Gib mir den Tagesplan von Mensaauskunft. \
            Alexa, Suche ein Gericht ohne Fleisch für morgen in der Mensa Golm mit Mensaauskunft. \
            Alexa, Frag Mensaauskunft Golm, was es morgen zu essen gibt."
    return handler_input.response_builder.speak(speech).set_should_end_session(True).response

## AMAZON.StopIntent
@sb.request_handler(can_handle_func=lambda input: is_intent_name("AMAZON.CancelIntent")(input) or
                is_intent_name("AMAZON.StopIntent")(input))
def exit_intent_handler(handler_input):
    """
    Der Intent stoppt den Skill mit einer Verabschiedung.
    
    :param handler_input: HandlerInput
    :type handler_input: (HandlerInput) -> Response
    :return: Gibt die vollständige Skill-Antwort zurück
    :rtype: Response
    """

    # type: (HandlerInput) -> Response
    print("In ExitIntentHandler")
    handler_input.response_builder.speak("Guten Hunger! ").set_should_end_session(True)
    return handler_input.response_builder.response

## ExitAppIntent (schließen, verlassen...)
@sb.request_handler(can_handle_func=lambda input: is_request_type("SessionEndedRequest")(input))
def session_ended_request_handler(handler_input):
    """
    Der Intent stoppt den Skill ohne Verabschiedung.
    
    :param handler_input: HandlerInput
    :type handler_input: (HandlerInput) -> Response
    :return: Gibt die response ohne Antwort zurück
    :rtype: Response
    """

    # type: (HandlerInput) -> Response
    print("In SessionEndedRequestHandler")
    print("Session ended with reason: {}".format(handler_input.request_envelope.request.reason))
    return handler_input.response_builder.set_should_end_session(True).response


## AMAZON.FallbackIntent
@sb.request_handler(can_handle_func=lambda input: is_intent_name("AMAZON.FallbackIntent")(input))
def fallback_intent_handler(handler_input):
    """
    Der Intent informiert den Benutzer darüber, dass der Skill die gewünschte Funktionalität nicht besitzt
    und beendet ihn.

    :param handler_input: HandlerInput
    :type handler_input: (HandlerInput) -> Response
    :return: Gibt die vollständige Skill-Antwort zurück
    :rtype: Response
    """
    # type: (HandlerInput) -> Response
    print("In FallbackIntentHandler")
    return handler_input.response_builder.speak(ERROR_PROMPT).set_should_end_session(True).response

## Exception Handler
@sb.exception_handler(can_handle_func=lambda i, e: True)
def all_exception_handler(handler_input, exception):
    """
    Der Intent ist ein Fallback für alle Exceptions. Er informiert darüber, 
    dass der Skill die gewünschte Funktionalität nicht besitzt und beendet ihn.

    :param handler_input: HandlerInput
    :type handler_input: (HandlerInput) -> Response
    :return: Gibt die vollständige Skill-Antwort zurück
    :rtype: Response
    """

    # type: (HandlerInput, Exception) -> Response
    logger.error(exception, exc_info=True)
    return handler_input.response_builder.speak(ERROR_PROMPT).set_should_end_session(True).response

## Unhandled handler
@sb.request_handler(can_handle_func=lambda input: True)
def unhandled_intent_handler(handler_input):
    """
    Ein Intent für alle "Unhandled requests". Er informiert darüber, 
    dass der Skill die gewünschte Funktionalität nicht besitzt und beendet ihn.

    :param handler_input: HandlerInput
    :type handler_input: (HandlerInput) -> Response
    :return: Gibt die vollständige Skill-Antwort zurück
    :rtype: Response
    """

    # type: (HandlerInput) -> Response
    return handler_input.response_builder.speak(ERROR_PROMPT).set_should_end_session(True).response

lambda_handler = sb.lambda_handler()