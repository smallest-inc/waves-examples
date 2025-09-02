#
# Copyright (c) 2024–2025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

"""Smallest STT service implementation."""
# src/pipecat/services/smallest/stt.py

import asyncio
import json
import urllib.parse
import warnings
from enum import Enum
from typing import Any, AsyncGenerator, Dict, List, Optional, Union
from urllib.parse import urlencode

from loguru import logger
from pydantic import BaseModel, Field, ValidationError

from pipecat.frames.frames import (
    CancelFrame,
    EndFrame,
    ErrorFrame,
    Frame,
    InterimTranscriptionFrame,
    StartFrame,
    TranscriptionFrame,
    UserStartedSpeakingFrame,
    UserStoppedSpeakingFrame,
)
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from pipecat.services.stt_service import STTService
from pipecat.transcriptions.language import Language
from pipecat.utils.time import time_now_iso8601
from pipecat.utils.tracing.service_decorators import traced_stt

try:
    import websockets
except ModuleNotFoundError as e:
    logger.error(f"Exception: {e}")
    logger.error("In order to use Smallest, you need to `pip install pipecat-ai[smallest]`.")
    raise Exception(f"Missing module: {e}")


class AudioChannel(int, Enum):
    MONO = 1
    STEREO = 2


class AudioEncoding(str, Enum):
    LINEAR16 = "linear16"
    FLAC = "flac"
    MULAW = "mulaw"
    OPUS = "opus"


class SensitiveData(str, Enum):
    PCI = "pci"
    SSN = "ssn"
    NUMBERS = "numbers"


class EventType(str, Enum):
    TRANSCRIPTION = "transcription"
    ERROR = "error"


class TranscriptionResponse(BaseModel):
    type: EventType = EventType.TRANSCRIPTION
    text: str
    isEndOfTurn: bool
    isFinal: bool


class ErrorResponse(BaseModel):
    type: EventType = EventType.ERROR
    message: str
    error: Union[List[str], str]


def language_to_smallest_language(language: Language) -> Optional[str]:
    """Convert a Language enum to Smallest's language code format."""
    BASE_LANGUAGES = {
        Language.EN: "en",
        Language.HI: "hi",
    }

    result = BASE_LANGUAGES.get(language)

    if not result:
        lang_str = str(language.value)
        base_code = lang_str.split("-")[0].lower()
        result = base_code if base_code in BASE_LANGUAGES.values() else None

    return result


class SmallestSTTService(STTService):
    """Speech-to-Text service using Smallest's API.

    This service connects to Smallest's WebSocket API for real-time transcription
    with support for multiple languages and various processing options.
    """

    class SmallestInputParams(BaseModel):
        """Configuration parameters for the Smallest STT service."""

        audioEncoding: Optional[AudioEncoding] = Field(
            default=AudioEncoding.LINEAR16,
            description="The encoding format of the audio input.",
        )
        audioSampleRate: Optional[int] = Field(
            default=16000,
            ge=8000,
            le=48000,
            description="The sample rate of the audio in Hz.",
        )
        audioLanguage: Optional[Language] = Field(
            default=Language.EN,
            description="The language of the audio input.",
        )
        audioChannels: Optional[AudioChannel] = Field(
            default=AudioChannel.MONO,
            description="The number of audio channels.",
        )
        addPunctuation: Optional[bool] = Field(
            default=None, description="Whether to add punctuation to the transcript."
        )
        speechEndThreshold: Optional[int] = Field(
            default=None,
            ge=10,
            le=60000,
            description="The duration in milliseconds to determine the end of a speech segment.",
        )
        emitVoiceActivity: Optional[bool] = Field(
            default=None, description="Whether to emit voice activity detection events."
        )
        redactSensitiveData: Optional[List[SensitiveData]] = Field(
            default=None,
            description="Types of sensitive data to redact from the transcript.",
        )
        speechEndpointing: Optional[Union[int]] = Field(
            default=None,
            description="Controls speech endpointing behavior.",
        )

    def __init__(
        self,
        *,
        api_key: str,
        url: Optional[str] = "wss://waves-api.smallest.ai/api/v1/asr",
        sample_rate: Optional[int] = None,
        params: SmallestInputParams = SmallestInputParams(),
        **kwargs,
    ):
        """Initialize the Smallest STT service."""
        super().__init__(sample_rate=sample_rate, **kwargs)

        self._api_key = api_key
        self._url = url
        self._params = params
        self._websocket = None
        self._receive_task = None
        self._settings = {**params.model_dump()}
        self._ping_interval = kwargs.get("ping_interval", None)
        self._ping_timeout = kwargs.get("ping_timeout", None)

    @property
    def language(self) -> Language:
        return self._settings["audioLanguage"]

    def can_generate_metrics(self) -> bool:
        return True

    async def set_language(self, language: Language):
        """Set the language for the STT service."""
        logger.info(f"{self.name} Switching STT language to: [{language}]")
        self._settings["audioLanguage"] = language
        await self._disconnect()
        await self._connect()

    async def set_model(self, model: str):
        await super().set_model(model)
        logger.info(f"{self.name} Switching STT model to: [{model}]")
        self._settings["model"] = model
        await self._disconnect()
        await self._connect()

    async def start(self, frame: StartFrame):
        """Initialize the connection when the service starts."""
        await super().start(frame)
        self._settings["audioSampleRate"] = self.sample_rate
        await self._connect()

    async def stop(self, frame: EndFrame):
        await super().stop(frame)
        await self._disconnect()

    async def cancel(self, frame: CancelFrame):
        await super().cancel(frame)
        await self._disconnect()

    async def run_stt(self, audio: bytes) -> AsyncGenerator[Frame, None]:
        """Send audio data to the websocket. Follows Deepgram pattern."""
        if self._websocket and not self._websocket.closed:
            try:
                await self._websocket.send(audio)
            except websockets.exceptions.ConnectionClosed as e:
                logger.warning(f"{self.name} Connection closed while sending: {e}")
                await self._disconnect()
            except Exception as e:
                logger.error(f"{self.name} Error sending audio: {e}")
                await self._disconnect()
        yield None

    def _build_websocket_url(self) -> str:
        def to_query_params(params: dict) -> str:
            """Convert the parameters to a query string, ignoring None values and converting enums to their values."""
            params = {
                k: (v.value if isinstance(v, Enum) else v)
                for k, v in params.items()
                if v is not None
            }
            return urlencode(params)

        """Build the WebSocket URL with query parameters."""
        query_string = to_query_params(self._settings)
        url = f"{self._url}?{query_string}"
        return url

    async def _connect(self):
        """Connect to Smallest websocket."""
        extra_headers = {
            "Authorization": f"Bearer {self._api_key}",
        }

        try:
            self._websocket = await websockets.connect(
                self._build_websocket_url(),
                extra_headers=extra_headers,
                ping_interval=self._ping_interval,
                ping_timeout=self._ping_timeout,
                compression=None,
            )

            self._receive_task = self.create_task(self._receive_task_handler())
            logger.info(f"{self.name} Successfully connected to Smallest")

        except Exception as e:
            logger.error(f"{self.name} Failed to connect: {e}")
            raise

    async def _disconnect(self):
        """Disconnect from Smallest."""
        logger.debug(f"{self.name} Disconnecting from Smallest")

        if self._receive_task:
            await self.cancel_task(self._receive_task)
            self._receive_task = None

        try:
            if self._websocket and not self._websocket.closed:
                await self._websocket.close()
        except Exception as e:
            logger.warning(f"{self.name} Error closing WebSocket connection: {e}")
        finally:
            self._websocket = None

    async def start_metrics(self):
        """Start metrics tracking."""
        await self.start_ttfb_metrics()
        await self.start_processing_metrics()

    async def _on_error(self, error_msg: str):
        """Handle connection errors."""
        logger.warning(f"{self.name} connection error, will retry: {error_msg}")
        await self.stop_all_metrics()
        try:
            await self._connect()
        except Exception as e:
            logger.error(f"{self.name} Failed to reconnect after error: {e}")

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        """Process frames. Follow Deepgram pattern."""
        await super().process_frame(frame, direction)

        if isinstance(frame, UserStartedSpeakingFrame):
            await self.start_metrics()
        elif isinstance(frame, UserStoppedSpeakingFrame):
            await self._finalize_audio()

    @traced_stt
    async def _handle_transcription(
        self, transcript: str, is_final: bool, language: Optional[Language] = None
    ):
        """Handle a transcription result with tracing."""
        pass

    async def _receive_task_handler(self):
        """Handle incoming websocket messages. This is the key method!"""
        try:
            while True:
                try:
                    message = await self._websocket.recv()
                    try:
                        data = json.loads(message)
                        event_type = data.get("type", None)
                        if event_type == EventType.TRANSCRIPTION.value:
                            transcription_response = TranscriptionResponse.model_validate_json(
                                message
                            )

                            if len(transcription_response.text) > 0:
                                await self.stop_ttfb_metrics()
                                if transcription_response.isFinal:
                                    await self.push_frame(
                                        TranscriptionFrame(
                                            transcription_response.text,
                                            "",
                                            time_now_iso8601(),
                                            self.language,
                                        )
                                    )
                                    await self._handle_transcription(
                                        transcription_response.text,
                                        transcription_response.isFinal,
                                        self.language,
                                    )
                                    await self.stop_processing_metrics()
                                else:
                                    await self.push_frame(
                                        InterimTranscriptionFrame(
                                            transcription_response.text,
                                            "",
                                            time_now_iso8601(),
                                            self.language,
                                        )
                                    )
                        elif event_type == EventType.ERROR.value:
                            error_response = ErrorResponse.model_validate_json(message)
                            logger.error(f"{self.name} Error response: {error_response}")

                        else:
                            logger.warning(f"{self.name} Unknown event type: {event_type}")

                    except json.JSONDecodeError as e:
                        logger.warning(f"{self.name} Failed to parse JSON message: {e}")
                        continue

                    except ValidationError as e:
                        logger.warning(f"{self.name} Failed to validate message: {e}")
                        continue

                    except Exception as e:
                        logger.error(f"{self.name} Error processing message: {e}")
                        continue

                except websockets.exceptions.ConnectionClosed as e:
                    logger.info(f"{self.name} WebSocket connection closed: {e.code} - {e.reason}")
                    break

                except Exception as e:
                    logger.error(f"{self.name} Error in receive loop: {e}")
                    break
        except Exception as e:
            logger.error(f"{self.name} Fatal error in receive task handler: {e}")

    async def _finalize_audio(self):
        """Finalize the audio stream."""
        if self._websocket and not self._websocket.closed:
            try:
                finalize_msg = json.dumps({"type": "Finalize"})
                await self._websocket.send(finalize_msg)
                logger.debug(f"{self.name} Sent finalize message")
            except Exception as e:
                logger.error(f"{self.name} Error sending finalize message: {e}")