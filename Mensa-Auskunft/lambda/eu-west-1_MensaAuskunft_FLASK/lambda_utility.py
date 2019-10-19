import random, requests, six
from ask_sdk_model.slu.entityresolution import StatusCode

################################################
# Utility functions ############################
################################################

def create_mensa_url(mensa_id, date):
    return 'https://openmensa.org/api/v2/canteens/{}/days/{}/meals'.format(mensa_id, date)

def random_phrase(str_list):
    """Return random element from list."""
    # type: List[str] -> str
    return random.choice(str_list)

def http_get(url, **kwargs):
    response = requests.get(url, **kwargs)
    if response.status_code < 200 or response.status_code >= 300:
        response.raise_for_status()
    if response.status_code == 204:
        raise ValueError('Response is empty.')
    return response.json()

def http_get_iterate(url):
    results = []
    response = requests.get(url)
    if response.status_code < 200 or response.status_code >= 300:
        response.raise_for_status()
    data = response.json()

    results = results + data

    for i in range(2, int(response.headers['X-Total-Pages']) + 1):
        next_url = url + "?page={}".format(i)
        response = requests.get(next_url)
        if response.status_code < 200 or response.status_code >= 300:
            response.raise_for_status()
        data = response.json()
        results = results + data

    return results


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
        print(str(e))
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
            print(e)
            slot_values[name] = {
                "synonym": slot_item.value,
                    "resolved": slot_item.value,
                        "id": None,
                        "is_validated": False,
                }
    return slot_values



def list_dishes(session_attr, current_date, ingredients={'first' : None, 'second' : None}):
    print("In ListDishes-Function")

    question = 'Kann ich sonst noch helfen? '
    # create API link
    try:
        mensa_url = create_mensa_url(mensa_id=session_attr['mensa_id'], date=current_date)
        # request mensa plan from API
        response_dishes = http_get(mensa_url)
    # No dishes found for requested date or API is down 
    except Exception as e:
        speech = "Sorry, für den ausgewählten Tag {} gibt es leider keinen Essensplan für {}. ".format(current_date, session_attr['mensa_name'])
        print("Intent: {}: message: {}".format('ListDishes-Funktion', str(e)))
        return speech+question, question
    dish_speech = ''
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
        question = 'Möchtest du Details zu einem dieser Gerichte erfahren? \
                    Sag zum Beispiel: \
                    Details. \
                    oder: Wie viel kostet Gericht Nummer 2 für Studenten. '
        speech = 'Es gibt {} {} Gerichte {} zur Auswahl: {}. {}'.format(len(session_attr['all_dishes']),
                                                                        ingredients_pre,
                                                                        ingredients_post,
                                                                        dish_speech,
                                                                        question)

    # no dishes found, e.g. there is no dish containing the requested ingredients
    else:
        
        if ingredients_post or ingredients_pre:
            speech = 'Leider gibt es keine passenden {} Gerichte {}.'.format(ingredients_pre,
                                                                             ingredients_post)
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
