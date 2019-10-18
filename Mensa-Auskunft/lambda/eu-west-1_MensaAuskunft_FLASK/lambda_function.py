# -*- coding: utf-8 -*-

import logging, requests
import lambda_utility as utility
from datetime import datetime

from flask import Flask
from ask_sdk_core.skill_builder import SkillBuilder
from flask_ask_sdk.skill_adapter import SkillAdapter

# from ask_sdk.standard import StandardSkillBuilder
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput

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

app = Flask(__name__)

# Skill Builder object
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
print(len(all_mensas))

##################################################
# Request Handler classes ########################
##### OUR OWN SKILL INTENTS ######################
##################################################

@sb.request_handler(can_handle_func=lambda input: is_intent_name("DetailsIntent")(input))
def details_intent_handler(handler_input):
    # type: (HandlerInput) -> Response
    print("In DetailsIntent")
    # extract slot values
    filled_slots = handler_input.request_envelope.request.intent.slots
    # get previous response from session attributes 
    session_attr = handler_input.attributes_manager.session_attributes
    user_groups_de = ['Angestellte', 'Andere', 'Schüler', 'Studenten']

    if 'all_dishes' not in session_attr:
        return handler_input.response_builder.speak("Du musst zuerst Gerichte erfragen,\
                bevor du Details erfahren kannst. ").response
    
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
    return handler_input.response_builder.speak(speech).response

@sb.request_handler(can_handle_func=lambda input: is_intent_name("ListDishesIntent")(input))
def list_dishes_intent_handler(handler_input, current_date=None):
    # type: (HandlerInput) -> Response
    print("In ListDishesIntent")
    # extract slot values
    filled_slots = handler_input.request_envelope.request.intent.slots
    slot_values = utility.get_slot_values(filled_slots)
    if current_date is None:
        current_date = slot_values['date']['resolved']
    # extract (un)desired ingredients
    ingredients = {}
    ingredients['first'] = slot_values['first_ingredient']['resolved']
    ingredients['first_prep'] = slot_values['first_prep']['resolved']
    ingredients['second'] = slot_values['second_ingredient']['resolved']
    ingredients['second_prep'] = slot_values['second_prep']['resolved']    

    # assigning session attributes to the mensa_name slot values
    session_attr = handler_input.attributes_manager.session_attributes
    session_attr['mensa_name'] = slot_values['mensa_name']['resolved']
    session_attr['mensa_id'] = slot_values['mensa_name']['id']
    print(slot_values)    

    # Mensa does not exist => return error prompt
    if session_attr['mensa_id'] is None:
        speech = "Sorry, Essenspläne für {} habe ich leider nicht im Angebot. ".format(session_attr['mensa_name'])
        return handler_input.response_builder.speak(speech).response

    # # saving session attributes to persistent attributes
    # #handler_input.attributes_manager.persistent_attributes = session_attr
    # persistent_attr = handler_input.attributes_manager.persistent_attributes
    # # persistent_attr['mensa_name'] = session_attr['mensa_name']
    # persistent_attr['mensa_id'] = session_attr['mensa_id']
    # handler_input.attributes_manager.save_persistent_attributes()
    # print('Persistent attributes: ', persistent_attr)

    # try to find matching dishes
    speech, question = utility.list_dishes(session_attr, current_date, ingredients)
    print('Session attributes: ',session_attr)
    return handler_input.response_builder.speak(speech).ask(question).response

@sb.request_handler(can_handle_func=lambda input: is_intent_name("PriceIntent")(input))
def price_intent_handler(handler_input):
    # type: (HandlerInput) -> Response
    print("In PriceIntent")

    # get previous response from session attributes 
    session_attr = handler_input.attributes_manager.session_attributes
    if 'all_dishes' not in session_attr:
        return handler_input.response_builder.speak("Du musst zuerst Gerichte erfragen,\
                bevor du einen Preis erfahren kannst. ").response
    
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
    
    return handler_input.response_builder.speak(speech).response


@sb.request_handler(can_handle_func=lambda input: is_intent_name("AddressIntent")(input))
def address_intent_handler(handler_input, json_data=all_mensas) :
    # type: (HandlerInput) -> Response
    print("In AddressIntent")
    filled_slots = handler_input.request_envelope.request.intent.slots
    slot_values = utility.get_slot_values(filled_slots)
    print(slot_values)
    current_mensa_id = slot_values['mensa_name']['id']
    current_mensa_name = slot_values['mensa_name']['resolved']
    try:
        address = [j['address'] for j in json_data if j['id'] == int(current_mensa_id)]
        speech = "Die Adresse der {} lautet {}".format(current_mensa_name,address[0])
    except Exception as e:
        speech = "Die Adresse der angefragten Mensa konnte leider nicht wiedergefunden werden. "
        print("Intent: {}: message: {}".format(handler_input.request_envelope.request.intent.name, str(e)))
    
    return handler_input.response_builder.speak(speech).response

@sb.request_handler(can_handle_func=lambda input: is_intent_name("ListMensasIntent")(input))
def list_mensas_intent_handler(handler_input, all_mensas=all_mensas):
    # type: (HandlerInput) -> Response
    print("In ListMensasIntent")
    filled_slots = handler_input.request_envelope.request.intent.slots
    slot_values = utility.get_slot_values(filled_slots)
    print(slot_values)
    city = slot_values['city']['resolved']
    try:
        speech = 'Es gibt die folgenden Mensas in {}:\n'.format(city)
        for diction in all_mensas:
            if diction['city'].lower() == city:
                speech += '{}, '.format(diction['name'])
        speech += '.'
    except Exception as e:
        speech = "Leider keine Mensas gefunden. Du kannst eine andere Stadt wählen. "
        print("Intent: {}: message: {}".format(handler_input.request_envelope.request.intent.name, str(e)))

    return handler_input.response_builder.speak(speech).response

@sb.request_handler(can_handle_func=lambda input: is_intent_name("GetNearestMensaIntent")(input))
def get_nearest_mensa_intent_handler(handler_input):
    print("In GetNearestMensaIntent")
    # device_id = handler_input.request_envelope.context.system.device.device_id
    # access_token = handler_input.request_envelope.context.system.api_access_token
    # print ("DeviceID:", device_id)
    # print("AccessToken:", access_token)

    system_context = handler_input.request_envelope.context.system
    # check if mobile device (to get current coordinates of user)
    if system_context.device.supported_interfaces.geolocation:
        geo_location = handler_input.request_envelope.context.geolocation
        # check if coordinates are available
        if geo_location:
            user_latitude = float(geo_location.coordinate.latitude_in_degrees)
            user_longitude = float(geo_location.coordinate.longitude_in_degrees)
            print("Latitude:", user_latitude)
            print("Longitude:", user_longitude)

        # coordinates not available
        else:
            # check if user gave skill permissions to read location data
            if system_context.user.permissions.scopes['alexa::devices:all:geolocation:read'].status.to_str() == "'GRANTED'":
                # check if location sharing is turned on on user's mobile device
                if geo_location:
                    
                    # location is turned on -> something else must have gone wrong
                    print("ERROR: Cannot get location although turned on and permission available.")
                    return handler_input.response_builder.speak("Oh je. Es scheint, als hätte ich zurzeit Probleme, \
                            deinen Standort ausfindig zu machen. Bitte versuche es später noch einmal. ").response

                # location sharing is turned off on user's device -> ask to turn on
                else:
                    print("Location sharing is turned off on device.")
                    return handler_input.response_builder.speak("Ich kann nicht auf deinen Standort zugreifen. \
                            Bitte gehe in die Einstellungen deines Geräts und erlaube das Teilen deines Standorts. ").response

            # user did not give permission to skill to share location data -> ask for permission
            else:
                print("Alexa has no permission to get user's location.")
                handler_input.response_builder.speak("Um die nächste Mensa zu finden, benötige ich Deinen Standort. \
                                                    Bitte öffne die Alexa-App, um deinen Standort mit mir zu teilen. ")
                handler_input.response_builder.set_card(AskForPermissionsConsentCard(permissions=['alexa::devices:all:geolocation:read']))
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
                return handler_input.response_builder.response
            # some error ocurred while trying to retrieve user's address
            else:
                print("ERROR: Alexa has permission but still can't get user's address.")
                print(e)
                return handler_input.response_builder.speak(ERROR_PROMPT2).response
        # user has permitted to use their address, but hasn't filled in address information -> ask to fill in
        except ValueError as e:
            print("Alexa has permission to get user address, but there is no address information.")
            print(e)
            return handler_input.response_builder.speak("Um die nächste Mensa für Dich zu finden, benötige ich Deine Adresse. \
                    Bitte füge sie in der Alexa-App hinzu. ").response
        # some error ocurred while trying to retrieve user's address
        except Exception as e:
            print("ERROR: Alexa has permission but still can't get user's address.")
            print(e)
            return handler_input.response_builder.speak(ERROR_PROMPT2).response

        # get coordinates of user's address using nominatim api
        address_string = "{},{},{},{}".format(address['addressLine1'], address['postalCode'], address['city'], address['countryCode'])
        nominatim_api = "https://nominatim.openstreetmap.org/search/{}?format=json&limit=1".format(address_string)
        try:
            location_data = utility.http_get(nominatim_api)[0]
            user_latitude = float(location_data['lat'])
            user_longitude = float(location_data['lon'])
            print("Latitude:", user_latitude)
            print("Longitude:", user_longitude)
        except Exception as e:
            print(e)
            return handler_input.response_builder.speak(ERROR_PROMPT2).response

    # calculate nearest mensa with haversine formula (airline distance)
    nearest_mensa = None
    shortest_distance = None
    for mensa in all_mensas:
        # check if coordinates availabe
        if mensa['coordinates']:
            mensa_latitude = mensa['coordinates'][0]
            mensa_longitude = mensa['coordinates'][1]
        # coordinates not available -> retrieve from address
        else:
            # get coordinates of mensa using nominatim api
            address_string = mensa['address']
            nominatim_api = "https://nominatim.openstreetmap.org/search/{}?format=json&limit=1".format(address_string)
            try:
                location_data = utility.http_get(nominatim_api)[0]
                mensa_latitude = float(location_data['lat'])
                mensa_longitude = float(location_data['lon'])
            except IndexError:
                pass
            except Exception as e:
                print(e)
                return handler_input.response_builder.speak(ERROR_PROMPT2).response

        distance = haversine((user_latitude, user_longitude), (mensa_latitude,mensa_longitude))
        if shortest_distance is None or distance < shortest_distance:
            shortest_distance = distance
            nearest_mensa = mensa

    nearest_mensa_name = nearest_mensa['name']
    nearest_mensa_address = nearest_mensa['address']

    nearest_mensa_speech = "Die nächste Mensa ist {} in {}.".format(nearest_mensa_name, nearest_mensa_address)
    return handler_input.response_builder.speak(nearest_mensa_speech).response


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
def launch_request_handler(handler_input, all_mensas=all_mensas):
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
    # type: (HandlerInput) -> Response
    print("In NoIntentHandler")
    # speech = 'Okay, was möchtest du tun? ' + random_phrase([SAMPLES1, SAMPLES2, SAMPLES3])
    # handler_input.response_builder.speak(speech).ask(REPROMPT)
    return handler_input.response_builder.speak('Okay, tschüss!').response


## AMAZON.HelpIntent
@sb.request_handler(can_handle_func=lambda input: is_intent_name("AMAZON.HelpIntent")(input))
def help_intent_handler(handler_input):
    # type: (HandlerInput) -> Response
    print("In HelpIntentHandler")
    speech = "Mensaauskunft kann dir dabei helfen, passende Gerichte in deiner Mensa zu finden! \
            Du kannst nach dem Tagesplan, nach Mensen in deiner Nähe, Adressen und nach einem Gericht mit Zutaten deiner Wahl suchen. \
            Sag zum Beispiel: \
            Frage Mensaauskunft, wo die nächste Mensa ist. \
            Sag Mensaauskunft, ich brauche die Adresse der Mensa Golm. \
            Gib mir den Tagesplan von Mensaauskunft. \
            Suche ein Gericht ohne Fleisch für morgen in der Mensa Golm mit Mensaauskunft. \
            Frag Mensaauskunft Golm, was es morgen zu essen gibt."
    return handler_input.response_builder.speak(speech).response

## AMAZON.StopIntent
@sb.request_handler(can_handle_func=lambda input: is_intent_name("AMAZON.CancelIntent")(input) or
                is_intent_name("AMAZON.StopIntent")(input))
def exit_intent_handler(handler_input):
    # type: (HandlerInput) -> Response
    print("In ExitIntentHandler")
    handler_input.response_builder.speak("Guten Hunger! ").set_should_end_session(True)
    return handler_input.response_builder.response

## ExitAppIntent (schließen, verlassen...)
@sb.request_handler(can_handle_func=lambda input: is_request_type("SessionEndedRequest")(input))
def session_ended_request_handler(handler_input):
    # type: (HandlerInput) -> Response
    print("In SessionEndedRequestHandler")
    print("Session ended with reason: {}".format(handler_input.request_envelope.request.reason))
    return handler_input.response_builder.response


## AMAZON.FallbackIntent
@sb.request_handler(can_handle_func=lambda input: is_intent_name("AMAZON.FallbackIntent")(input))
def fallback_intent_handler(handler_input):
    # type: (HandlerInput) -> Response
    print("In FallbackIntentHandler")
    return handler_input.response_builder.speak(ERROR_PROMPT).response

## Exception Handler
@sb.exception_handler(can_handle_func=lambda i, e: True)
def all_exception_handler(handler_input, exception):
    # type: (HandlerInput, Exception) -> Response
    logger.error(exception, exc_info=True)
    return handler_input.response_builder.speak(ERROR_PROMPT).response

## Unhandled handler
@sb.request_handler(can_handle_func=lambda input: True)
def unhandled_intent_handler(handler_input):
    # type: (HandlerInput) -> Response
    return handler_input.response_builder.speak(ERROR_PROMPT).response

lambda_handler = sb.lambda_handler()

# --- flask
skill_adapter = SkillAdapter(skill=sb.create(), skill_id='TEST', app=app)

@app.route("/", methods=['POST'])
def invoke_skill():
    return skill_adapter.dispatch_request()

if __name__ == '__main__':
    app.run(debug=True)
