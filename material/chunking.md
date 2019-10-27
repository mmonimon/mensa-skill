# Chunking

## Vorüberlegungen

—> **Erster Vorschlag**: Split von Gerichtsnamen an "," und/oder "oder" (Problem - Kommata gehören zu dem vorherigen String --> Punktuation muss entfernt werden + außerden weil der Skill wegen mancher Punktuation abstürzt)
—> **Zweiter Vorschlag**: Split nach allerersten Präposition
—> **Finale Entscheidung**: Split nach allen Präpositionen, ähnliche Gerichte suchen und den unterschiedlichen Teil nach der ersten gelichen Phrase mit 'mit' anhängen

## Allgemeine Beobachtungen:

- Chunking mit SpaCy funktioniert zwar ok, aber es gibt keine Einheitliche Form von den Phrasen, wo man allgemein entscheiden kann, dass jetzt genau die NP passt und extrahiert werden soll (z.B. bei "Fusilli Tricolore alla Saporita mit Seelachswürfel in Weißwein-Sahnesoße").
- immer ein Tradeoff zwischen Kürze und ausreichnendem Informationsgrad!
- manche Phrasen sind schon kurz genung (—> "Schweinegeschnetzeltes mit Pasta")
- bei "3erlei Nudeln besser" split nach ‘oder’, weil sonst die drei Gerichte völlig gleich sind (es gibt mehrere solche Beispliele, daher find_difference Funktion benötigt)
- Kategorie ist wichtig! (Mensas in Berlin unterscheiden z.B. Vorspeisen und Beilagen etc.)

## Implementierung

Chunking wurde wie in oben in dem finalen Entscheidung schon kurz geschrieben mit dem Split nach den gängigsten Präpositionen gemacht:

['\n', 'aus', '\naus', 'dazu', '\ndazu', 'oder', '\noder', 'mit', '\nmit', 'im', '\nim', 'auf', '\nauf', 'in', '\nin', 'an', '\nan']

Die Hauptfunktion **make_chunking** bekommt die Liste von allen an dem gefragten Tag un an der gewählten Mensa vorhandenen Gerichten. Zuerst werden alle Gerichte "vorgechunkt" mit der Funktion **chunking**. Diese orientiert sich nach den obengenannten Präpositionen und schneidet den Namen des Gerichts nach der ersten vorgekommenen Präposition und lässt die esten Nomen nachdem. Es wird außerdem überprüft, ob es vielleicht nach dem ersten Nomen auch noch ein Nomen ist wie in dem Beispiel mit "Linseneintopf mit Wiener Würstchen", damit der Name des Gerichts immer noch verständlich ist. Die Funktion **find_difference** überprüft dabei, ob es ähnliiche Gerichte in der Liste gibt. Diese werden dann so verkürzt, dass nach der Präposition "mit" der unterschiedliche Teil dieser Gerichte steht. Anschließend wird die fertig abgearbeitete Liste mit den Grichten zurückgegeben.


## Beispiele:
**Potsdam - Golm**  
1. 
* Gemüseeintopf mit Tofu
* Rindergeschnetzeltes mit Pasta und Salate
* Rinderbraten mit Pasta und Salate
* Tofu in Sesam-Tempura auf Tomaten-Gemüsesugo
* Pulled Turkey im Oliven-Ciabatta
* Pulled Soja im Oliven-Ciabatta
* 3erlei Nudeln --> 3erlei Nudeln, dazu Austernpilzsauce
* 3erlei Nudeln --> 3erlei Nudeln, dazu veganes Gemüse
* 3erlei Nudeln --> 3erlei Nudeln, dazu Hähnchenpfanne mit Oliven und Tomaten
2. 
* Italienisches Nudelgericht mit Tofu
* Italienisches Nudelgericht mit Salami
* Gebratene Sojastreifen in Honig-Senf-Sauce mit Mischgemüse und Reis
* Hähnchengeschnetzeltes mit Mischgemüse und Nudelreis
* Lammhacksteak mit Joghurtdip und buntem Nudelreis
* Älpler Maggerone mit Appenzeller Käse überbacken
* Schweinegeschnetzeltes mit Pasta
* 3erlei Nudeln
* 3erlei Nudeln
* 3erlei Nudeln

**Magdeburg:**
* Crunchy Chicken-Burger mit Kartoffelspalten und Sour Cream
* Geflügel-Frühlingsrolle mit süß-saurer Soße
* 2 gekochte Eier in Senfsoße mit Kartoffelpüree
* Pastabuffet: Fusilli Tricolore alla Saporita mit Seelachswürfel in Weißwein-Sahnesoße

**Berlin:**  
1.
* Italienischer Pastasalat mit getrockneten Tomaten
* Doppelte Salatschale
* Große Salatschale
* Kleine Salatschale
* Allgäuer Käsecremesuppe
* Gemüsebrühe mit Wildreis
* Würzige Sojastreifen mit Schluppen
* Badische Schupfnudeln mit Spinatrahm und Tomatenwürfeln
* Italienische Spaghetti mit Tomaten-Basilikum-Ragout
* Buchweizenpfanne mit geräuchertem Tofu und frischem Gemüse
* Ein Matjes - Doppelfilet Hausfrauen Art mit Äpfeln und Zwiebeln
* Schweinegulasch nach ungarischer Art
* Ein Germknödel mit Kirschfüllung
* Prinzessbohnen mit Zwiebelwürfeln
* Gartengemüse
* Brokkoli
* Kartoffeln
* Muschelnudeln
* Erdnussreis
* Hausfrauen Sauce mit Äpfeln und Zwiebeln
* Obstschälchen
* Haselnussjoghurt
* Quark mit Schwarzen Johannisbeeren
* Schokoladenpudding
2.
* Antipasti
* Italienischer Pastasalat mit getrockneten Tomaten
* Doppelte Salatschale
* Große Salatschale
* Kleine Salatschale
* Allgäuer Käsecremesuppe
* Gemüsebrühe mit Wildreis
* Badische Schupfnudeln mit Spinatrahm und Tomatenwürfeln
* Pulled Pork Burger mit Barbecuesauce
* Italienische Spaghetti mit Tomaten-Basilikum-Ragout
* Buchweizenpfanne mit geräuchertem Tofu und frischem Gemüse
* Ein Matjes - Doppelfilet Hausfrauen Art mit Äpfeln und Zwiebeln
* Schweinegulasch nach ungarischer Art
* Buntes Gemüsefrikassee mit Geflügel und Reis
* Gartengemüse
* Bratkartoffeln
* Brokkoli
* Kartoffeln
* Muschelnudeln
* Erdnussreis
* Quark mit Schwarzen Johannisbeeren
* Haselnussjoghurt
* Schokoladenpudding

## Verbesserungsmöglichkeiten
Es gibt einige Bespiele bei manchen Mensen wie z.B. bei der Mensa in Heidelberg "Tagessuppe\nHähnchengeschnetzeltes\nCurry-Sahnesauce\nReis\nSalat der Saison\n", wo man zusätzliche Methoden verwenden muss, um die Gerichtsphrase zu teilen. 

## Code

```python

def chunking(meal):
    """Hilfsfunktion wendet naive Chunking auf die Gerichte an,
    die keine ähnliche Gerichte in der globale Liste haben.

    :param meal: Name des Gerichts auf den Chunking angewendet wird.
    :type meal: str
    :return: Gibt den abgekurzten String zurück.
    :rtype: str
    """
    dish = meal.split(' ')
    preposition_list = ['\n', 'aus', '\naus', 'dazu', '\ndazu', 'oder', '\noder', 'mit', '\nmit', 'im', '\nim', 'auf', '\nauf', 'in', '\nin', 'an', '\nan']
    first_prep_found = next((word for word in dish if word in preposition_list), None)

    if first_prep_found != None:
        ind = dish.index(first_prep_found)
        first_noun_ind = next(i for i in range(ind, len(dish)) if dish[i][0].isupper())
        cut_dish = dish[:ind] + dish[ind:first_noun_ind + 1]
        print(cut_dish)
        if first_noun_ind != len(dish)-1 and dish[first_noun_ind][-1] != ',':
            if dish[first_noun_ind+1][0].isupper():
                cut_dish = dish[:ind] + dish[ind:first_noun_ind + 2]
    else:
        return ' '.join(dish)

    return ' '.join(cut_dish)

def find_difference(duplicates, all_dishes):
    """Hilfsfunktion für Chunking, die ähnliche Gerichte in der Liste
    mit allen Gerichten sucht und diese so verkürzt, dass nach der
    Präposition mit der unterschiedlicher Teil diser Gerichte steht

    :param duplicates: Liste ähnlicher Gerichte
    :type all_dishes: list
    :return: Gibt die Liste der ähnlichen Gerichte, wenn diese vorkommen
    :rtype: list
    """

    similar_meals = []
    similar_groups = [[phrase for phrase in all_dishes if duplicate in phrase] for duplicate in duplicates]
    for i in range(len(similar_groups)):
        pairs = itertools.combinations(similar_groups[i], 2)
        for pair in pairs:
            dish1 = pair[0].split(' ')
            dish2 = pair[1].split(' ')

            diff1, diff2 = list(set(dish1) - set(dish2)), list(set(dish2) - set(dish1))
            meal1 = duplicates[i] + ' mit ' + ' '.join(diff1)
            meal2 = duplicates[i] + ' mit ' + ' '.join(diff2)
            similar_meals.extend((meal1, meal2))

    return list(dict.fromkeys(similar_meals))


def make_chunking(all_dishes):
    """Hauptfunktion der Chunking.
    Die Länge der Namen der Gerichte in der endgültigen Liste wird durch
    parameter cutoff von overlap-Funktion kontrolliert.

    :param all_dishes: Liste aller Gerichte.
    :type all_dishes: list
    :return: Gibt die Liste mit schon geschnittenen Namen der Gerichte
    :rtype: list
    """

    chunked_dishes = []
    for dish in all_dishes:
        chunked_dishes.append(chunking(dish))

    # if naive chunking returns duplicates
    if len(set(chunked_dishes)) != len(chunked_dishes):
        dups = [(i, dish) for i, dish in enumerate(chunked_dishes) if chunked_dishes.count(dish) > 1]
        zip_dups = list(zip(*dups))
        # find the difference between those duplicates using original names
        # and add the differences to already chunked string
        similar = find_difference(list(dict.fromkeys(zip_dups[1])), all_dishes)

        # arrange the dishes according to their original index
        for i, dish in zip(zip_dups[0], similar):
            chunked_dishes[i] = dish

    if len(chunked_dishes) != len(all_dishes):
        logging.warning("Chunking has removed some dishes from the list!")

    # removing punctuation signs from each string
    final_list = [i.translate(str.maketrans(i, i, string.punctuation))
                  for i in chunked_dishes]

    return final_list


```
