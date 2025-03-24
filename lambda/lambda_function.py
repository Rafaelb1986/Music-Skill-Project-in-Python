
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

# Loads the metadata for the APL document.
APL_DOCUMENT_ID = "audioplayer"

APL_DOCUMENT_TOKEN = "audioPlayerToken"

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
            "primaryText": "Cinelax by Liborio Conti",
            "secondaryText": "Album: Relaxing Music for the senses",
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
        # Add APL directive
        handler_input.response_builder.add_directive(
            RenderDocumentDirective(
                token="audioPlayerToken",
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
                    ),
                    metadata=AudioItemMetadata(
                        title="Cinelax by Liborio Conti",
                        subtitle="Album: Relaxing Music for the senses"
                    )
                )
            )
        )

    def handle(self, handler_input):
        speak_output = "Welcome, to midnight radio"
        
        # Check if the device supports APL
        apl_supported = self.supports_apl(handler_input)
        if apl_supported:
            self.launch_screen(handler_input)
            handler_input.response_builder.add_directive(
                ExecuteCommandsDirective(
                    token="audioPlayerToken",
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

class PauseIntentHandler(AbstractRequestHandler):
    """Handler for Pause and Stop Intents."""
    
    def can_handle(self, handler_input):
        return (ask_utils.is_intent_name("AMAZON.PauseIntent")(handler_input) 
                or ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        speak_output = "Pausing Midnight Radio."

        response_builder = handler_input.response_builder

        # Check if APL is supported
        if get_supported_interfaces(handler_input).alexa_presentation_apl is not None:
            response_builder.add_directive(
                ExecuteCommandsDirective(
                    token="audioPlayerToken",
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

class ResumeStopIntentHandler(AbstractRequestHandler):
    """Handler for Resume Intent."""
    
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.ResumeIntent")(handler_input)

    def handle(self, handler_input):

        speak_output = "Resuming Midnight Radio."

        response_builder = handler_input.response_builder

        if get_supported_interfaces(handler_input).alexa_presentation_apl is not None:
            response_builder.add_directive(
                ExecuteCommandsDirective(
                    token="audioPlayerToken",
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
                        ),
                        metadata=AudioItemMetadata(
                            title="Cinelax by Liborio Conti",
                            subtitle="Album: Relaxing Music for the senses"
                        )
                    )
                )
            )

        return response_builder.speak(speak_output).response

class CancelIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel Intent."""
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

class StartOverIntentHandler(AbstractRequestHandler):
    """Handler for starting over."""
    
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.StartOverIntent")(handler_input)

    def supports_apl(self, handler_input):
        # Checks whether APL is supported by the User's device
        supported_interfaces = get_supported_interfaces(handler_input)
        return supported_interfaces.alexa_presentation_apl is not None

    def launch_screen(self, handler_input):
        # Add APL directive
        handler_input.response_builder.add_directive(
            RenderDocumentDirective(
                token="audioPlayerToken",
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
                    ),
                    metadata=AudioItemMetadata(
                        title="Midnight Radio",
                        subtitle="Album: Relaxing Music for the senses"
                    )
                )
            )
        )

    def handle(self, handler_input):
        speak_output = "Starting over Midnight Radio."
        
        # Check if the device supports APL
        apl_supported = self.supports_apl(handler_input)
        if apl_supported:
            self.launch_screen(handler_input)
            handler_input.response_builder.add_directive(
                ExecuteCommandsDirective(
                    token="audioPlayerToken",
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

class WhoIsPlayingIntent(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("whoIsPlaying")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You are listening the song Cinelax by Liborio Conti from the album Relaxing Music for the senses"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "This is midnight radio, enjoy the music. To play the music, simply say open midnight radio"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class UnhandledFeaturesIntentHandler(AbstractRequestHandler):
    """Handler for Unsupported Features."""
    def can_handle(self, handler_input):
        return (is_intent_name("AMAZON.LoopOnIntent")(handler_input)
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
        return (ask_utils.is_request_type("SessionEndedRequest")(handler_input) or
                ask_utils.is_request_type("AudioPlayer.PlaybackFinished")(handler_input))

    def handle(self, handler_input):
        # Any cleanup logic goes here.
        logger.info("Session ended or audio playback finished. Ending session.")

        response_builder = handler_input.response_builder

        # Check if the device supports APL
        if get_supported_interfaces(handler_input).alexa_presentation_apl is not None:
            response_builder.add_directive(
                ExecuteCommandsDirective(
                    token="audioPlayerToken",
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

        return response_builder.set_should_end_session(True).response

sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(PauseIntentHandler())
sb.add_request_handler(ResumeStopIntentHandler())
sb.add_request_handler(CancelIntentHandler())
sb.add_request_handler(StartOverIntentHandler())
sb.add_request_handler(WhoIsPlayingIntent())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(UnhandledFeaturesIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

lambda_handler = sb.lambda_handler()