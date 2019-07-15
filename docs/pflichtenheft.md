# Pflichtenheft
## Dialogmodellierung: Gruppenprojekt - Alexa Mensaauskunft-Skill
*Monique Noss*  
*Olha Zolotarenko*  
*Maria Lomaeva*  
*Bogdan Kostić*  

### Zielbestimmungen
Grundsätzliches Ziel des Gruppenprojektes ist es, den standortsübergreifend Alexa Mensaauskunft-Skill zu programmieren.

### Aufteilung

* Bogdan: IngredientIntent, WithoutIntent
* Olha: AddressIntent, Pflichtenheft
* Maria: ListMensasIntent, Pflichtenheft
* Moni: ListDishesIntent, PriceIntent

### Invocation Name

```sh
mensa auskunft
```

### Mögliche Erweiterungen
Als weitere mögliche Verbesserungen, die aber zur Zeit den Rahmen des Projekts sprengen, werden folgene Punkte betrachtet:

1. User Accounts, um personliche Vorlieben des Users speichern zu können. 
2. Syntaktisches Parsing der Gerichte, um nur Kopf der "Gerichtsphrase" auszugeben. 
3. Nach Gerichten in allen Standorten suchen. 

### Einsatz - Wofür benutzt man den Mensaauskunft-Skill?
Der Mensaauskunft-Skill gibt die folgenden Informationen aus: 

* welche Mensas gibt es in einer Stadt
* welche Adresse hat die Mensa
* welche Gerichte werden am bestimmten Tag serviert
* welche Preise gibt es für das ausgewählte Gericht. 

Ein Beuspieldialog wäre:

> U: Alexa, öffne Mensaauskunft.  
> A: In welcher Mensa möchtest du essen?  
U: Golm.  
A: Wann möchtest du essen?  
U: Übermorgen.   
A: Übermorgen gibt es Geflügelgulasch, … \*  
U: Alexa, welche Gerichte sind vegetarisch?  
A: Ich habe die folgenden vegetarischen Gerichte gefunden: Bami Goreng, …  
U: Alexa, wie viel kostet Bami Goreng für Studenten?  
A: Für Studenten kostet Bami Goreng 2€. Möchtest du noch etwas über ein anderes Gericht wissen?  
U: Welche Gerichte gab es denn?  
A: …  
U: …  
> A: … . Guten Appetit! 

\*Alexa kann immer unterbrochen werden

### Funktionen - Was man bei dem Mensaasukunft-Skill fragen kann?
#### Essenplan
Gibt den Essenplan von einer bestimmten Mensa, Datum oder Ingredient aus. 

Beispieläußerungen:

>"lies mir den plan für {date} vor"  
"gibt es {date} {ingredient} gerichte in der {mensa_name}"  
>"was gibt's in der mensa"  

#### Adresse der Mensa
Die Adresse einer Mensa wird vorgelesen. 

Beispieläußerungen:

>"zeige mir die adresse der {mensa_name}"  
"standort {mensa_name}"  
>"adresse {mensa_name}"  

#### Preis der Gerichte
Der Skill gibt den Preis für ein Gericht zurück.

Beispieläußerungen:

>"preis für nummer {number}"  
"wie viel kostet das {number} für {user_group}"  
>"wie teuer ist das {number} gericht"  

#### Mensas in einer Stadt
Listet die Mensas in einer genannten Stadt auf.

Beispieläußerungen:

>"welche mensas gibt es in {city}"  
"suche mensas in {city}"  
>"gibt es mensas in {city}"  

#### Gericht ohne Ingrediens
Nach dem Wunsch können nur die Gerichte ohne bestimmtes Ingrediens gesucht werden. 

Beispieläußerungen:

>"suche für {date} {synonyms_gericht} ohne {ingredient} in {mensa_name}"  
"gibt es {date} {synonyms_gericht} ohne {ingredient}"  
>"nach {synonyms_gericht} ohne {ingredient} bitte"  

#### Technisches Umfeld

<img src="mermaid-diagram-20190715215538.svg" alt="drawing" width="500" align="middle"/>

#### Tests
???
