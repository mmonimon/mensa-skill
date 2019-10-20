# Dokumentation des Skills "Mensa-Auskunft"
*Monique Noss*  
*Olha Zolotarenko*  
*Maria Lomaeva*  
*Bogdan Kostić*

## 1. Zusammenfassung
## 2. Projektziele, Anforderungsdefinition
### 2.1 Anwendungsbereich und Zielgruppe
Bei einem Mensa-Skill, dessen Hauptaufgabe es ist, über den Essensplan einer Mensa zu informieren, sind vor allem Studierende, aber auch Dozierende die Zielgruppe. Dessen Informationsbedürfnis ist es einerseits eine grobe Übersicht über das Angebot zu erhalten, andererseits aber auch nach bestimmten Zutaten gefilterte Ergebnisse zu erhalten, falls Allergien oder besondere Ernährungsweisen vorliegen (z.B. Veganismus). Auch der Preis eines bestimmten Gerichtes könnte für eine finale Auswahl entscheidend sein, da das Budget eines Studiernden selten großzügig ausfällt. Diese und weitere verschiedene Funktionen wurden eingebaut, um die in der OpenMensa API angebotenen Daten ausgiebig zu nutzen. Dazu gehören auch die folgenden Lokationsfunktionen:

- Adresse von Mensen
- Koordinaten, um die nächste Mensa zu finden
- Mensen nach Stadt finden

Neben den oben genannten Funktionen, die durch selbsterstellte Intents des Skills umgesetzt wurden, bietet Amazon den Skill-Entwicklern an, dynamische, auf den Benutzer zugeschnittene Funktionen einzubauen. Ein Beispiel hierfür sind die "Persist Attributes" (= "bleibende Attribute"). Persist Attributes dienen dazu, bestimmte Daten in einer Session zu speichern, damit sie in der nächsten wieder abgerufen werden können. So müsste ein Benutzer nicht bei jedem Launch mit erwähnen, für welche Mensa ein Essensplan ausgegeben werden muss. Während die Implementierung und Einbettung über AWS DynamoDB einfach vorgenommen werden kann, könnten diese beim Entwickler Kosten verursachen, weshalb wir in diesem Skill auf die Benutzung dieser Attribute verzichtet haben. Auch könnten User Accounts angelegt werden, um persönliche Vorlieben des Users speichern zu können.

Eine weitere mögliche Verbesserung haben wir während der zweiten Projektphase, also nach der ersten Vorstellung der Projekte, umsetzen können. Es handelt sich hierbei um Syntaktisches Parsing der Gerichte, um nur Kopf der "Gerichtsphrase" auszugeben und somit die Antworten des Skills zu kürzen, um den Nutzer nicht mit Informationen zu überhäufen. Aus demselben Grund werden nun immer nur vier Gerichte in einem Prompt vorgelesen. Möchte der Nutzer weitere Gerichte erfahren, kann einfach "weiter" gescrollt werden. Mit eine Intent für Details können dagegen Details zu einem Gericht erfragt werden.

Für uns war es wichtig, die gesammte Breite der API zu nutzen, um dem Nutzer so viele Funktionen zu bieten wie möglich. Nichtsdestotrotz findet die In-App-Kommunikation schnell ein Ende, wenn der Benutzer ein mögliches Ziel erreicht hat oder ein Fehler aufgetreten ist. Der Skill kann dann in einem One-Shot erneut gelaunched werden.

### 2.2 Szenarien und Beispieldialoge

Im nachfolgenden Absatz werden Beispieldialoge für jeden Intent aufgelistet, die Skillerfolge und -misserfolge darstellen sollen, um die Funktionalität des Skills zu verdeutlichen. Diese werden jeweils anhand von spezifischen Szenarien veranschaulicht und erklärt.

#### 2.2.1 Beispieldialoge: Essensplan und Preise erfahren
Die am häufigsten genutzte Funktion eines Mensa-Skills wird voraussichtlich das Abfragen des Essensplans für einen bestimmten Tag in der eigenen Mensa. Hierbei kann der Nutzer Zutaten inkludieren, um die Auswahl von Anfang an auszuschließen. Wenn eine Auswahl getroffen wurde, wird der Benutzer gefragt, ob er Details oder den Preis eines der Gerichte erfahren möchte. Der Benutzer kann an dieser Stelle auch verneinen, dann wird der Skill geschlossen.

##### Szenario 1: Benutzer möchte den Essensplan für eine bestimmte Mensa, für einen bestimmten Tag erfragen.
Wann? Jederzeit, wann immer der User in der Mensa essen möchte.
###### Situation 1.1: Morgen ist ein Werktag.

> U: Alexa, öffne Mensaauskunft.  
> A: Willkommen bei der Mensaauskunft! Wenn du Hilfe bei der Bedienung brauchst, \
            sag bitte HILFE. Was möchtest du wissen?  
U: Was gibt es morgen in der Mensa?
A: In welcher Mensa möchtest du essen?
U: Mensa Golm.
A: Es gibt 5  Gerichte  zur Auswahl: 1. Eintopf aus Kichererbsen, Linsen, Gemüse,Kartoffeln, 2. Eintopf aus Kichererbsen, Linsen, Gemüse,Kartoffeln, 3. Gulasch und 4. Hähnchenbrust „Piccata Milanese“. Möchtest du mehr Gerichte hören oder Details? 
U: Mehr!
A: 5. Griechisches Kartoffelgericht. Möchtest du Details zu einem dieser Gerichte erfahren? \
                Sag zum Beispiel: \
                Details. \
                oder: Wie viel kostet Gericht Nummer 2 für Studenten.
U: Wie viel kostet Gericht Nummer 2 für Studenten?
> A: Das Gericht Eintopf aus Kichererbsen, Linsen, Gemüse,Kartoffeln und Rindfleisch kostet 1,6 Euro für Studenten. 
---- SKILL SCHLIEßT SICH ----

###### Situation 1.2: Morgen ist Wochenende oder Feiertag.

> U: Alexa, frag Mensaauskunft, was gibt es morgen in der Mensa Golm?
> A: Sorry, für den ausgewählten Tag 2019-10-20 gibt es leider keinen Essensplan für mensa golm.
---- SKILL SCHLIEßT SICH ----

###### Situation 1.3: Die Mensa wurde nicht richtig verstanden (ASR Error) oder ist nicht im Katalog.

> U: Alexa, frag Mensaauskunft, was gibt es morgen in der Mensa Golm?
> A: Sorry, Essenspläne für mensa golum habe ich leider nicht im Angebot.

###### Situation 1.4 Der Benutzer sucht nach Gerichten mit einer bestimmten Zutat.

__Dialog 1.4.1__

> U: Alexa, frag Mensaauskunft nach veganen Gerichten. 
> A: Für wann?
U: Morgen.
A: In welcher Mensa möchtest du essen?
U: Mensa Golm.
A: Es gibt 2 Vegan Gerichte zur Auswahl: 1. Vegane Knusperkroketten und 2. Glasnudel-Bowl. Möchtest du Details zu einem dieser Gerichte erfahren? Sag zum Beispiel: Details. oder: Wie viel kostet Gericht Nummer 2 für Studenten.
U: Stopp.
> A: Guten Hunger!
---- SKILL SCHLIEßT SICH ----

__Dialog 1.4.2__

> U: Alexa, frag Mensaauskunft nach Gerichten mit Sellerie. 
> A: Für wann?
U: Morgen.
A: In welcher Mensa möchtest du essen?
U: Mensa Golm.
A: Leider gibt es keine passenden  Gerichte mit sellerie. Kann ich sonst noch helfen? 
U: Nein.
> A: Okay, tschüss!
---- SKILL SCHLIEßT SICH ----

#### 2.2.2 Beispieldialoge: Die nächste Mensa finden
Ein wenig komplexer ist die Funktionalität, eine Mensa in der Nähe des Standortes des Benutzers zu finden. Aus dem Intent können daher daher unterschiedliche Reaktionen hervorgehen, je nach Status der Standortfreigabe für das benutzte Gerät und den Skill selbst.

##### Szenario 2: Benutzer möchte eine Mensa in seiner Nähe finden und befindet sich im Ortsteil Golm in Potsdam.
Wann? Höchstwahrscheinlich nur ein mal, wenn der User wissen möchte, welche Mensa die nächste in der Umgebung ist.
###### Situation 2.1: Der User hat den Gerätestandort nicht freigegeben.

> U: Alexa, frag Mensaauskunft, wo die nächste Mensa ist.
> A: Um die nächste Mensa zu finden, benötige ich Deinen Standort. Bitte öffne die Alexa-App, um deinen Standort mit mir zu teilen. 
---- SKILL SCHLIEßT SICH ----

###### Situation 2.2: Der User hat den Gerätestandort freigegeben.

> U: Alexa, frag Mensaauskunft, wo die nächste Mensa ist.
> A: Die nächste Mensa ist Mensa Golm in Karl-Liebknecht-Str. 24/25, 14476 Potsdam OT Golm.
---- SKILL SCHLIEßT SICH ----

#### 2.2.3 Beispieldialoge: Die Adresse einer Mensa erfahren
Die Adresse der Mensa kann auch erneut erfragt werden oder auch nach Adressen anderer Mensen gesucht werden.

##### Szenario 3: Benutzer möchte die Adresse einer Mensa erfahren.
###### Situation 3.1: Die Adresse der Mensa kann gefunden werden, sie ist also im Katalog vorhanden.
> U: Alexa, Frag Mensaauskunft nach der Adresse der Mensa Golm. 
> A: Die Adresse der mensa golm lautet Karl-Liebknecht-Str. 24/25, 14476 Potsdam OT Golm
---- SKILL SCHLIEßT SICH ----

###### Situation 3.2: Die Adresse der Mensa kann nicht gefunden werden, sie ist also nicht im Katalog vorhanden. Auch möglich, dass ASR falsch verstanden hat.
> U: Alexa, Frag Mensaauskunft nach der Adresse der Mensa Golm. 
> A: Die Adresse der angefragten Mensa mensa ball um konnte leider nicht gefunden werden. 

##### Szenario 4: Benutzer möchte erfahren, welche Mensen es in einer bestimmten Stadt gibt.
##### Situation 4.1: Der Nutzer fragt nach Mensen in einer deutschen Stadt, zum Beispiel Potsdam.
> U: Alexa, Frag Mensaauskunft, welche Mensas gibt es in Potsdam? 
> A: Es gibt die folgenden Mensas in potsdam: Mensa Am Neuen Palais, Mensa Kiepenheuerallee, Mensa Golm, Mensa Griebnitzsee, Bistro Tasty Studio Babelsberg, Ulf's Café (HPI Cafeteria), Erfrischungshalle.
---- SKILL SCHLIEßT SICH ----

##### Situation 4.2: Der Nutzer fragt nach Mensen in einer Stadt, die nicht in Deutschland ist, zum Beispiel Tokyo.
> U: Alexa, Frag Mensaauskunft, welche Mensas gibt es in Tokyo? 
> A: Leider keine Mensas in Tokyo gefunden. Du kannst eine andere Stadt in Deutschland auswählen. 
---- SKILL SCHLIEßT SICH ----

##### Szenario 5: Benutzer möchte erfahren, welche Mensen es in einer bestimmten deutschen Stadt gibt.
##### Situation 5.1: Der Nutzer fragt nach Mensen in einer deutschen Stadt, zum Beispiel Potsdam.
> U: Alexa, Frag Mensaauskunft, welche Mensas gibt es in Potsdam? 
> A: Es gibt die folgenden Mensas in potsdam: Mensa Am Neuen Palais, Mensa Kiepenheuerallee, Mensa Golm, Mensa Griebnitzsee, Bistro Tasty Studio Babelsberg, Ulf's Café (HPI Cafeteria), Erfrischungshalle.
---- SKILL SCHLIEßT SICH ----

##### Situation 5.2: Der Nutzer fragt nach Mensen in einer deutschen Stadt, zum Beispiel Potsdam.
> U: Alexa, Frag Mensaauskunft, welche Mensas gibt es in Tokyo? 
> A: Leider keine Mensas in Tokyo gefunden. Du kannst eine andere Stadt in Deutschland auswählen. 
---- SKILL SCHLIEßT SICH ----

## 3. Projektorganisation
- TeilnehmerInnen, Aufgabenverteilung
- Planungsdokumente, Milestones (und ihre Dynamik über die Entwicklungsphase: Wie wurde der Plan angepasst über die Entwicklungszeit?)
## 4. Entwurf des Systems, Dokumentation
- Entwicklungsumgebung (verwendete Software, etc.)
- Dokumentation Intents
## 5. Projektabschluss, Evaluation
- Versuchsanordnung: VPs, Material, Methode (Fragebogen, Erfolg)
- Auswertung
- Ausblick, Verbesserungsmöglichkeiten
