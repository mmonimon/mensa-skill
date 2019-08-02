# -*- coding: utf-8 -*-

import logging
import requests
import six
import random
from datetime import datetime

from flask import Flask
from ask_sdk_core.skill_builder import SkillBuilder
from flask_ask_sdk.skill_adapter import SkillAdapter

from ask_sdk.standard import StandardSkillBuilder
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model.slu.entityresolution import StatusCode
from ask_sdk_model import Response

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
sb = StandardSkillBuilder(table_name="Mensa-Auskunft", auto_create_table=True)


################################################
# Utility functions ############################
################################################

def create_mensa_url(mensa_id, date):
    return 'https://openmensa.org/api/v2/canteens/{}/days/{}/meals'.format(mensa_id, date)

def random_phrase(str_list):
    """Return random element from list."""
    # type: List[str] -> str
    return random.choice(str_list)

def http_get(url):
    response = requests.get(url)
    if response.status_code < 200 or response.status_code >= 300:
        response.raise_for_status()
    return response.json()

def build_dish_speech(dishlist):
    dishlist_string = ''
    for count, dish in enumerate(dishlist, 1):
        if count == len(dishlist):
            dishlist_string += '{}. {}'.format(count, dish['name'])
        elif count == (len(dishlist) - 1):
            dishlist_string += '{}. {} und '.format(count, dish['name'])
        else:
            dishlist_string += '{}. {}, '.format(count, dish['name'])

    return dishlist_string


def build_price_speech(price, user):
    return '{} Euro für {}, '.format(str(price).replace('.',','), user)

def get_resolved_value(request, slot_name):
    """Resolve the slot name from the request using resolutions."""
    # type: (IntentRequest, str) -> Union[str, None]
    try:
        return (request.intent.slots[slot_name].resolutions.
                resolutions_per_authority[0].values[0].value.name)
    except (AttributeError, ValueError, KeyError, IndexError, TypeError) as e:
        print("Couldn't resolve {} for request: {}".format(slot_name, request))
        # print(str(e))
        return None

def get_slot_values(filled_slots):
    """Return slot values with additional info."""
    # type: (Dict[str, Slot]) -> Dict[str, Any]
    slot_values = {}
    # print("Filled slots: {}".format(filled_slots))
    
    for key, slot_item in six.iteritems(filled_slots):
        name = slot_item.name
        try:
            status_code = slot_item.resolutions.resolutions_per_authority[0].status.code
            
            if status_code == StatusCode.ER_SUCCESS_MATCH:
                slot_values[name] = {
                    "synonym": slot_item.value,
                    "resolved": slot_item.resolutions.resolutions_per_authority[0].values[0].value.name,
                    "id": slot_item.resolutions.resolutions_per_authority[0].values[0].value.id,
                    "is_validated": True,
            }
            elif status_code == StatusCode.ER_SUCCESS_NO_MATCH:
                slot_values[name] = {
                    "synonym": slot_item.value,
                    "resolved": slot_item.value,
                    "id": None,
                    "is_validated": False,
            }
            else:
                pass
        except (AttributeError, ValueError, KeyError, IndexError, TypeError) as e:
            # print("Couldn't resolve status_code for slot item: {}".format(slot_item))
            # print(e)
            slot_values[name] = {
                "synonym": slot_item.value,
                    "resolved": slot_item.value,
                        "id": None,
                        "is_validated": False,
                }
    return slot_values

##################################################
# DATA  ##########################################
##################################################

### PROMPTS
WELCOME_PROMPT = "Willkommen bei der Mensa-Auskunft! "
HELP_PROMPT = "Ich kann dir dabei helfen, eine Auskunft über das Essen in der Mensa zu erhalten! "
REPROMPT = "Suchst du nach dem Tagesplan, der Adresse einer Mensa oder eine Auflistung aller Mensen in deiner Stadt? "
SAD_PROMPT = "Sorry, dabei kann Mensa-Auskunft leider nicht helfen. "
ERROR_PROMPT = "Sorry, das kann Mensa-Auskunft leider nicht verstehen. Bitte versuche es erneut. "
ERROR_PROMPT1 = "Sorry, für den ausgewählten Tag {} gibt es leider keinen Essensplan für {}. "
ERROR_PROMPT2 = "Sorry, Essenspläne für {} habe ich leider nicht im Angebot. "
ERROR_PROMPT3 = "Nanu! Das Gericht Nummer {} konnte nicht wiedergefunden werden. Bitte versuche es erneut. "
ERROR_PROMPT4 = "Die Adresse der angefragten Mensa konnte leider nicht wiedergefunden werden. "
ERROR_PROMPT5 = "Leider keine Mensas gefunden. Du kannst eine andere Stadt wählen. "
ERROR_PROMPT6 = "Du musst zuerst Gerichte erfragen, bevor du einen Preis erfahren kannst. "
SAMPLES1 = "Frag zum Beispiel: Gibt es morgen vegane Gerichte in der Mensa Golm? Oder: Welche Mensen gibt es in Berlin? "
SAMPLES2 = "Sag zum Beispiel: Gib mir den Essensplan! Oder: Finde Gerichte ohne Fleisch! "
SAMPLES3 = "Frag zum Beispiel: Wie ist die Adresse der Mensa Golm? Oder: Lies mir den Plan für Montag vor! "
PRICE_QUESTION = 'Möchtest du den Preis eines dieser Gerichte erfahren? \
            Frag zum Beispiel: Wie viel kostet Gericht Nummer 2 für Studenten? '
PRICE_REPROMPT = 'Möchtest du noch einen anderen Preis erfahren? Sage bitte die Nummer des Gerichts. '

### DATA
api_url_base = "https://openmensa.org/api/v2/canteens"
all_mensas = http_get(api_url_base)
# print(all_mensas)

##################################################
# Request Handler classes ########################
##### OUR OWN SKILL INTENTS ######################
##################################################

def list_dishes(session_attr, current_date, ingredients={'first' : None, 'second' : None}):
    print("In ListDishes-Function")

    # create API link
    mensa_url = create_mensa_url(mensa_id=session_attr['mensa_id'], date=current_date)
    # request mensa plan from API
    response_dishes = http_get(mensa_url)

    count = 0
    dish_speech = ''
    optional_speech = ''
    session_attr['all_dishes'] = []

    # create list of desired dishes
    # user did not include optional (un)desired ingredient(s) in utterance --> list all dishes
    if (not ingredients['first']) and (not ingredients['second']):
        session_attr['all_dishes'] = response_dishes

    # user included at least one (un)desired ingredient in utterance
    elif ingredients['first']:
        # first_ingredient is 'fleisch'
        if ingredients['first'].lower() == 'fleisch':
            session_attr['all_dishes'] = ingredient_fleisch(response_dishes, ingredients['first_prep'], None)

        else:
            # ingredient is undesired
            # sample utterance: 
            #   - "Suche Gerichte ohne {first_ingredient} ..."
            if ingredients['first_prep'] == 'ohne':
                undesired_ingredient = ingredients['first'].lower()
                # add all dishes without undesired ingredient
                session_attr['all_dishes'] = [dish 
                                              for dish in response_dishes 
                                              if not ingredient_in_dish(undesired_ingredient, dish)]

            # ingredient is desired
            # sample utterances:
            #   - "Suche Gerichte mit {first_ingredient} ..."
            #   - "Suche {first_ingredient} Gerichte ..."
            else:
                desired_ingredient = ingredients['first'].lower()
                # add all dishes with desired ingredient
                session_attr['all_dishes'] = [dish 
                                              for dish in response_dishes 
                                              if ingredient_in_dish(desired_ingredient, dish)]

        # user included another (un)desired ingredient in utterance
        if ingredients['second']:
            if ingredients['second'].lower() == 'fleisch':
                session_attr['all_dishes'] = ingredient_fleisch(session_attr['all_dishes'],
                                                                ingredients['first_prep'],
                                                                ingredients['second_prep'],
                                                                is_first_ingredient=False)

            else:
                # ingredient is undesired
                # sample utterances:
                #   - "Suche Gerichte mit {first_ingredient} und ohne {second_ingredient}"
                #   - "Suche {first_ingredient} Gerichte ohne {second_ingredient}"
                #   - "Suche Gerichte ohne {first_ingredient} und {second_ingredient}"
                if (ingredients['second_prep'] == 'ohne') or \
                   ((ingredients['second_prep'] is None) and (ingredients['first_prep'] == 'ohne')):
                    
                    undesired_ingredient = ingredients['second'].lower()
                    # remove all dishes with undesired ingredient
                    session_attr['all_dishes'] = [dish
                                                  for dish in session_attr['all_dishes']
                                                  if not ingredient_in_dish(undesired_ingredient, dish)]

                # ingredient is desired
                # sample utterances:
                #   - "Suche Gerichte mit {first_ingredient} und {second_ingredient}"
                #   - "Suche {first_ingredient} Gerichte mit {second_ingredient}"
                else:
                    desired_ingredient = ingredients['second'].lower()
                    # remove all dishes without desired ingredient
                    session_attr['all_dishes'] = [dish
                                                  for dish in session_attr['all_dishes']
                                                  if ingredient_in_dish(desired_ingredient, dish)]


    # build speech for dish list
    dish_speech = build_dish_speech(session_attr['all_dishes'])

    # build speech for first and second ingredient
    ingredients_pre = ''
    ingredients_post = ''
    # user included one ingredient in utterance
    if ingredients['first']:
        if ingredients['first_prep']:
            ingredients_post = '{} {}'.format(ingredients['first_prep'], ingredients['first'])
        else:
            ingredients_pre = ingredients['first']
    # user included another ingredient in utterance
    if ingredients['second']:
        if ingredients['second_prep'] and ingredients['first_prep'] is None:
            ingredients_post = '{} {}'.format(ingredients['second_prep'], ingredients['second'])
        elif ingredients['second_prep']:
            ingredients_post += ' und {} {}'.format(ingredients['second_prep'], ingredients['second'])
        else:
            ingredients_post += ' und {}'.format(ingredients['second'])

    # dishes found: build speech with a list of dishes
    if dish_speech:
        question = PRICE_QUESTION
        speech = 'Es gibt {} {} Gerichte {} zur Auswahl: {}. {}'.format(len(session_attr['all_dishes']),
                                                                        ingredients_pre,
                                                                        ingredients_post,
                                                                        dish_speech,
                                                                        question)
        # speech = ' '.join(speech.split())

    # no dishes found, e.g. there is no dish containing the requested ingredients
    else:
        question = 'Kann ich sonst noch helfen? ' + random_phrase([SAMPLES1, SAMPLES2, SAMPLES3])
        if ingredients_post or ingredients_pre:
            speech = 'Leider gibt es keine passenden {} Gerichte {}. Such doch mal nach einem Gericht ohne Fleisch!'.format(ingredients_pre,
                                                                                                                            ingredients_post)
            # speech = ' '.join(speech.split())
        else:
            speech = 'Es gibt leider keine passenden Gerichte zu deiner Anfrage.'

    return speech, question


# returns True if a given ingredient is found in a dish (in 'notes' or in dish-string) 
def ingredient_in_dish(ingredient, dish) :
    # ingredient found in 'notes' ingredient is substring of 'name'
    if [note for note in dish['notes'] if (ingredient in note.lower())] or \
        ingredient in dish['name'].lower():

        return True

    # ingredient not found
    return False

# return dishes with / without meat (as this is not marked in a general way in API data)
def ingredient_fleisch(dishlist, first_prep, second_prep, is_first_ingredient=True):
    if is_first_ingredient:
        # meat is undesired
        if first_prep == 'ohne':
            return [dish
                    for dish in dishlist
                    if ingredient_in_dish('vegan', dish) or \
                       ingredient_in_dish('vegetarisch', dish) or \
                       ingredient_in_dish('fisch', dish)]
        # meat is desired
        else:
            return [dish
                    for dish in dishlist
                    if not(ingredient_in_dish('vegan', dish) or \
                           ingredient_in_dish('vegetarisch', dish) or \
                           ingredient_in_dish('fisch', dish))]

    else:
        # meat is undesired
        if (second_prep == 'ohne') or \
           ((second_prep is None) and first_prep  == 'ohne'):

            return [dish
                    for dish in dishlist
                    if ingredient_in_dish('vegan', dish) or \
                       ingredient_in_dish('vegetarisch', dish) or \
                       ingredient_in_dish('fisch', dish)]
        # meat is desired
        else:
            return [dish
                    for dish in dishlist
                    if not(ingredient_in_dish('vegan', dish) or \
                           ingredient_in_dish('vegetarisch', dish) or \
                           ingredient_in_dish('fisch', dish))]


@sb.request_handler(can_handle_func=lambda input: is_intent_name("ListDishesIntent")(input))
def list_dishes_intent_handler(handler_input, current_date=None):
    # type: (HandlerInput) -> Response
    print("In ListDishesIntent")
    # extract slot values
    filled_slots = handler_input.request_envelope.request.intent.slots
    slot_values = get_slot_values(filled_slots)
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
        speech = ERROR_PROMPT2.format(session_attr['mensa_name'])
        return handler_input.response_builder.speak(speech).response

    # saving session attributes to persistent attributes
    #handler_input.attributes_manager.persistent_attributes = session_attr
    persistent_attr = handler_input.attributes_manager.persistent_attributes
    # persistent_attr['mensa_name'] = session_attr['mensa_name']
    persistent_attr['mensa_id'] = session_attr['mensa_id']
    handler_input.attributes_manager.save_persistent_attributes()
    print('Persistent attributes: ', persistent_attr)

    # try to find matching dishes
    try:
        speech, question = list_dishes(session_attr, current_date, ingredients)
    # No dishes found for requested date or API is down 
    except Exception as e:
        speech = ERROR_PROMPT1.format(current_date, session_attr['mensa_name'])
        question = REPROMPT
        print("Intent: {}: message: {}".format(handler_input.request_envelope.request.intent.name, str(e)))
    print('Session attributes: ',session_attr)
    # return the speech
    return handler_input.response_builder.speak(speech).ask(question).response
    

@sb.request_handler(can_handle_func=lambda input: is_intent_name("PriceIntent")(input))
def price_intent_handler(handler_input):
    # type: (HandlerInput) -> Response
    print("In PriceIntent")

    # get previous response from session attributes 
    session_attr = handler_input.attributes_manager.session_attributes
    if 'all_dishes' not in session_attr:
        return handler_input.response_builder.speak(ERROR_PROMPT6).ask(SAMPLES2).response
    
    # define user group names
    user_groups_de = ['Angestellte', 'Andere', 'Schüler', 'Studenten']

    # extract slot values
    filled_slots = handler_input.request_envelope.request.intent.slots
    slot_values = get_slot_values(filled_slots)
    print(slot_values)
    current_number = slot_values['number']['resolved']
    current_usergroup_id = slot_values['user_group']['id']
    current_user = slot_values['user_group']['resolved']

    # try do get dish by index
    try:
        dish_name = session_attr['all_dishes'][int(current_number)-1]['name']
        dish_prices = session_attr['all_dishes'][int(current_number)-1]['prices']
        user_groups = list(dish_prices.keys())
        speech = "Das Gericht {} kostet ".format(dish_name)
        # if user asked for a specific user group, only read this price
        if current_usergroup_id:
            price = dish_prices[current_usergroup_id]
            speech += build_price_speech(price, current_user)
        # if not: read all prices for each available user group
        else:
            for i in range(len(user_groups)):
                price = dish_prices[user_groups[i]]
                if price == None:
                    continue
                speech += build_price_speech(price, user_groups_de[i])
        speech += '. ' + PRICE_REPROMPT

    # dish cannot be found any more: user may have used a higher number
    except Exception as e:
        speech = ERROR_PROMPT3.format(current_number)
        print("Intent: {}: message: {}".format(handler_input.request_envelope.request.intent.name, str(e)))
    
    return handler_input.response_builder.speak(speech).ask(PRICE_REPROMPT).response


@sb.request_handler(can_handle_func=lambda input: is_intent_name("AddressIntent")(input))
def address_intent_handler(handler_input, json_data=all_mensas) :
    # type: (HandlerInput) -> Response
    print("In AddressIntent")
    filled_slots = handler_input.request_envelope.request.intent.slots
    slot_values = get_slot_values(filled_slots)
    print(slot_values)
    current_mensa_id = slot_values['mensa_name']['id']
    current_mensa_name = slot_values['mensa_name']['resolved']
    try:
        address = [j['address'] for j in json_data if j['id'] == int(current_mensa_id)]
        speech = "Die Adresse der {} lautet {}".format(current_mensa_name,address[0])
    except Exception as e:
        speech = ERROR_PROMPT4
        print("Intent: {}: message: {}".format(handler_input.request_envelope.request.intent.name, str(e)))
    
    return handler_input.response_builder.speak(speech).response

@sb.request_handler(can_handle_func=lambda input: is_intent_name("ListMensasIntent")(input))
def list_mensas_intent_handler(handler_input, all_mensas=all_mensas):
    # type: (HandlerInput) -> Response
    print("In ListMensasIntent")
    filled_slots = handler_input.request_envelope.request.intent.slots
    slot_values = get_slot_values(filled_slots)
    print(slot_values)
    city = slot_values['city']['resolved']
    try:
        speech = 'Es gibt die folgenden Mensas in {}:\n'.format(city)
        for diction in all_mensas:
            if diction['city'].lower() == city:
                speech += '{}, '.format(diction['name'])
        speech += '.'
    except Exception as e:
        speech = ERROR_PROMPT5
        print("Intent: {}: message: {}".format(handler_input.request_envelope.request.intent.name, str(e)))

    return handler_input.response_builder.speak(speech).response

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
    persist_attr = handler_input.attributes_manager.persistent_attributes
    print(persist_attr)
    if persist_attr:
        handler_input.attributes_manager.session_attributes = persist_attr
        session_attr = handler_input.attributes_manager.session_attributes
        session_attr['mensa_name'] = [mensa['name'] for mensa in all_mensas if int(persist_attr['mensa_id']) == mensa['id']][0]
        print('Previous Mensa:', session_attr['mensa_name'])
        reprompt = 'Möchtest du wieder den Tagesplan für {} hören? '.format(session_attr['mensa_name'])
        speech = WELCOME_PROMPT + reprompt
        return handler_input.response_builder.speak(speech).ask(reprompt).response
    speech = WELCOME_PROMPT + HELP_PROMPT + random_phrase([SAMPLES1, SAMPLES2, SAMPLES3])
    return handler_input.response_builder.speak(speech).ask(REPROMPT).response

## AMAZON.YesIntent
@sb.request_handler(can_handle_func=lambda input: is_intent_name("AMAZON.YesIntent")(input))
def yes_intent_handler(handler_input):
    # type: (HandlerInput) -> Response
    print("In YesIntentHandler")
    session_attr = handler_input.attributes_manager.session_attributes
    print(session_attr)

    if not session_attr:
        speech = "Du musst zuerst eine Mensa auswählen! " + random_phrase([SAMPLES1, SAMPLES2, SAMPLES3])
        return handler_input.response_builder.speak(speech).ask(speech).response
    
    # current date should be today => TODO: maybe tomorrow? maybe asking the user again?
    current_date = datetime.now().strftime("%Y-%m-%d")
    print(current_date)
    try:
        speech, question = list_dishes(session_attr, current_date)
        print(speech, question)
    except Exception as e:
        speech = ERROR_PROMPT1.format(current_date, session_attr['mensa_name'])
        question = REPROMPT
        print("Intent: {}: message: {}".format(handler_input.request_envelope.request.intent.name, str(e)))
    return handler_input.response_builder.speak(speech).ask(question).response

## AMAZON.NoIntent
@sb.request_handler(can_handle_func=lambda input: is_intent_name("AMAZON.NoIntent")(input))
def no_intent_handler(handler_input):
    # type: (HandlerInput) -> Response
    print("In NoIntentHandler")
    speech = 'Okay, was möchtest du tun? ' + random_phrase([SAMPLES1, SAMPLES2, SAMPLES3])
    handler_input.response_builder.speak(speech).ask(REPROMPT)
    return handler_input.response_builder.response

## AMAZON.FallbackIntent
@sb.request_handler(can_handle_func=lambda input: is_intent_name("AMAZON.FallbackIntent")(input))
def fallback_intent_handler(handler_input):
    # type: (HandlerInput) -> Response
    print("In FallbackIntentHandler")
    speech = SAD_PROMPT + REPROMPT + random_phrase([SAMPLES1, SAMPLES2, SAMPLES3])
    handler_input.response_builder.speak(speech).ask(REPROMPT)
    return handler_input.response_builder.response

## AMAZON.HelpIntent
@sb.request_handler(can_handle_func=lambda input: is_intent_name("AMAZON.HelpIntent")(input))
def help_intent_handler(handler_input):
    # type: (HandlerInput) -> Response
    print("In HelpIntentHandler")
    speech = "Dies ist Mensa-Auskunft. "+ HELP_PROMPT + random_phrase([SAMPLES1, SAMPLES2, SAMPLES3])
    handler_input.response_builder.speak(speech).ask(REPROMPT)
    return handler_input.response_builder.response

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

## Exception Handler
@sb.exception_handler(can_handle_func=lambda i, e: True)
def all_exception_handler(handler_input, exception):
    # type: (HandlerInput, Exception) -> Response
    logger.error(exception, exc_info=True)
    return handler_input.response_builder.speak(ERROR_PROMPT).ask(REPROMPT).response

## Unhandled handler
@sb.request_handler(can_handle_func=lambda input: True)
def unhandled_intent_handler(handler_input):
    # type: (HandlerInput) -> Response
    return handler_input.response_builder.speak(ERROR_PROMPT).ask(REPROMPT).response

lambda_handler = sb.lambda_handler()

# --- flask
skill_adapter = SkillAdapter(skill=sb.create(), skill_id='TEST', app=app)

@app.route("/", methods=['POST'])
def invoke_skill():
    return skill_adapter.dispatch_request()

if __name__ == '__main__':
    app.run(debug=True)
