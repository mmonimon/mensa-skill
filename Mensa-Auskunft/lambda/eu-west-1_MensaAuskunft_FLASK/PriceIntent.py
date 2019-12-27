from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput
import lambda_utility as utility
from prompts import REPROMPTS
from ask_sdk_model.dialog import DelegateDirective
from ask_sdk_core.dispatch_components import AbstractRequestHandler

############## PriceIntent ########################

# PriceIntent unvalid because user has not made asked for dishes yet
class PriceIntentInvalidHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        print(is_intent_name("PriceIntent")(handler_input) and ('all_dishes' not in session_attr))
        return is_intent_name("PriceIntent")(handler_input) and ('all_dishes' not in session_attr)

    def handle(self, handler_input):
        print("In PriceIntent – unvalid")
        # request = handler_input.request_envelope.request
        return handler_input.response_builder.speak("Du musst zuerst Gerichte erfragen,\
                    bevor du einen Preis erfahren kannst. ").ask(utility.random_phrase(REPROMPTS)).response

class PriceIntentValidIncompleteHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        request = handler_input.request_envelope.request
        return (is_intent_name("PriceIntent")(handler_input)) and \
            ('all_dishes' in session_attr) and \
            (str(request.dialog_state) == 'DialogState.STARTED')

    # PriceIntent valid, but dish number is missing -> ask user to provide it
    def handle(self, handler_input):
        print("In PriceIntent – valid & uncompleted")
        # current_intent = handler_input.request_envelope.request.intent
        return handler_input.response_builder.add_directive(DelegateDirective()).response

# PriceIntent valid
class PriceIntentValidCompletedHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        request = handler_input.request_envelope.request
        return (is_intent_name("PriceIntent")(handler_input)) and \
            ('all_dishes' in session_attr) and \
            (str(request.dialog_state) in ['DialogState.COMPLETED', 'DialogState.IN_PROGRESS'])

    def handle(self, handler_input):
        """Der Intent gibt den Preis für ein bestimmtes Gericht zurück. 
        Der Benutzer muss dabei die Nummer des Gerichts angeben und kann optional eine Zielgruppe
        (Studierende, Angestellte, Andere) definieren.

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
        print("In PriceIntent – valid & completed")

        # get previous response from session attributes 
        session_attr = handler_input.attributes_manager.session_attributes

        # define user group names
        user_groups_de = ['Angestellte', 'Andere', 'Schüler', 'Studierende']

        # extract slot values
        filled_slots = handler_input.request_envelope.request.intent.slots
        slot_values = utility.get_slot_values(filled_slots)
        print(slot_values)
        current_dish = slot_values['dish']['resolved']
        current_dish_idx = slot_values['dish']['id']
        current_usergroup_id = slot_values['user_group']['id']
        current_user = slot_values['user_group']['resolved']

        # try to get dish by index
        try:
            dish_name = session_attr['all_dishes'][int(current_dish_idx)]['name']
            dish_prices = session_attr['all_dishes'][int(current_dish_idx)]['prices']
            user_groups = sorted(list(dish_prices.keys()))
            speech = "Das Gericht {} kostet ".format(dish_name)
            # if user asked for a specific user group, only read this price
            if current_usergroup_id:
                price = dish_prices[current_usergroup_id]
                if price != None:
                    speech += utility.build_price_speech(price, current_user)
                else:
                    price = dish_prices['others']
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
            speech = "Nanu! Das Gericht Nummer {} konnte nicht wiedergefunden werden. Bitte versuche es erneut. ".format(current_dish)
            print("Intent: {}: message: {}".format(handler_input.request_envelope.request.intent.name, str(e)))
            return handler_input.response_builder.speak(speech).ask(utility.random_phrase(REPROMPTS)).response
        
        return handler_input.response_builder.speak(speech).set_should_end_session(True).response

############## PriceDishIntent ########################

class PriceDishIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        request = handler_input.request_envelope.request
        return (is_intent_name("PriceDishIntent")(handler_input)) and \
            ('all_dishes' in session_attr) and \
            (str(request.dialog_state) in ['DialogState.COMPLETED', 'DialogState.IN_PROGRESS'])

    def handle(self, handler_input):
        print("In PriceDishIntent – valid & completed")

        # type: (HandlerInput) -> Response
        print("In PriceIntent – valid & completed")

        # get previous response from session attributes 
        session_attr = handler_input.attributes_manager.session_attributes

        # define user group names
        user_groups_de = ['Angestellte', 'Andere', 'Schüler', 'Studierende']

        # extract slot values
        filled_slots = handler_input.request_envelope.request.intent.slots
        slot_values = utility.get_slot_values(filled_slots)
        print(slot_values)
        current_number = slot_values['number']['resolved']
        current_usergroup_id = slot_values['user_group']['id']
        current_user = slot_values['user_group']['resolved']

        # try to get dish by index
        try:
            dish_name = session_attr['all_dishes'][int(current_number)]['name']
            dish_prices = session_attr['all_dishes'][int(current_number)]['prices']
            user_groups = sorted(list(dish_prices.keys()))
            speech = "Das Gericht {} kostet ".format(dish_name)
            # if user asked for a specific user group, only read this price
            if current_usergroup_id:
                price = dish_prices[current_usergroup_id]
                if price != None:
                    speech += utility.build_price_speech(price, current_user)
                else:
                    price = dish_prices['others']
                    speech += utility.build_price_speech(price, current_user)
            # if not: read all prices for each available user group
            else:
                for i in range(len(user_groups)):
                    price = dish_prices[user_groups[i]]
                    if price == None:
                        continue
                    speech += utility.build_price_speech(price, user_groups_de[i])
            speech += '. '
        # dish cannot be found any more
        except Exception as e:
            speech = "Nanu! Das Gericht {} konnte nicht wiedergefunden werden. Bitte versuche es erneut. ".format(current_dish)
            print("Intent: {}: message: {}".format(handler_input.request_envelope.request.intent.name, str(e)))
            return handler_input.response_builder.speak(speech).ask(utility.random_phrase(REPROMPTS)).response
        return handler_input.response_builder.speak(speech).response