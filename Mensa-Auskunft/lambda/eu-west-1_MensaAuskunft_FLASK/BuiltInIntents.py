from ask_sdk_core.utils import is_request_type, is_intent_name
import lambda_utility as utility
from prompts import REPROMPTS, ERROR_PROMPT, HELP_SAMPLES
from ask_sdk_core.dispatch_components import AbstractRequestHandler

##################################################
# Request Handler classes ########################
##### BUILT IN INTENTS ###########################
##################################################

## AMAZON.WelcomeIntent
class WelcomeHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("LaunchRequest")(handler_input)
    def handle(self, handler_input):
        """Der Intent wird beim Öffnen des Skills durch Modal-Launchphrasing getriggert. 
        Er gibt eine Willkommensnachricht zurück.

        :param handler_input: HandlerInput
        :type handler_input: (HandlerInput) -> Response
        :return: Gibt die vollständige Skill-Antwort zurück
        :rtype: Response
        """

        # type: (HandlerInput) -> Response
        print("In LaunchRequestHandler")
        speech = "Willkommen bei der Mensaauskunft! Wenn du Hilfe bei der Bedienung brauchst, \
                sag bitte HILFE. Was möchtest du wissen? "
        return handler_input.response_builder.speak(speech).ask("Suchst du nach dem Tagesplan, \
                                                                der Adresse einer Mensa oder eine Auflistung \
                                                                aller Mensen in deiner Stadt? ").response

## AMAZON.YesIntent
class YesHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.YesIntent")(handler_input)
    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        print("In YesIntentHandler")
        return handler_input.response_builder.speak("Los geht's! Was möchtest du wissen? ").ask(utility.random_phrase(REPROMPTS)).response

## AMAZON.NoIntent
class NoHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.NoIntent")(handler_input)
    def handle(self, handler_input):
        """
        Der Intent wird ausgelöst, wenn der Benutzer eine Rückfrage des Skills verneint.
        Er gibt eine Verabschiedung zurück und beendet den Skill.

        :param handler_input: HandlerInput
        :type handler_input: (HandlerInput) -> Response
        :return: Gibt die vollständige Skill-Antwort zurück
        :rtype: Response
        """

        # type: (HandlerInput) -> Response
        print("In NoIntentHandler")
        return handler_input.response_builder.speak('Okay, tschüss!').set_should_end_session(True).response

## AMAZON.HelpIntent
class HelpHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        """
        Der Intent unterstützt den Nutzer bei der Bedienung des Skills. 
        Er informiert den Nutzer über den Umfang des Skills und gibt Beispielanfragen zurück.
        
        :param handler_input: HandlerInput
        :type handler_input: (HandlerInput) -> Response
        :return: Gibt die vollständige Skill-Antwort zurück
        :rtype: Response
        """

        # type: (HandlerInput) -> Response
        print("In HelpIntentHandler")
        speech = "Mensaauskunft kann dir dabei helfen, passende Gerichte in deiner Mensa zu finden! \
                Du kannst nach dem Tagesplan, nach Mensen in deiner Nähe, Adressen und nach einem Gericht mit Zutaten deiner Wahl suchen. \
                Sag zum Beispiel: {}.".format(utility.random_phrase(HELP_SAMPLES))
        return handler_input.response_builder.speak(speech).ask('Was möchtest du tun? ').response

## AMAZON.StopIntent
class StopHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.CancelIntent")(handler_input) or is_intent_name("AMAZON.StopIntent")(handler_input)
    def handle(self, handler_input):
        """
        Der Intent stoppt den Skill mit einer Verabschiedung.
        
        :param handler_input: HandlerInput
        :type handler_input: (HandlerInput) -> Response
        :return: Gibt die vollständige Skill-Antwort zurück
        :rtype: Response
        """

        # type: (HandlerInput) -> Response
        print("In ExitIntentHandler")
        return handler_input.response_builder.speak("Guten Hunger! ").set_should_end_session(True).response

## ExitAppIntent (schließen, verlassen...)
class ExitHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("SessionEndedRequest")(handler_input)
    def handle(self, handler_input):
        """
        Der Intent stoppt den Skill ohne Verabschiedung.
        
        :param handler_input: HandlerInput
        :type handler_input: (HandlerInput) -> Response
        :return: Gibt die response ohne Antwort zurück
        :rtype: Response
        """

        # type: (HandlerInput) -> Response
        print("In SessionEndedRequestHandler")
        print("Session ended with reason: {}".format(handler_input.request_envelope.request.reason))
        return handler_input.response_builder.set_should_end_session(True).response


## AMAZON.FallbackIntent
class FallbackHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)
    def handle(self, handler_input):
        """
        Der Intent informiert den Benutzer darüber, dass der Skill die gewünschte Funktionalität nicht besitzt
        und fragt den User, ob er eine andere Suche starten möchte.

        :param handler_input: HandlerInput
        :type handler_input: (HandlerInput) -> Response
        :return: Gibt die vollständige Skill-Antwort zurück
        :rtype: Response
        """
        # type: (HandlerInput) -> Response
        print("In FallbackIntentHandler")
        return handler_input.response_builder.speak(ERROR_PROMPT).ask(utility.random_phrase(REPROMPTS)).response


## Unhandled handler
class UnhandledHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return True
    def handle(self, handler_input):
        """
        Ein Intent für alle "Unhandled requests". Er informiert darüber, 
        dass der Skill die gewünschte Funktionalität nicht besitzt und beendet ihn.

        :param handler_input: HandlerInput
        :type handler_input: (HandlerInput) -> Response
        :return: Gibt die vollständige Skill-Antwort zurück
        :rtype: Response
        """

        # type: (HandlerInput) -> Response
        return handler_input.response_builder.speak(ERROR_PROMPT).set_should_end_session(True).response