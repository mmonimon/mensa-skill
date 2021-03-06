from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput
import lambda_utility as utility
from prompts import REPROMPTS
from ask_sdk_model.dialog import DelegateDirective
from ask_sdk_core.dispatch_components import AbstractRequestHandler

############## DetailsIntent ########################

# DetailsIntent unvalid because user has not made asked for dishes yet
class DetailsIntentInvalidHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        return ((is_intent_name("DetailsIntent")(handler_input)) or 
                (is_intent_name("DetailsDishIntent")(handler_input))) and ('all_dishes' not in session_attr)

    def handle(self, handler_input):
        print("In DetailsIntent – unvalid")
        # request = handler_input.request_envelope.request
        return handler_input.response_builder.speak("Du musst zuerst Gerichte erfragen,\
                    bevor du Details über ein Gericht erfahren kannst. ").ask(utility.random_phrase(REPROMPTS)).response

# DetailsIntent valid, but dish number is missing -> ask user to provide it
class DetailsIntentValidIncompleteHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        request = handler_input.request_envelope.request
        return ((is_intent_name("DetailsIntent")(handler_input)) or 
                (is_intent_name("DetailsDishIntent")(handler_input))) and \
            ('all_dishes' in session_attr) and \
            (str(request.dialog_state) == 'DialogState.STARTED')

    def handle(self, handler_input):
        print("In DetailsIntent – valid & uncompleted")
        # current_intent = handler_input.request_envelope.request.intent
        return handler_input.response_builder.add_directive(DelegateDirective()).response

# DetailsIntent valid
class DetailsIntentValidCompletedHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        request = handler_input.request_envelope.request
        return (is_intent_name("DetailsIntent")(handler_input)) and \
            ('all_dishes' in session_attr) and \
            (str(request.dialog_state) in ['DialogState.COMPLETED', 'DialogState.IN_PROGRESS'])

    def handle(self, handler_input):
        """Der Intent listet die Details zu einem bestimmten Gericht auf.

        (Alle verfügbaren Informationen der OpenMensa API.)

        Dazu gehören:
            - Der vollständige Titel des Gerichts
            - Die Preise für Studierende, Angestellte und Andere
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
        print("In DetailsIntent – valid & completed")
        # extract slot values
        filled_slots = handler_input.request_envelope.request.intent.slots
        # get previous response from session attributes 
        session_attr = handler_input.attributes_manager.session_attributes
        user_groups_de = ['Angestellte', 'Andere', 'Schüler', 'Studierende']
        
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
            user_groups = sorted(list(dish_prices.keys()))
            speech = "Du hast das Gericht {} ausgewählt. ".format(dish_name)
            speech += "Es kostet "
            # read all prices for each available user group
            for i in range(len(user_groups)):
                price = dish_prices[user_groups[i]]
                if price == None:
                    continue
                speech += utility.build_price_speech(price, user_groups_de[i])
            speech += '. Es gehört zur Kategorie: {} und enthält '.format(dish_cat)
            for i in range(len(dish_notes)):
                if i == len(dish_notes)-2:
                    speech += dish_notes[i] + ' und '
                else:
                    speech += dish_notes[i] + ', '
            speech += '. '


        # dish cannot be found any more: user may have used a higher number
        except Exception as e:
            speech = "Nanu! Das Gericht Nummer {} konnte nicht wiedergefunden werden. Bitte versuche es erneut. ".format(current_number)
            print("Intent: {}: message: {}".format(handler_input.request_envelope.request.intent.name, str(e)))
            return handler_input.response_builder.speak(speech).ask(utility.random_phrase(REPROMPTS)).response
        return handler_input.response_builder.speak(speech).set_should_end_session(True).response

############## DetailsDishIntent ########################

class DetailsDishIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        request = handler_input.request_envelope.request
        return (is_intent_name("DetailsDishIntent")(handler_input)) and \
            ('all_dishes' in session_attr) and \
            (str(request.dialog_state) in ['DialogState.COMPLETED', 'DialogState.IN_PROGRESS'])

    def handle(self, handler_input):
        print("In DetailsDishIntent – valid & completed")
        session_attr = handler_input.attributes_manager.session_attributes

        # extract slot values
        filled_slots = handler_input.request_envelope.request.intent.slots
        slot_values = utility.get_slot_values(filled_slots)
        # print(filled_slots)
        current_dish = slot_values['dish']['resolved']
        current_dish_idx = slot_values['dish']['id']
        user_groups_de = ['Angestellte', 'Andere', 'Schüler', 'Studierende']
        print(slot_values)
        # try to get dish by index
        try:
            dish_name = session_attr['all_dishes'][int(current_dish_idx)]['name']
            dish_prices = session_attr['all_dishes'][int(current_dish_idx)]['prices']
            dish_cat = session_attr['all_dishes'][int(current_dish_idx)]['category']
            dish_notes = session_attr['all_dishes'][int(current_dish_idx)]['notes']
            user_groups = sorted(list(dish_prices.keys()))
            speech = "Du hast das Gericht {} ausgewählt. ".format(dish_name)
            speech += "Es kostet "
            # read all prices for each available user group
            for i in range(len(user_groups)):
                price = dish_prices[user_groups[i]]
                if price == None:
                    continue
                speech += utility.build_price_speech(price, user_groups_de[i])
            speech += '. Es gehört zur Kategorie: {} und enthält '.format(dish_cat)
            for i in range(len(dish_notes)):
                if i == len(dish_notes)-2:
                    speech += dish_notes[i] + ' und '
                else:
                    speech += dish_notes[i] + ', '
            speech += '. '

        # dish cannot be found any more
        except Exception as e:
            speech = "Nanu! Das Gericht {} konnte nicht wiedergefunden werden. Bitte versuche es erneut. ".format(current_dish)
            print("Intent: {}: message: {}".format(handler_input.request_envelope.request.intent.name, str(e)))
            return handler_input.response_builder.speak(speech).ask(utility.random_phrase(REPROMPTS)).response
        return handler_input.response_builder.speak(speech).response