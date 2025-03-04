# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.utils import is_intent_name, get_supported_interfaces
from ask_sdk_model.interfaces.alexa.presentation.apl import RenderDocumentDirective
from ask_sdk_model.interfaces.alexa.presentation.apl import ExecuteCommandsDirective, ControlMediaCommand
from ask_sdk_model.interfaces.audioplayer import (PlayDirective, PlayBehavior, AudioItem, Stream, AudioItemMetadata,
    StopDirective, ClearQueueDirective, ClearBehavior)
from utils import create_presigned_url

from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

APL_DOCUMENT_ID = "audioplayer"

APL_DOCUMENT_TOKEN = "documentToken"

DATASOURCE = {
    "audioPlayerTemplateData": {
        "type": "object",
        "properties": {
            "audioControlType": "none",
            "audioSources": [
                create_presigned_url("Media/Cinelax.mp3")
            ],
            "backgroundImage": create_presigned_url("Media/night.jpg"),
            "coverImageSource": create_presigned_url("Media/Cinelax.jpg"),
            "headerTitle": "Midnight Radio",
            "logoUrl": create_presigned_url("Media/icon_108_A2Z.png"),
            "primaryText": "Welcome to the midnight radio",
            "secondaryText": "Enjoy the music",
            "sliderType": "determinate"
        }
    }
}

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def supports_apl(self, handler_input):
        # Checks whether APL is supported by the User's device
        supported_interfaces = get_supported_interfaces(handler_input)
        return supported_interfaces.alexa_presentation_apl is not None

    def launch_screen(self, handler_input):
        # Only add APL directive if User's device supports APL
        if self.supports_apl(handler_input):
            handler_input.response_builder.add_directive(
                RenderDocumentDirective(
                    token="documentToken",
                    document={
                        "type": "Link",
                        "src": f"doc://alexa/apl/documents/audioplayer"
                    },
                    datasources=DATASOURCE
                )
            )

    def launch_audio(self, handler_input):
        # Add AudioPlayer directive to play audio
        handler_input.response_builder.add_directive(
            PlayDirective(
                play_behavior=PlayBehavior.REPLACE_ALL,
                audio_item=AudioItem(
                    stream=Stream(
                        token="midnight_radio",
                        url=create_presigned_url("Media/Cinelax.mp3"),
                        offset_in_milliseconds=0
                    ),
                    metadata=AudioItemMetadata(
                        title="Midnight Radio",
                        subtitle="Enjoy the music"
                    )
                )
            )
        )

    def handle(self, handler_input):
        speak_output = "Welcome, to midnight radio"
        
        # Check if the device supports APL
        if self.supports_apl(handler_input):
            self.launch_screen(handler_input)
            handler_input.response_builder.add_directive(
                ExecuteCommandsDirective(
                    token="documentToken",
                    commands=[
                        {
                            "type": "SetValue",
                            "componentId": "MainPlayButton",
                            "property": "checked",
                            "value": True
                        }
                    ]
                )
            )
        else:
            # Only play audio if APL is NOT supported
            self.launch_audio(handler_input)

        return handler_input.response_builder.speak(speak_output).response

class HelloWorldIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("HelloWorldIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Hello World!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can say hello to me! How can I help?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class UnhandledFeaturesIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (is_intent_name("AMAZON.LoopOnIntent")(handler_input)
                or is_intent_name("AMAZON.NavigateHomeIntent")(handler_input)
                or is_intent_name("AMAZON.RepeatIntent")(handler_input)
                or is_intent_name("AMAZON.PreviousIntent")(handler_input)
                or is_intent_name("AMAZON.NextIntent")(handler_input)
                or is_intent_name("AMAZON.ShuffleOnIntent")(handler_input)
                or is_intent_name("AMAZON.ShuffleOffIntent")(handler_input)
                or is_intent_name("AMAZON.LoopOffIntent")(handler_input)
                )
    
    def handle(self, handler_input):
        speak_output = "This feature is not supported."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )
    
class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intents."""
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.CancelIntent")(handler_input)

    def handle(self, handler_input):
        return (
            handler_input.response_builder
                .add_directive(ClearQueueDirective(clear_behavior=ClearBehavior.CLEAR_ALL))
                .add_directive(StopDirective())
                .speak("Goodbye!")
                .set_should_end_session(True)
                .response
        )

class PauseIntentHandler(AbstractRequestHandler):
    """Handler for Pause Intent."""
    
    def can_handle(self, handler_input):
        return (ask_utils.is_intent_name("AMAZON.PauseIntent")(handler_input) 
                or ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        speak_output = "Pausing Midnight Radio."

        session_attr = handler_input.attributes_manager.session_attributes
        audio_player_state = handler_input.request_envelope.context.audio_player
        offset = audio_player_state.offset_in_milliseconds if audio_player_state else 0

        # Store the offset in session attributes
        session_attr["offset"] = offset

        response_builder = handler_input.response_builder

        # Check if APL is supported
        if get_supported_interfaces(handler_input).alexa_presentation_apl is not None:
            response_builder.add_directive(
                ExecuteCommandsDirective(
                    token="documentToken",
                    commands=[
                        ControlMediaCommand(component_id="videoPlayer", command="pause"),
                        {
                            "type": "SetValue",
                            "componentId": "MainPlayButton",
                            "property": "checked",
                            "value": False
                        }
                    ]
                )
            )
        else:
            # If APL is not supported, stop audio playback
            response_builder.add_directive(StopDirective())

        return response_builder.speak(speak_output).response

class ResumeIntentHandler(AbstractRequestHandler):
    """Handler for Resume Intent."""
    
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.ResumeIntent")(handler_input)

    def handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        offset = session_attr.get("offset", 0)  # Default to 0 if no offset is stored

        speak_output = "Resuming Midnight Radio."

        response_builder = handler_input.response_builder

        if get_supported_interfaces(handler_input).alexa_presentation_apl is not None:
            response_builder.add_directive(
                ExecuteCommandsDirective(
                    token="documentToken",
                    commands=[
                        ControlMediaCommand(component_id="videoPlayer", command="play"),
                        {
                            "type": "SetValue",
                            "componentId": "MainPlayButton",
                            "property": "checked",
                            "value": True
                        }
                    ]
                )
            )
        else:
            response_builder.add_directive(
                PlayDirective(
                    play_behavior=PlayBehavior.REPLACE_ALL,
                    audio_item=AudioItem(
                        stream=Stream(
                            token="midnight_radio",
                            url=create_presigned_url("Media/Cinelax.mp3"),
                            offset_in_milliseconds=offset
                        ),
                        metadata=AudioItemMetadata(
                            title="Midnight Radio",
                            subtitle="Enjoy the music"
                        )
                    )
                )
            )

        return response_builder.speak(speak_output).response

class StartOverIntentHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.StartOverIntent")(handler_input)

    def supports_apl(self, handler_input):
        # Checks whether APL is supported by the User's device
        supported_interfaces = get_supported_interfaces(handler_input)
        return supported_interfaces.alexa_presentation_apl is not None

    def launch_screen(self, handler_input):
        # Only add APL directive if User's device supports APL
        if self.supports_apl(handler_input):
            handler_input.response_builder.add_directive(
                RenderDocumentDirective(
                    token="documentToken",
                    document={
                        "type": "Link",
                        "src": f"doc://alexa/apl/documents/audioplayer"
                    },
                    datasources=DATASOURCE
                )
            )

    def launch_audio(self, handler_input):
        # Add AudioPlayer directive to play audio
        handler_input.response_builder.add_directive(
            PlayDirective(
                play_behavior=PlayBehavior.REPLACE_ALL,
                audio_item=AudioItem(
                    stream=Stream(
                        token="midnight_radio",
                        url=create_presigned_url("Media/Cinelax.mp3"),
                        offset_in_milliseconds=0
                    ),
                    metadata=AudioItemMetadata(
                        title="Midnight Radio",
                        subtitle="Enjoy the music"
                    )
                )
            )
        )

    def handle(self, handler_input):
        speak_output = "Welcome, to midnight radio"
        
        # Check if the device supports APL
        if self.supports_apl(handler_input):
            self.launch_screen(handler_input)
            handler_input.response_builder.add_directive(
                ExecuteCommandsDirective(
                    token="documentToken",
                    commands=[
                        {
                            "type": "SetValue",
                            "componentId": "MainPlayButton",
                            "property": "checked",
                            "value": True
                        }
                    ]
                )
            )
        else:
            # Only play audio if APL is NOT supported
            self.launch_audio(handler_input)

        return handler_input.response_builder.speak(speak_output).response

class FallbackIntentHandler(AbstractRequestHandler):
    """Single handler for Fallback Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")
        speech = "Hmm, I'm not sure. You can say Hello or Help. What would you like to do?"
        reprompt = "I didn't catch that. What can I help you with?"

        return handler_input.response_builder.speak(speech).ask(reprompt).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(UnhandledFeaturesIntentHandler())
sb.add_request_handler(PauseIntentHandler())
sb.add_request_handler(ResumeIntentHandler())
sb.add_request_handler(HelloWorldIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(StartOverIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()