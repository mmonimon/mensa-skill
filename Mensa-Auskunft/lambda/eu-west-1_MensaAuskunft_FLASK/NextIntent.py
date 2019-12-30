from ask_sdk_core.utils import is_request_type, is_intent_name
import lambda_utility as utility
from prompts import REPROMPTS, ERROR_PROMPT, HELP_SAMPLES
from ask_sdk_core.dispatch_components import AbstractRequestHandler

## AMAZON.NextIntent
class NextHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.NextIntent")(handler_input)
    def handle(self, handler_input):
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
        if 'next_intent_state' in session_attr:

            # dialogue state for NextIntent in ListDishes
            if session_attr['next_intent_state'] == 'ListDishes' and 'all_dishes' in session_attr:
                dishes_names = [d['name'] for d in session_attr['all_dishes']]
                chunked_dishes = utility.make_chunking(dishes_names)
                more_dish_speech, session_attr['last_idx'] = utility.build_dish_speech(chunked_dishes, session_attr['last_idx'])
                if session_attr['last_idx'] < len(chunked_dishes):
                    question = 'Möchtest du mehr Gerichte hören oder Details? '
                else:
                    question = 'Möchtest du Details zu einem dieser Gerichte erfahren? \
                                Sag zum Beispiel: Details. oder: Wie viel kostet Gericht Nummer 2 für Studierende. '
                return handler_input.response_builder.speak(more_dish_speech+question).ask(question).response
            # dialogue state for NextIntent in ListMensas
            elif session_attr['next_intent_state'] == 'ListMensas':
                more_mensa_speech, session_attr['last_idx_mensas'] = utility.build_mensa_speech(session_attr['city_mensas'], session_attr['last_idx_mensas'])
                more_mensa_speech = utility.convert_acronyms(more_mensa_speech)
                if session_attr['last_idx_mensas'] < len(session_attr['city_mensas']):
                    question = "Möchtest du mehr Mensen hören? Sage: Weiter! "
                    return handler_input.response_builder.speak(more_mensa_speech+question).ask(question).response
                else:
                    goodbye = "<say-as interpret-as=\"interjection\">zum wohl</say-as>."
                    return handler_input.response_builder.speak(more_mensa_speech+goodbye).set_should_end_session(True).response

            # undefined dialogue state
            print("Undefined Dialogue State {} in NextIntent".format(session_attr['next_intent_state']))
        speech = "Du musst zuerst eine Suche starten, bevor du weitere Gerichte oder Mensen hören kanst. "
        return handler_input.response_builder.speak(speech).ask(utility.random_phrase(REPROMPTS)).response
