from gtts import gTTS

# Create a simple audio file with some text
text = "Hello, this is a test audio file for our transcription service. Testing one, two, three."
tts = gTTS(text=text, lang='en')

# Save the audio file
tts.save("test_audio.mp3")
print("Test audio file 'test_audio.mp3' has been created!")
