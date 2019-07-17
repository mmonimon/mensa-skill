Monique Noss  
Olha Zolotarenko  
Maria Lomaeva  
Bogdan Kostić  
17. Juli 2019  

# Dialogmodellierung – Gruppenprojekt, Meeting 2 

## To-Dos / mögliche Verbesserungen 

* *ListDishesIntent* und *WithoutIntent* zusammenführen zu einem Intent 
    * *mit* & *ohne* als eigenen Slot 
    * dabei Möglichkeit einbauen, mehr als eine Zutat anzugeben 
    * *"Am Foodtruck gibt es ..."* einbauen 
    * Datum heute als Default-Wert für slot *date* 
    * Aufzählungsliste verkürzen! 
        * Möglichkeiten: 
            * Gerichte splitten an Präpositionen 
            * Dependenzparser 
            * Konstituentenparser 
            * NP-Chunking 
            * *Notes* verwenden -> *"Es gibt Geflügel, Vegetarisch, ..."* (finden wir nicht so gut) 
* *MoreInfoIntent* um komplettes Gericht zu erfahren 
* *IsOpenIntent* um zu erfahren, ob eine Mensa geöffnet ist 
* *ListMensasIntent* einschränken, z.B.: 
    * näheste Mensa zum eigenen Standort ausgeben 
    * nach Mensas in (der Nähe von) Bezirk/Straße/... fragen 
* mehr natürliche sample utterances 
* natürliche Pausen für bessere Intonation einfügen 
* Skill an naiven Usern testen; an DAU (dümmster anzunehmender User) denken 
* Zustandsvariablen im Backend für besseres Dialogmanagement?
* Dokumentation

## Zwischenfazit

Wir haben schon viel geschafft und unser Skill kann schon eine Menge!
Die Arbeit in unserer Gruppe funktioniert sehr gut und hat uns allen gut gefallen. 
Wenn wir die oben stehenden Punkte noch berücksichtigen, dann sollte unser Skill echt vorzeigbar sein. :-) 


