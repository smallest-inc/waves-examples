import asyncio
import datetime
import json
import requests
import websockets
from concurrent.futures import ThreadPoolExecutor
from typing import AsyncGenerator
from loguru import logger

from vocode.streaming.models.audio import AudioEncoding
from vocode.streaming.models.message import BaseMessage
from vocode.streaming.synthesizer.base_synthesizer import BaseSynthesizer, SynthesisResult
from vocode.streaming.models.synthesizer import SynthesizerConfig
from vocode.streaming.models.synthesizer import WavesSynthesizerConfig
    
class WavesSynthesizer(BaseSynthesizer[WavesSynthesizerConfig]):
    CHUNK_SIZE = 320
    
    def __init__(self, synthesizer_config: WavesSynthesizerConfig):
        super().__init__(synthesizer_config)
        self.waves_lightning_url = f"http://waves-api.smallest.ai/api/v1/lightning/get_speech"
        self.thread_pool_executor = ThreadPoolExecutor(max_workers=1)
        
    async def create_speech(
            self,
            message: BaseMessage,
            chunk_size: int,
            is_first_text_chunk: bool = False,
            is_sole_text_chunk: bool = False
        ) -> SynthesisResult:
            audio_data = await self._generate_audio(message.text)
            
            async def chunk_generator() -> AsyncGenerator[SynthesisResult.ChunkResult, None]:
                for i in range(0, len(audio_data), chunk_size):
                    chunk = audio_data[i:i+chunk_size]
                    yield SynthesisResult.ChunkResult(chunk, i+chunk_size >= len(audio_data))

            def get_message_up_to(seconds: float) -> str:
                # This is a simplified implementation. You might want to improve this
                # based on the actual audio duration and text alignment.
                return message.text
            
            return SynthesisResult(chunk_generator(), get_message_up_to)
    
    async def _generate_audio(self, text: str) -> bytes:
        payload = {
            "text": text,
            "voice_id": self.synthesizer_config.voice_id,
            "add_wav_header": False,
            "sample_rate": self.synthesizer_config.sampling_rate,
            "language": self.synthesizer_config.language,
            "speed": self.synthesizer_config.speed,
            "keep_ws_open": True,
            "remove_extra_silence": self.synthesizer_config.remove_extra_silence,
            "transliterate": self.synthesizer_config.transliterate,
            "get_end_of_response_token": True,
        }
        logger.info(f"payload for generate audio: {payload}")
        audio_data = b""
        first = False
        
        headers = {
            "Authorization": f"Bearer {self.synthesizer_config.api_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.request("POST", self.waves_lightning_url, json=payload, headers=headers)
        return response.content

