# -*- coding: utf-8 -*-

import logging
import requests
import six
import random

from flask import Flask
from flask_ask_sdk.skill_adapter import SkillAdapter
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler, AbstractExceptionHandler,
    AbstractResponseInterceptor, AbstractRequestInterceptor)
from ask_sdk_core.utils import is_intent_name, is_request_type

from typing import Union, Dict, Any, List
from ask_sdk_model.dialog import (ElicitSlotDirective, DelegateDirective)
from ask_sdk_model import (Response, IntentRequest, DialogState, SlotConfirmationStatus, Slot)
from ask_sdk_model.slu.entityresolution import StatusCode

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
app = Flask(__name__)

# Skill Builder object
sb = SkillBuilder()


##################################################
# DATA  ##########################################
##################################################

### PROMPT constants
# TODO: geht bestimmt schöner
WELCOME_PROMPT = "Willkommen bei der Mensa-Auskunft! "
HELP_PROMPT = "Ich kann dir dabei helfen, eine Auskunft über das Essen in der Mensa zu erhalten! "
REPROMPT = "Suchst du nach dem Tagesplan, der Adresse einer Mensa oder eine Auflistung aller Mensen in deiner Stadt? "
SAD_PROMPT = "Sorry, dabei kann Mensa-Auskunft leider nicht helfen. "
ERROR_PROMPT = "Sorry, das kann Mensa-Auskunft leider nicht verstehen. Bitte versuche es erneut. "
ERROR_PROMPT1 = "Sorry, für den ausgewählten Tag {} gibt es leider keinen Essensplan für {}. "
ERROR_PROMPT2 = "Sorry, Essenspläne für {} habe ich leider nicht im Angebot. "
ERROR_PROMPT3 = "Nanu! Das Gericht Nummer {} konnte nicht wiedergefunden werden. Bitte versuche es erneut. "

### Data
# required_slots = ["mensa_name", "date"]
api_url_base = "https://openmensa.org/api/v2/canteens"
DISHES = {}
RESPONSE = []

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


#### TEST ABOVE section:
# all_mensas = requests.get(api_url_base).json() # all mensas with names, cities, addresses, ids
# print(all_mensas)
# print(http_get('https://openmensa.org/api/v2/canteens/61/days/2019-06-19/meals'))

##################################################
# Request Handler classes ########################
##### OUR OWN SKILL INTENTS ######################
##################################################
## TODO

class ListDishesIntent(AbstractRequestHandler):
    def __init__(self):
        self.dishes = {}
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("ListDishesIntent")(handler_input) and
                handler_input.request_envelope.request.dialog_state == DialogState.COMPLETED)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In ListDishesIntent")
        filled_slots = handler_input.request_envelope.request.intent.slots
        slot_values = get_slot_values(filled_slots)
        print(slot_values)
        current_mensa_id = slot_values['mensa_name']['id']
        current_date = slot_values['date']['resolved']
        optional_ingredient = slot_values['ingredient']['resolved']
        if current_mensa_id == None:
            speech = ERROR_PROMPT2.format(current_mensa_id)
            return handler_input.response_builder.speak(speech).response
        mensa_url = create_mensa_url(mensa_id=current_mensa_id, date=current_date)
        try:
            response = http_get(mensa_url)
            count = 0
            dish_speech = ''
            for dish in response:
                if optional_ingredient and optional_ingredient in dish['notes']:
                    count += 1
                    dish_speech += self.build_speech(dish, count)
                elif not optional_ingredient:
                    count += 1
                    dish_speech += self.build_speech(dish, count)
            if dish_speech:
                speech = 'Es gibt folgende Gerichte zur Auswahl: ' + dish_speech + '. '
            else: 
                speech = 'Es gibt leider keine passenden Gerichte zu deiner Anfrage. '

        except Exception as e:
            speech = ERROR_PROMPT1.format(current_date, current_mensa_id)
            logger.info("Intent: {}: message: {}".format(handler_input.request_envelope.request.intent.name, str(e)))

        return handler_input.response_builder.speak(speech).response

    def build_speech(self, dish, count):
        speech = ''
        RESPONSE.append(dish)
        DISHES[count] = dish['id']
        speech += '{}. {}, '.format(count, dish['name'])
        return speech

class PriceIntent(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("PriceIntent")(handler_input) and
                handler_input.request_envelope.request.dialog_state == DialogState.COMPLETED)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In PriceIntent")
        user_groups = ['Studenten', 'Angestellte', 'Schüler', 'Andere']
        filled_slots = handler_input.request_envelope.request.intent.slots
        slot_values = get_slot_values(filled_slots)
        current_number = slot_values['number']['resolved']
        current_user = slot_values['user_group']['resolved']
        print(slot_values)
        try:
            dish_id = DISHES[int(current_number)]
            print(DISHES)
            print(RESPONSE)
            for dish in RESPONSE:
                if dish_id == dish['id']:
                    speech = "Das Gericht {} kostet ".format(dish['name'])
                    dish_keys = list(dish['prices'].keys())
                    for i in range(len(dish_keys)):
                        price = dish['prices'][dish_keys[i]]
                        if price == None:
                            continue
                        speech += "{} Euro für {}, ".format(str(price).replace('.',','), user_groups[i])
                    speech += '.'
        except Exception as e:
            speech = ERROR_PROMPT3.format(current_number)
            logger.info("Intent: {}: message: {}".format(handler_input.request_envelope.request.intent.name, str(e)))

        return handler_input.response_builder.speak(speech).response


################################################
# Request and Response Loggers #################
################################################

class RequestLogger(AbstractRequestInterceptor):
    """Log the request envelope."""
    def process(self, handler_input):
        # type: (HandlerInput) -> None
        logger.info("Request Envelope: {}".format(
            handler_input.request_envelope))

class ResponseLogger(AbstractResponseInterceptor):
    """Log the response envelope."""
    def process(self, handler_input, response):
        # type: (HandlerInput, Response) -> None
        logger.info("Response: {}".format(response))

################################################
# Utility functions ############################
################################################

def get_resolved_value(request, slot_name):
    """Resolve the slot name from the request using resolutions."""
    # type: (IntentRequest, str) -> Union[str, None]
    try:
        return (request.intent.slots[slot_name].resolutions.
                resolutions_per_authority[0].values[0].value.name)
    except (AttributeError, ValueError, KeyError, IndexError, TypeError) as e:
        logger.info("Couldn't resolve {} for request: {}".format(slot_name, request))
        logger.info(str(e))
        return None

def get_slot_values(filled_slots):
    """Return slot values with additional info."""
    # type: (Dict[str, Slot]) -> Dict[str, Any]
    slot_values = {}
    logger.info("Filled slots: {}".format(filled_slots))

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
            logger.info("Couldn't resolve status_code for slot item: {}".format(slot_item))
            logger.info(e)
            slot_values[name] = {
                "synonym": slot_item.value,
                "resolved": slot_item.value,
                "id": None,
                "is_validated": False,
            }
    return slot_values


##################################################
# Request Handler classes ########################
##### BUILT IN INTENTS ###########################
##################################################
### NO NEED FOR MODIFICATION

## AMAZON.WelcomeIntent
# => no sample utterances, will be triggered by opening the skill without one shot 
# (no direct link to a skill specific intent)
class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for skill launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In LaunchRequestHandler")
        speech = WELCOME_PROMPT + HELP_PROMPT
        handler_input.response_builder.speak(speech).ask(REPROMPT)
        return handler_input.response_builder.response

## AMAZON.FallbackIntent
class FallbackIntentHandler(AbstractRequestHandler):
    """Handler for handling fallback intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")
        speech = SAD_PROMPT + REPROMPT
        handler_input.response_builder.speak(speech).ask(REPROMPT)
        return handler_input.response_builder.response

## AMAZON.HelpIntent
class HelpIntentHandler(AbstractRequestHandler):
    """Handler for help intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In HelpIntentHandler")
        speech = "Dies ist Mensa-Auskunft. "+ HELP_PROMPT
        handler_input.response_builder.speak(speech).ask(REPROMPT)
        return handler_input.response_builder.response

## AMAZON.StopIntent
class ExitIntentHandler(AbstractRequestHandler):
    """Single Handler for Cancel, Stop and Pause intents."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In ExitIntentHandler")
        handler_input.response_builder.speak("Bye").set_should_end_session(
            True)
        return handler_input.response_builder.response

## ExitAppIntent (schließen, verlassen...)
class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for skill session end."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In SessionEndedRequestHandler")
        logger.info("Session ended with reason: {}".format(
            handler_input.request_envelope.request.reason))
        return handler_input.response_builder.response

# Exception Handler classes
class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Catch All Exception handler.
    This handler catches all kinds of exceptions and prints
    the stack trace on AWS Cloudwatch with the request envelope."""
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)
        speech = ERROR_PROMPT
        handler_input.response_builder.speak(speech).ask(speech)
        return handler_input.response_builder.response


# Add all request handlers to the skill.
## custom intents
sb.add_request_handler(ListDishesIntent())
sb.add_request_handler(PriceIntent())

## built-in intents
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(ExitIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

# Add exception handler to the skill.
sb.add_exception_handler(CatchAllExceptionHandler())

# Add response interceptor to the skill.
sb.add_global_request_interceptor(RequestLogger())
sb.add_global_response_interceptor(ResponseLogger())

# Expose the lambda handler to register in AWS Lambda.
lambda_handler = sb.lambda_handler()

# --- flask
skill_adapter = SkillAdapter(skill=sb.create(), skill_id='TEST', app=app)


@app.route("/", methods=['POST'])
def invoke_skill():
    return skill_adapter.dispatch_request()


if __name__ == '__main__':
    app.run(debug=True)