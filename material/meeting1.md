Monique Noss  
Olha Zolotarenko  
Maria Lomaeva  
Bogdan Kostić  
20. Juni 2019  

# Dialogmodellierung – Gruppenprojekt, Meeting 1

* Invocation name: Mensaauskunft
* verschiedene Intents aufteilen
* allgemeiner Mensa-Skill, nicht nur Potsdam  
* Option ganzes Menü zu hören
* Special Features: 
    * nach Zutaten standortübergreifend suchen

* Intents:
    * ListDishesIntent (mit möglichen Keyword) 
        * Slot: Ingredient (optional)
        * Slot: DATE
        * Slot: MensaName
    * KeyWordIntent? 
    * ListDishesWithoutIntent --> intent chaining?
        * Slot: Ingredient
        * Slot: DATE
        * Slot: MensaName
    * PriceIntent --> intent chaining?
        * Slot: UserGroup (optional)
        * Slot: Dish
    * AddressIntent
        * Slot: MensaName
    * ListMensenIntent
        * Slot: CITY

* Slots:
    * MensaName (ID)
    * DATE
    * Ingredient
    * UserGroup
    * Dish
    * CITY

## Mögliche Erweiterungen:
* Accounts wären gut, sprengen aber den Rahmen
* syntaktisches Parsen der Gerichte, um nur Kopf der "Gerichtsphrase" auszugeben, sprengt auch den Rahmen  (Chunking mit spacy?)
* nach Gerichten in allen Standorten suchen

## Beispieldialog
U: Alexa, öffne Mensaauskunft.  
A: In welcher Mensa möchtest du essen?  
U: Golm.  
A: Wann möchtest du essen?  
U: Übermorgen. (wenn geschlossen, dann Exit?)  
A: Übermorgen gibt es Geflügelgulasch, …  
U: Alexa, welche Gerichte sind vegetarisch?  
A: Ich habe die folgenden vegetarischen Gerichte gefunden: Bami Goreng, …  
U: Alexa, wie viel kostet Bami Goreng für Studenten?  
A: Für Studenten kostet Bami Goreng 2€. Möchtest du noch etwas über ein anderes Gericht wissen?  
U: Welche Gerichte gab es denn?  
A: …  
U: …  
A: … . Guten Appetit!   
