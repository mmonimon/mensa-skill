# mensa-skill

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

### Links
https://developer.amazon.com/de/blogs/alexa/post/dbceb5dd-3c4d-40f1-be22-172f4050fbcb/building-conversational-alexa-skills-how-to-dynamically-elicit-slots-based-on-a-previous-answer-using-dialog-management

https://developer.amazon.com/de/docs/custom-skills/handle-requests-sent-by-alexa.html

https://developer.amazon.com/de/blogs/alexa/post/9ffdbddb-948a-4eff-8408-7e210282ed38/intent-chaining-for-alexa-skill

https://developer.amazon.com/de/blogs/alexa/post/114cec18-4a38-4cbe-8c6b-0fa6d8413f4f/build-for-context-switching-don-t-forget-important-information-when-switching-between-intents
