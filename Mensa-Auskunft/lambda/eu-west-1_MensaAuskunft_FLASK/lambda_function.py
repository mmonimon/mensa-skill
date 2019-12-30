# -*- coding: utf-8 -*-
import logging
from ask_sdk_core.skill_builder import SkillBuilder
import lambda_utility as utility
from prompts import ERROR_PROMPT

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

sb = SkillBuilder()

# Custom Intents

from PriceIntent import PriceIntentInvalidHandler, PriceIntentValidCompletedHandler, PriceIntentValidIncompleteHandler, PriceDishIntentHandler
from DetailsIntent import DetailsIntentInvalidHandler, DetailsIntentValidCompletedHandler, DetailsDishIntentHandler, DetailsIntentValidIncompleteHandler
from ListMensasIntent import ListMensasIntentHandler
from AddressIntent import AddressIntentHandler
from GetNearestMensa import GetNearestMensaHandler
from ListDishesIntent import ListDishesIntentHandler

sb.add_request_handler(PriceIntentInvalidHandler())
sb.add_request_handler(PriceIntentValidCompletedHandler())
sb.add_request_handler(PriceIntentValidIncompleteHandler())
sb.add_request_handler(PriceDishIntentHandler())
sb.add_request_handler(DetailsDishIntentHandler())
sb.add_request_handler(DetailsIntentInvalidHandler())
sb.add_request_handler(DetailsIntentValidCompletedHandler())
sb.add_request_handler(DetailsIntentValidIncompleteHandler())
sb.add_request_handler(ListMensasIntentHandler())
sb.add_request_handler(AddressIntentHandler())
sb.add_request_handler(GetNearestMensaHandler())
sb.add_request_handler(ListDishesIntentHandler())

# Built-In Intents

from BuiltInIntents import NoHandler, YesHandler, WelcomeHandler, StopHandler, HelpHandler, ExitHandler, UnhandledHandler
from NextIntent import NextHandler

sb.add_request_handler(NextHandler())
sb.add_request_handler(NoHandler())
sb.add_request_handler(YesHandler())
sb.add_request_handler(WelcomeHandler())
sb.add_request_handler(StopHandler())
sb.add_request_handler(HelpHandler())
sb.add_request_handler(ExitHandler())
sb.add_request_handler(UnhandledHandler())

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

# --- flask

from flask import Flask
from flask_ask_sdk.skill_adapter import SkillAdapter

app = Flask(__name__)

skill_adapter = SkillAdapter(skill=sb.create(), skill_id='TEST', app=app)

@app.route("/", methods=['POST'])
def invoke_skill():
    """
    POST Methode, die den Skill als FLASK app startet.

    :return: Startet den Skill
    :rtype: dispatch_request
    """
    return skill_adapter.dispatch_request()

if __name__ == '__main__':
    app.run(debug=True)
