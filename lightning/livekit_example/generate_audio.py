import asyncio
import aiohttp
import wave
from livekit.plugins import smallest, deepgram

from dotenv import load_dotenv
load_dotenv()

async def test_tts():
    # Create an aiohttp session
    async with aiohttp.ClientSession() as session:
        # Create TTS instance with the session
        tts = smallest.TTS(
            http_session=session  # Pass the aiohttp session here
        )

        # Synthesize text into speech
        frames = []
        async for audio in tts.synthesize(text="Hello, this is a test of the TTS system."):
            frames.append(audio.frame)

        # Save frames to a WAV file
        with wave.open("output.wav", "wb") as wav_file:
            wav_file.setnchannels(1)  # Mono audio
            wav_file.setsampwidth(2)  # 2 bytes per sample (16-bit)
            wav_file.setframerate(tts._opts.sample_rate)
            
            for frame in frames:
                # Convert the frame data to bytes
                frame_bytes = frame.data.tobytes()
                wav_file.writeframes(frame_bytes)

        print("Audio saved to output.wav")

        # Optionally, continue with STT if needed
        deepgram_stt = deepgram.STT(http_session=session)
        res = await deepgram_stt.recognize(buffer=frames)
        print(res)

# Run the async test
if __name__ == "__main__":
    asyncio.run(test_tts())