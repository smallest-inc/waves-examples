import asyncio
import signal

from pydantic_settings import BaseSettings, SettingsConfigDict

from vocode.helpers import create_streaming_microphone_input_and_speaker_output
from vocode.logging import configure_pretty_logging
from vocode.streaming.agent.chat_gpt_agent import ChatGPTAgent
from vocode.streaming.models.agent import ChatGPTAgentConfig
from vocode.streaming.models.message import BaseMessage
from vocode.streaming.models.synthesizer import WavesSynthesizerConfig
from vocode.streaming.models.transcriber import (
    DeepgramTranscriberConfig,
    PunctuationEndpointingConfig,
)
from vocode.streaming.streaming_conversation import StreamingConversation
from vocode.streaming.synthesizer.custom_waves_lightning_synthesizer import WavesSynthesizer
from vocode.streaming.transcriber.deepgram_transcriber import DeepgramTranscriber

configure_pretty_logging()


class Settings(BaseSettings):
    """
    Settings for the streaming conversation quickstart.
    These parameters can be configured with environment variables.
    """

    openai_api_key: str = "YOUR OPEN AI API KEY HERE"
    waves_api_key: str = "YOUR WAVES API TOKEN HERE"
    deepgram_api_key: str = "YOUR DEEPGRAM API KEY HERE"

    # This means a .env file can be used to overload these settings
    # ex: "OPENAI_API_KEY=my_key" will set openai_api_key over the default above
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()


async def main():
    (
        microphone_input,
        speaker_output,
    ) = create_streaming_microphone_input_and_speaker_output(
        use_default_devices=False,
    )

    conversation = StreamingConversation(
        output_device=speaker_output,
        transcriber=DeepgramTranscriber(
            DeepgramTranscriberConfig.from_input_device(
                microphone_input,
                endpointing_config=PunctuationEndpointingConfig(),
                api_key=settings.deepgram_api_key,
            ),
        ),
        agent=ChatGPTAgent(
            ChatGPTAgentConfig(
                openai_api_key=settings.openai_api_key,
                model_name="gpt-3.5-turbo-1106",
                initial_message=BaseMessage(text="Hello, Kya chal rha hai?"),
                prompt_preamble="""You are a AI friend that gossips with the user about actors and models. 
                                    Do not give any emojis in output. 
                                    Always reply in same language as that of user.
                                    Always restrict your reply to maximum 2 sentences.""",
            )
        ),
        synthesizer=WavesSynthesizer(
            WavesSynthesizerConfig.from_output_device(
                speaker_output,
                api_token=settings.waves_api_key,
                voice_id="raj",
                language="hi",
                speed=1.2,
                remove_extra_silence=False,
                transliterate=True,
                sample_rate=16000
            ))
    )
    await conversation.start()
    print("Conversation started, press Ctrl+C to end")
    signal.signal(signal.SIGINT, lambda _0, _1: asyncio.create_task(conversation.terminate()))
    while conversation.is_active():
        chunk = await microphone_input.get_audio()
        conversation.receive_audio(chunk)


if __name__ == "__main__":
    asyncio.run(main())
