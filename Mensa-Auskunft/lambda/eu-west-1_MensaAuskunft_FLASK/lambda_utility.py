import random, requests, six
from ask_sdk_model.slu.entityresolution import StatusCode
from haversine import haversine

################################################
# Utility functions ############################
################################################

def create_mensa_url(mensa_id, date):
    """Baut den String für die OpenMensa API Anfrage.

    :param mensa_id: die Mensa-ID als String
    :type mensa_id: str
    :param date: das Datum als String
    :type date: str
    :return: Gibt die Webseite der API als String zurück
    :rtype: str
    """
    return 'https://openmensa.org/api/v2/canteens/{}/days/{}/meals'.format(mensa_id, date)

def random_phrase(str_list):
    """Gibt einen zufälligen String aus einer String-Liste zurück.

    :param str_list: Liste mit Strings
    :type str_list: List[str]
    :return: Gibt einen String zurück
    :rtype: str
    """
    # type: List[str] -> str
    return random.choice(str_list)

def http_get(url, **kwargs):
    """Erfragt Daten mithilfe des requests-Moduls und fängt Error ab.

    :param url: die API url, die angefragt wird
    :type url: str
    :raises ValueError: ValueError, wenn die Response leer ist
    :raises [ErrorType]: Je nach Statuscode, den die Response enthält
    :return: Gibt eine Antwort des requests-Moduls als json zurück.
    :rtype: json
    """
    response = requests.get(url, **kwargs)
    if response.status_code < 200 or response.status_code >= 300:
        response.raise_for_status()
    if response.status_code == 204:
        raise ValueError('Response is empty.')
    return response.json()

def http_get_iterate(url):
    """Erfragt Daten mithilfe des requests-Moduls und fängt Error ab.
    Iteriert über alle Seiten einer API

    :param url: die API url, die angefragt wird
    :type url: str
    :raises [ErrorType]: Je nach Statuscode, den die Response enthält
    :return: Gibt die Antworten des requests-Moduls als json zurück.
    :rtype: json
    """
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

# chunking for shorter lists of dishes
# ',' are not cut because they belong to the previous string
def chunking(j):
    """Sucht nach Präpositionen in einem String, um ab dieser den Rest wegzuschneiden.

    :param j: Der zu schneidende String.
    :type j: str
    :return: Gibt den geschnittenen String zurück
    :rtype: str
    """
    dish = j.split(' ')
    preposition_list = ['dazu', '\ndazu', 'oder', 'und', '\nmit', 'mit']
    for prep in preposition_list:
        if prep in dish:
            dish = dish[:dish.index(prep)]
    return ' '.join(dish)

def build_mensa_speech(mensalist, start_idx):
    """Baut den String, der anschließend für den Prompt des ListMensasIntents benutzt wird.
    Die Liste ist möglicherweise sehr lang. Deshalb wird nur das Element am Startindex und drei
    weitere Elemente in den Prompt gebaut, um zu lange Antworten zu vermeiden.

    Der letzte Index wird gemerkt und zusammen mit dem String zurückgegeben.
    Dieser fungiert beim nächsten Durchlauf als Startindec, damit die Liste an derselben Stelle
    fortgesetzt wird.

    :param mensalist: Eine Liste mit Mensen als Strings
    :type mensalist: List[str]
    :param start_idx: Der Index, bei dem angefangen werden soll zu suchen.
    :type start_idx: int
    :return: Gibt den fertigen String un den letzten Index für den nächsten Durchlauf zurück.
    :rtype: str, int
    """

    mensalist_string = ''
    last_idx = start_idx + 3
    for i in range(start_idx, len(mensalist)):
        current_mensa = mensalist[i]
        if i == last_idx:
            mensalist_string += '{}. '.format(current_mensa)
            break
        if i + 1 == len(mensalist):
            mensalist_string += '{}. '.format(current_mensa)
        elif i == (len(mensalist) - 2) or i == last_idx - 1:
            mensalist_string += '{} und '.format(current_mensa)
        else:
            mensalist_string += '{}, '.format(current_mensa)
    print(mensalist_string)
    return mensalist_string, last_idx+1


def build_dish_speech(dishlist, start_idx):
    """Baut den String, der anschließend für den Prompt des ListDishesIntents benutzt wird.
    Die Liste ist möglicherweise sehr lang. Daher wird nur das Element am Startindex und 
    drei weitere Strings in den Prompt gebaut, um zu lange Antworten zu vermeiden.

    Der letzte Index wird gemerkt und zusammen mit dem String zurückgegeben. 
    Dieser fungiert beim nächsten Durchlauf als Startindex, damit die Liste an derselben Stelle fortgesetzt wird.

    :param dishlist: Eine Liste mit Gerichten als Strings
    :type dishlist: List[str]
    :param start_idx: Der Index, bei dem angefangen werden soll zu suchen.
    :type start_idx: int
    :return: Gibt den fertigen String und den letzten Index für den nächsten Durchlauf zurück
    :rtype: str, int
    """

    dishlist_string = ''
    last_idx = start_idx + 3 # TODO
    for i in range(start_idx, len(dishlist)):
        current_dish = chunking(dishlist[i]['name'])
        count = i+1
        if i == last_idx:
            dishlist_string += '{}. {}. '.format(count, current_dish)
            break
        if count == len(dishlist):
            dishlist_string += '{}. {}. '.format(count, current_dish)
        elif count == (len(dishlist) - 1) or count == last_idx:
            dishlist_string += '{}. {} und '.format(count, current_dish)
        else:
            dishlist_string += '{}. {}, '.format(count, current_dish)
    print(dishlist_string)
    return dishlist_string, last_idx+1


def build_preposition_speech(ingredients):
    """Baut einen zusätlichen String, der Zutaten enthält, um dem Nutzer mitzuteilen, wonach er gesucht hat.

    :param ingredients: Ein Dictionary mit Zutaten-Strings
    :type ingredients: dict
    :return: Gibt den fertigen String zurück
    :rtype: str
    """
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
    return ingredients_pre, ingredients_post

def build_price_speech(price, user):
    """Baut die Prompt für den Preis.

    :param price: Der Preis als String
    :type price: str
    :param user: Die Zielgruppe als String
    :type user: str
    :return: Gibt den fertigen String zurück
    :rtype: str
    """

    return '{} Euro für {}, '.format(str(price).replace('.',','), user)

def get_resolved_value(request, slot_name):
    """Die Funktion löst einen slot name mithilfe von slot resolutions auf,
    um einen \"dahinterliegenden\" Wert zu finden.

    \"Resolve the slot name from the request using resolutions.\"
    
    :param request: Die Anfrage des Intents
    :type request: IntentRequest
    :param slot_name: Name des Slots
    :type slot_name: str
    :raises AttributeError: 
    :raises KeyError:
    :raises ValueError:
    :raises IndexError:
    :raises TypeError:
    :return: Gibt entweder den resolved slot value zurück oder None
    :rtype: str, None
    """
    # type: (IntentRequest, str) -> Union[str, None]
    try:
        return (request.intent.slots[slot_name].resolutions.
                resolutions_per_authority[0].values[0].value.name)
    except (AttributeError, ValueError, KeyError, IndexError, TypeError) as e:
        print("Couldn't resolve {} for request: {}".format(slot_name, request))
        print(str(e))
        return None

def get_slot_values(filled_slots):
    """Extrahiert zusätzliche Informationen zum Slot filling, wie z.B. die ID eines slots, 
    ob der Slot in den Slot values des Interaction Models vorhanden ist und seinen resolved value.

    \"Return slot values with additional info.\"
    
    :param filled_slots: Ein Dictionary mit allen Slots
    :type filled_slots: Dict[str, Slot]
    :raises AttributeError: 
    :raises KeyError:
    :raises ValueError:
    :raises IndexError:
    :raises TypeError:
    :return: Gibt die extrahierten Values mit zusätzlichen Infos zurück
    :rtype:  Dict[str, Any]
    """
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



def find_matching_dishes(api_response, ingredients={'first' : None, 'second' : None}):
    """Filtert die aus der API-Antwort erhaltenen Gerichte nach bestimmten Zutaten.
    Hat der User keine Zutaten angebeben, sind diese "None" und es wird die komplette API-Antwort zurückgegeben.
    
    :param api_response: Die json response der OpenMensa API
    :type api_response: json
    :param ingredients: Dictionary mit Zutaten-String
    :type ingredients: Dict[str, [None, str]] (Default: {'first' : None, 'second' : None} )
    :return: Liste mit den erwünschten Gerichten
    :rtype: List[str]
    """
    print("In ListDishes-Function")
    all_dishes = []

    # create list of desired dishes
    # user did not include optional (un)desired ingredient(s) in utterance --> list all dishes
    if (not ingredients['first']) and (not ingredients['second']):
        all_dishes = api_response

    # user included at least one (un)desired ingredient in utterance
    elif ingredients['first']:
        # first_ingredient is 'fleisch'
        if ingredients['first'].lower() == 'fleisch':
            all_dishes = ingredient_fleisch(api_response, ingredients['first_prep'], None)

        else:
            # ingredient is undesired
            # sample utterance: 
            #   - "Suche Gerichte ohne {first_ingredient} ..."
            if ingredients['first_prep'] == 'ohne':
                undesired_ingredient = ingredients['first'].lower()
                # add all dishes without undesired ingredient
                all_dishes = [dish 
                            for dish in api_response 
                            if not ingredient_in_dish(undesired_ingredient, dish)]

            # ingredient is desired
            # sample utterances:
            #   - "Suche Gerichte mit {first_ingredient} ..."
            #   - "Suche {first_ingredient} Gerichte ..."
            else:
                desired_ingredient = ingredients['first'].lower()
                # add all dishes with desired ingredient
                all_dishes = [dish 
                            for dish in api_response 
                            if ingredient_in_dish(desired_ingredient, dish)]

        # user included another (un)desired ingredient in utterance
        if ingredients['second']:
            if ingredients['second'].lower() == 'fleisch':
                all_dishes = ingredient_fleisch(all_dishes,
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
                    all_dishes = [dish
                                for dish in all_dishes
                                if not ingredient_in_dish(undesired_ingredient, dish)]

                # ingredient is desired
                # sample utterances:
                #   - "Suche Gerichte mit {first_ingredient} und {second_ingredient}"
                #   - "Suche {first_ingredient} Gerichte mit {second_ingredient}"
                else:
                    desired_ingredient = ingredients['second'].lower()
                    # remove all dishes without desired ingredient
                    all_dishes = [dish
                                for dish in all_dishes
                                if ingredient_in_dish(desired_ingredient, dish)]
    return all_dishes



# returns True if a given ingredient is found in a dish (in 'notes' or in dish-string) 
def ingredient_in_dish(ingredient, dish) :
    """Checkt, ob eine bestimmte Zutat in einem Gerichte-String oder in den Notes enthalten ist.
    
    :param ingredients: Dictionary mit Zutaten-String
    :type ingredients: Dict[str, [None, str]]
    :param dish: Dictionary mit allen Daten zu einem Gericht
    :type dish: Dict[str, Any]
    :return: Gibt True zurück, wenn die Zutat gefunden wurde, sonst False
    :rtype: Boolean
    """

    # ingredient found in 'notes' ingredient is substring of 'name'
    if [note for note in dish['notes'] if (ingredient in note.lower())] or \
        ingredient in dish['name'].lower():

        return True

    # ingredient not found
    return False

# return dishes with / without meat (as this is not marked in a general way in API data)
def ingredient_fleisch(dishlist, first_prep, second_prep, is_first_ingredient=True):
    """Filtert die erhaltenen Gerichte nach veganen und vegetarischen Gerichten,
    da dies nicht aus den Daten der API ersichtlich ist.

    :param dishlist: Liste mit Gerichten
    :type dishlist: List[str]
    :param first_prep: Die erste Präposition
    :type first_prep: str
    :param second_prep: Die zweite Präposition
    :type second_prep: str
    :param is_first_ingredient: TODO Docu
    :type is_first_ingredient: Boolean (Default: True)
    :return: Liste mit Gerichten mit/ohne Fleisch
    :rtype: List[str]
    """
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

# calculates nearest mensa using haversine formula (airline distance)
def calculate_nearest_mensa(user_coordinates, mensa_list):
    """Berechnet die zum User nächstgelegene Mensa (Luftlinie)
    mithilfe der Haversine-Formel.

    :param user_coordinates: Paar mit Koordinaten des Users
    :type user_coordinates: Tuple[float]
    :param mensa_list: Liste aller Mensen
    :type mensa_list: List[dict]
    :return: Paar mit Name und Adresse der nächsten Mensa
    :rtype: Tuple[str]
    """
    nearest_mensa = None
    shortest_distance = None
    for mensa in mensa_list:
        # check if coordinates are available for current mensa
        if mensa['coordinates']:
            mensa_coordinates = (float(mensa['coordinates'][0]), float(mensa['coordinates'][1]))
        # coordinates not available -> retrieve from address
        else:
            # get coordinates of mensa using nominatim api
            address_string = mensa['address']
            nominatim_api = "https://nominatim.openstreetmap.org/search/{}?format=json&limit=1".format(address_string)
            try:
                location_data = http_get(nominatim_api)[0]
                coordinates = (float(location_data['lat']), float(location_data['lon']))
            # Nominatim API could not find address of Mensa in its database
            except IndexError:
                pass

        distance = haversine(user_coordinates, mensa_coordinates)
        if shortest_distance is None or distance < shortest_distance:
            shortest_distance = distance
            nearest_mensa = mensa

    return nearest_mensa['name'], nearest_mensa['address']