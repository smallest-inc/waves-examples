import io
import numpy as np
from typing import Union
from pydub import AudioSegment

MAX_BUFFER_SIZE = 16000000 # 16*10^6 * 2 Bytes -> 32 MB

class AudioBuffer:

    def __init__(self,
                 buffer: Union[bytes, bytearray],
                 max_length: int =  MAX_BUFFER_SIZE,
                 overwrite: bool = False,
                 chunk_size: int = 320,
                 sample_rate: int = 16000):
        
        # TODO: handle len(buffer) >= max_length in __init__
        if buffer:
            self.buffer = bytearray(buffer)
        else:
            self.buffer = b''
        self.max_length = max_length
        self.overwrite = overwrite
        self.chunk_size = chunk_size
        self.sample_rate = sample_rate
        self.dtype = np.int16

    def __len__(self):
        return len(self.buffer) // 2
    
    def __bool__(self):
        return bool(self.buffer)
    
    @classmethod
    def from_mp3(cls, buffer: bytes, sample_rate=16000):
        return AudioBuffer(AudioSegment.from_mp3(io.BytesIO(buffer)).set_frame_rate(sample_rate).set_channels(1).raw_data)

    @classmethod
    def from_mp3_file(cls, mp3_file: str, sample_rate=16000):
        return AudioBuffer(AudioSegment.from_mp3(mp3_file).set_frame_rate(sample_rate).set_channels(1).raw_data)

    def extend(self, audio_buffer):
        
        total_length = len(self) + len(audio_buffer)

        if total_length <= self.max_length:
            self.buffer += audio_buffer.buffer
            return
        else:
            if self.overwrite:
                self.buffer = (self.buffer + audio_buffer.buffer)[-2*self.max_length:]
                return
            else:
                self.buffer = (self.buffer + audio_buffer.buffer)[:2*self.max_length]
                return

    def get_numpy(self):

        return np.frombuffer(self.buffer, dtype=self.dtype).copy()

    def get_bytes(self):
        return bytes(self.buffer)

    def clear(self):

        self.buffer = bytearray(b'')
        return

    def pop_chunk(self):
        
        if len(self) <= self.chunk_size:
            audio_chunk = self.buffer
            self.buffer = bytearray(b'')
            return bytes(audio_chunk)

        audio_chunk = self.buffer[:self.chunk_size*2]
        self.buffer = self.buffer[2*self.chunk_size:]

        return bytes(audio_chunk)

    def pop_chunk_raw(self):
        audio_chunk = self.pop_chunk()

        return AudioSegment(audio_chunk.tobytes(), 
                                frame_rate=self.sampling_rate, 
                                sample_width=self.buffer.dtype.itemsize, 
                                channels=1).raw_data

    def export(self, path: str, format: str):
        
        audio = AudioSegment(data=bytes(self.buffer),
                             sample_width=2,
                             frame_rate=self.sample_rate,
                             channels=1)
        audio.export(path, format=format)