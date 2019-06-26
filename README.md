# mensa-skill
### Projektplan

1. Offene Fragen:
- invocation name?
- intents?
- slots?
- sample utterances?
- API der mensa? (bei der UP anfragen)
- arbeitsteilung?

### Install ASK CLI
```
    2  apt update
    3  apt install nodejs
    4  apt install ask-cli
    5  apt install npm
    6  npm install -g ask-cli
    8  ask init --no-browser
   10  ask api list-skills
   
   22  git clone https://github.com/mmonimon/test-repo.git
   25  cd test-repo/
   26  ask deploy
   27  ask dialog --locale=de-DE
```
### Use ngrok for testing
* `ngrok http 5000` => öffnet port
* https URL kopieren, als Endpoint in ASK einfügen als "wildcard certificate"
* lokal lambda_function.py ausführen => extra terminal fenster, da kommen dann auch die error meldungen
* in TEST section kann skill jetzt getestet werden
