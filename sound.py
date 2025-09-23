from google import genai
from google.genai import types
import os
import pyaudio
import wave
import io

# Initialize Gemini client
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

speech_config = types.SpeechConfig(
    voice_config=types.VoiceConfig(
        prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Zephyr")
    )
)

# Generate TTS
response = client.models.generate_content(
    model="models/gemini-2.5-flash-preview-tts",
    contents="Hello, This is Edza Assistant. How can I help you?",
    config=types.GenerateContentConfig(
        response_modalities=["AUDIO"],
        speech_config=speech_config,
    ),
)

# Extract raw audio bytes
audio_bytes = response.candidates[0].content.parts[0].inline_data.data

# Gemini default audio settings
SAMPLE_RATE = 24000  # Hz
CHANNELS = 1         # mono
SAMPLE_WIDTH = 2     # 16-bit PCM

# --- Play audio first ---
p = pyaudio.PyAudio()
stream = p.open(format=p.get_format_from_width(SAMPLE_WIDTH),
                channels=CHANNELS,
                rate=SAMPLE_RATE,
                output=True)

stream.write(audio_bytes)

stream.stop_stream()
stream.close()
p.terminate()

# --- Save as proper WAV ---
with wave.open("audi1.wav", "wb") as wf:
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(SAMPLE_WIDTH)
    wf.setframerate(SAMPLE_RATE)
    wf.writeframes(audio_bytes)

print("Audio played and saved as audi1.wav")
