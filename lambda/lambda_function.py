# -*- coding: utf-8 -*-

import logging
import ask_sdk_core.utils as ask_utils

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_model.interfaces.alexa.presentation.apl import RenderDocumentDirective
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model.interfaces.audioplayer import (
    PlayDirective, PlayBehavior, AudioItem, Stream, AudioItemMetadata,
    StopDirective, ClearQueueDirective, ClearBehavior
)
from utils import create_presigned_url
from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        speak_output = "Welcome to Midnight Radio. Enjoy the music."
        
        # Play the audio with metadata including images
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
                        subtitle="Enjoy the music",
                        art={"sources": [{"url": create_presigned_url("Media/Cinelax.jpg")}]},
                        background_image={"sources": [{"url": create_presigned_url("Media/Sunset.jpg")}]}
                    )
                )
            )
        )

        return handler_input.response_builder.speak(speak_output).response

class PauseIntentHandler(AbstractRequestHandler):
    """Handler for Pause Intent."""
    
    def can_handle(self, handler_input):
        return ( ask_utils.is_intent_name("AMAZON.PauseIntent")(handler_input)
                    or ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))
                    
    def handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        audio_player_state = handler_input.request_envelope.context.audio_player
        offset = audio_player_state.offset_in_milliseconds if audio_player_state else 0
        
        # Store the offset in session attributes
        session_attr["offset"] = offset

        speak_output = "Pausing Midnight Radio."

        handler_input.response_builder.add_directive(StopDirective())

        return handler_input.response_builder.speak(speak_output).response

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

class AboutIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("aboutIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "This is Midnight Radio"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class ResumeIntentHandler(AbstractRequestHandler):
    """Handler for Resume Intent."""
    
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.ResumeIntent")(handler_input)

    def handle(self, handler_input):
        # Retrieve the stored offset from session attributes
        session_attr = handler_input.attributes_manager.session_attributes
        offset = session_attr.get("offset", 0)  # Default to 0 if no offset is stored

        speak_output = "Resuming Midnight Radio."

        handler_input.response_builder.add_directive(
            PlayDirective(
                play_behavior=PlayBehavior.REPLACE_ALL,
                audio_item=AudioItem(
                    stream=Stream(
                        token="midnight_radio",
                        url=create_presigned_url("Media/Cinelax.mp3"),
                        offset_in_milliseconds=offset  # Resume from the stored offset
                    ),
                    metadata=AudioItemMetadata(
                        title="Midnight Radio",
                        subtitle="Enjoy the music",
                        art={"sources": [{"url": create_presigned_url("Media/Cinelax.jpg")}]},
                        background_image={"sources": [{"url": create_presigned_url("Media/Sunset.jpg")}]}
                    )
                )
            )
        )

        return handler_input.response_builder.speak(speak_output).response

class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intents."""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input)

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
    """Handler for Start Over Intent."""

    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.StartOverIntent")(handler_input)

    def handle(self, handler_input):
        speak_output = "Restarting Midnight Radio from the beginning."

        # Reset offset to 0 and play from the start
        handler_input.response_builder.add_directive(
            PlayDirective(
                play_behavior=PlayBehavior.REPLACE_ALL,
                audio_item=AudioItem(
                    stream=Stream(
                        token="midnight_radio",
                        url=create_presigned_url("Media/Cinelax.mp3"),
                        offset_in_milliseconds=0  # Always start from the beginning
                    ),
                    metadata=AudioItemMetadata(
                        title="Midnight Radio",
                        subtitle="Enjoy the music",
                        art={"sources": [{"url": create_presigned_url("Media/Cinelax.jpg")}]},
                        background_image={"sources": [{"url": create_presigned_url("Media/Sunset.jpg")}]}
                    )
                )
            )
        )

        return handler_input.response_builder.speak(speak_output).response

class UnhandledFeaturesIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (ask_utils.is_intent_name("AMAZON.LoopOnIntent")(handler_input)
                or ask_utils.is_intent_name("AMAZON.RepeatIntent")(handler_input)
                or ask_utils.is_intent_name("AMAZON.PreviousIntent")(handler_input)
                or ask_utils.is_intent_name("AMAZON.NextIntent")(handler_input)
                or ask_utils.is_intent_name("AMAZON.ShuffleOnIntent")(handler_input)
                or ask_utils.is_intent_name("AMAZON.ShuffleOffIntent")(handler_input)
                or ask_utils.is_intent_name("AMAZON.LoopOffIntent")(handler_input)
                )

    def handle(self, handler_input):
        speak_output = "This feature is not supported."

        return handler_input.response_builder.speak(speak_output).response

class FallbackIntentHandler(AbstractRequestHandler):
    """Single handler for Fallback Intent."""
    
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        speech = "Hmm, I'm not sure. You can say play music or help. What would you like to do?"
        reprompt = "I didn't catch that. What can I help you with?"

        return handler_input.response_builder.speak(speech).ask(reprompt).response

class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors."""
    
    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return handler_input.response_builder.speak(speak_output).ask(speak_output).response

# Skill Builder
sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(UnhandledFeaturesIntentHandler())
sb.add_request_handler(PauseIntentHandler())
sb.add_request_handler(ResumeIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(StartOverIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(AboutIntentHandler())
sb.add_request_handler(FallbackIntentHandler())

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
