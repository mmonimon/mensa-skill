from ask_sdk_core.utils import is_request_type, is_intent_name
import lambda_utility as utility
from prompts import REPROMPTS
from ask_sdk_core.dispatch_components import AbstractRequestHandler

############## AddressIntent ########################

class AddressIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AddressIntent")(handler_input)

    def handle(self, handler_input):
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
        ### DATA
        api_url_base = "https://openmensa.org/api/v2/canteens"
        all_mensas = utility.http_get_iterate(api_url_base)
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
            speech = "Die Adresse der angefragten Mensa {} konnte leider nicht gefunden werden".format(current_mensa_name)
            speech = utility.convert_acronyms(speech) + ". "
            print("Intent: {}: message: {}".format(handler_input.request_envelope.request.intent.name, str(e)))
            return handler_input.response_builder.speak(speech+utility.random_phrase(REPROMPTS)).ask(utility.random_phrase(REPROMPTS)).response
        
        return handler_input.response_builder.speak(speech).set_should_end_session(True).response