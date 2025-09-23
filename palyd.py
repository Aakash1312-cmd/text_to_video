from pydub import AudioSegment

# Load your WAV file
wav_audio = AudioSegment.from_file("audi1.wav", format="wav")

# Export as MP3
wav_audio.export("audi1.mp3", format="mp3")

print("Conversion done!")
