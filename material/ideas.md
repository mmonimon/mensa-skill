### Hausaufgabe 6/7: Design des Mensa-Skills

##### Überlegen Sie schon einmal, wie Sie einen Mensa-Potsdam-Skill aufsetzen würden. Was sollte er können?
Der Skill müsste:
- die verschiedenen täglichen Gerichte und deren Zutaten kennen (aktuelle Auskunft) und den Plan für die ganze Woche kennen
- eine Preisauskunft geben können
- nach Ernährungsweise suchen können (vegetarisch/vegan/mit Fleisch/egal)
- nach Zutaten suchen können wegen Allergien ("suche ein gericht ohne nüsse/milch...")

##### Welche Intents ergibt das? Wie sähen Beispieldialoge aus?

__Slots:__ <br> 
foot_type: vegetarisches, veganes, mit Fleisch<br>
ingredient: nüsse, milch, ...<br>
day_of_week: heute, am Donnerstag, übermorgen,...<br>

__Intents:__
- ListDishes<br>
"Was gibt's {day_of_week} in der Mensa?"
- FindDishesByName<br>
"wann gibt es {dish_name}?"
- FindDishesByFoodType<br>
"Gibt es ein {foot_type} Gericht?"
- FindDishesByIngredient<br>
"Gibt es ein Gericht ohne {ingredient}?"
- GetDishPrice<br>
"Wie viel kostet {dish_name}?"<br>
dish_name: die vegetarische Spaghetti Bolognese, der Fisch, ...
- GetDishDetails<br>
"Erzähl mir mehr über {dish_name}"<br>
"Ist {dish_name} {foot_type}?"<br>
"Gibt es {ingredient} in {dish_name}?"

__Beispieldialog:__<br>
a: willkommen beim mensa potsdam skill. was kann ich für dich tun?<br>
u: was gibt's heute in der mensa?<br>
a: es gibt spaghetti bolognese und fisch. über welches gericht möchtest du mehr wissen? <br>
u: wie viel kostet der fisch?<br>
a: der fisch kostet 3,50 euro. kann ich noch etwas für dich tun?<br>
u: ist die spaghetti bolognese vegetarisch?<br>
a: die spaghetti bolognese sind mit fleisch. was kann ich noch für dich tun?<br>
u: wann gibt es die vegetarische bolognese? <br>
a: die vegetarische bolognese gibt es wieder am donnerstag. gibt es noch etwas?<br>
u: nein danke<br>
a: bye!<br>

#### Aufgabe nach Sitzung 7: Design des Mensa-Skills
###### Aufgabe 1
Lesen Sie den Alexa Design Guide gründlich durch.
###### Aufgabe 2
- Versuchen Sie, für Ihren geplanten Mensaauskunftsskill die Fragen aus dem Guide zu beantworten. (Z.B. “Was ist der Zweck des Skills?”, “Warum wollen Nutzer ihn verwenden?”)
1. What’s the goal or purpose of your skill?
* Informationen über Mensaessen geben
2. How will customers invoke your skill?
* One-Shot: frage mensa uni potsdam nach dem tagesmenü
* Modal: öffne mensa uni potsdam
3. What can a customer do with your skill?
* Informationen über das aktuelle Tagesmenü der Mensa, den Wochenplaan oder über ein bestimmtes Gericht einholen
* nach bestimmten Gerichten suchen und/oder nach Zutaten suchen (z.B. bei Allergien)
4. What kinds of information do you need to collect from customers to personalize the experience?
* welche Option ausgewählt wird (Tagesplan, Wochenplan, Gerichtinfos (zb. Zutaten, vegan/vegetarisch, Preis)
* Je nach Option:
    * Tag
    * Gerichtname
    * Zutaten (Wenn nach einem Gericht gesucht werden soll)
    * Vegan/vegetarisch
    * evtl. Preisrange


#### Sample scripts
##### Mensa Uni Potsdam – optimal (happy) path
USER

Alexa, öffne Mensa Uni Potsdam

ALEXA

Willkommen beim Mensaskill der Unipotsdam! Ich kann dir die aktuelle Karte für den \<heutiges Datum\> vorlesen, Preise für ein gesuchtes Gericht mitteilen oder den Wochenplan vorlesen. Was möchtest du tun?

USER

Was gibt es heute in der Mensa?

ALEXA

Heute gibt es Spaghetti Bolognese, Fisch mit Kartoffelbrei und Hühnersuppe. Worüber möchtest du mehr erfahren?

USER

Ist die Bolognese vegetarisch?

ALEXA

Leider nicht. Es gibt immer am Dienstag und Donnerstag vegetarische Bolognese. Kann ich noch etwas für dich tun?

USER

Das ist alles, danke.

ALEXA 

Okay, bis zum nächsten Mal!

##### Mensa Uni Potsdam – help
(The customer might ask for help in the middle of using the skill.)

USER

Das verstehe ich nicht.

ALEXA

Ich kann dir die aktuelle Karte für den \<heutiges Datum\> vorlesen, Preise für ein gesuchtes Gericht mitteilen oder den Wochenplan vorlesen. Was möchtest du tun?

USER

Oh, ich würde gern den Wochenplan hören.

ALEXA

Okay, am Montag gibt es ..., am Dienstag gibt es ... (usw.)
Möchtest du mehr über ein bestimmtes Gericht wissen? Ich kann dir den Preis und die Zutaten nennen.