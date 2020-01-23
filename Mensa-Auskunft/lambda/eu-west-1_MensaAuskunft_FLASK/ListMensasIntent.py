from ask_sdk_core.utils import is_request_type, is_intent_name
import lambda_utility as utility
from prompts import REPROMPTS
from ask_sdk_core.dispatch_components import AbstractRequestHandler

############## ListMensasIntent ########################

class ListMensasIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("ListMensasIntent")(handler_input)
    def handle(self, handler_input):
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
        api_url_base = "https://openmensa.org/api/v2/canteens"
        all_mensas = utility.http_get_iterate(api_url_base)
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
                    session_attr['last_idx_mensas'] += 4
                    question = "Möchtest du mehr Mensen hören? Sag: Weiter!"
                    return handler_input.response_builder.speak(speech+question).ask(question).response

        # no mensas found
        speech = "Leider keine Mensen in {} gefunden. Du kannst eine andere Stadt in Deutschland wählen. ".format(city)
        return handler_input.response_builder.speak(speech+utility.random_phrase(REPROMPTS)).ask(utility.random_phrase(REPROMPTS)).response
