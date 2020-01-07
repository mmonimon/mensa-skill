from ask_sdk_core.utils import is_request_type, is_intent_name
import lambda_utility as utility
from prompts import REPROMPTS
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_model.dialog import DynamicEntitiesDirective
from ask_sdk_model.er.dynamic import UpdateBehavior, EntityListItem, Entity, EntityValueAndSynonyms

############## ListDishesIntent ########################

class ListDishesIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("ListDishesIntent")(handler_input)
    def handle(self, handler_input):
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
            return handler_input.response_builder.speak(speech+utility.random_phrase(REPROMPTS)).ask(utility.random_phrase(REPROMPTS)).response
        # create API link
        try:
            mensa_url = utility.create_mensa_url(mensa_id=session_attr['mensa_id'], date=session_attr['current_date'])
            # request mensa plan from API
            api_response = utility.http_get(mensa_url)
        # No dishes found for requested date or API is down 
        except Exception as e:
            speech = "Sorry, für den ausgewählten Tag {} gibt es leider keinen Essensplan für {}. \
                    Bitte überprüfe, ob die Mensa an diesem Tag geöffnet ist. ".format(session_attr['current_date'], session_attr['mensa_name'])
            print("Intent: {}: message: {}".format('ListDishesIntent', str(e)))
            return handler_input.response_builder.speak(speech+utility.random_phrase(REPROMPTS)).ask(utility.random_phrase(REPROMPTS)).response

        # try to find matching dishes
        session_attr['all_dishes'] = utility.find_matching_dishes(api_response, ingredients)
        # build speech for dish list
        dishes_names = [d['name'] for d in session_attr['all_dishes']]
        chunked_dishes = utility.make_chunking(dishes_names)
        dish_speech, session_attr['last_idx'] = utility.build_dish_speech(chunked_dishes, 0)
        updated_values = [Entity(id=i, name=EntityValueAndSynonyms(value=d, synonyms=d.split()
                                                            )
                        )
                for i, d in enumerate(chunked_dishes)
                ]
        print(updated_values)
        replace_entity_directive = DynamicEntitiesDirective(update_behavior=UpdateBehavior.REPLACE,
                                                            types=[EntityListItem(name="Dish", values=updated_values)])
        
        ingredients_pre, ingredients_post = utility.build_preposition_speech(ingredients)

        # dishes found: build speech with a list of dishes
        if dish_speech:
            if session_attr['last_idx'] < len(session_attr['all_dishes']):
                question = 'Möchtest du mehr Gerichte hören oder Details? '
            else: 
                question = 'Möchtest du Details zu einem dieser Gerichte erfahren? \
                            Sag zum Beispiel: Details. oder: Wie viel kostet Gericht Nummer 2 für Studierende. '

            speech = 'Es gibt {} {} Gerichte {} zur Auswahl: {}. {}'.format(len(session_attr['all_dishes']),
                                                                            ingredients_pre,
                                                                            ingredients_post,
                                                                            dish_speech,
                                                                            question)

        # no dishes found, e.g. there is no dish containing the requested ingredients
        else:
            # back up question in case it there is no dish_speech
            question = utility.random_phrase(REPROMPTS)
            if ingredients_post or ingredients_pre:
                speech = 'Leider gibt es keine passenden {} Gerichte {}. '.format(ingredients_pre,
                                                                                ingredients_post)
            else:
                speech = 'Es gibt leider keine passenden Gerichte zu deiner Anfrage. '
            speech += question
        print('Session attributes: ',session_attr)
        return handler_input.response_builder.speak(speech).ask(question).add_directive(replace_entity_directive).response

