import asyncio
import datetime
import json
import websockets
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
        self.websocket_url = f"wss://call-dev.smallest.ai/invocations_streaming?token={synthesizer_config.api_token}"
        
    async def create_speech(
            self,
            message: BaseMessage,
            chunk_size: int,
            is_first_text_chunk: bool = False,
            is_sole_text_chunk: bool = False
        ) -> SynthesisResult:
            # audio_data = await self._generate_audio(message.text)
            
            async def chunk_generator() -> AsyncGenerator[SynthesisResult.ChunkResult, None]:
                i = 0
                async for audio_chunk in self._generate_audio(message.text):
                    yield SynthesisResult.ChunkResult(audio_chunk, i+chunk_size >= len(audio_chunk))
                    
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
        async with websockets.connect(self.websocket_url) as websocket:
            first = True
            logger.info(f"websocket for waves is connected: {datetime.datetime.now()}")
            await websocket.send(json.dumps(payload))
            while True:
                response = await websocket.recv()
                if response == "<END>":
                    logger.info(f"waves last received audio: {datetime.datetime.now()}")
                    break
                else:
                    if first:   
                        logger.info(f"waves received audio: {datetime.datetime.now()}")
                    yield response
