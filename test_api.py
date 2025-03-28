import requests

def test_transcription():
    url = 'http://127.0.0.1:5000/transcribe'
    
    # Open the audio file
    files = {
        'file': ('test_audio.mp3', open('test_audio.mp3', 'rb'), 'audio/mp3')
    }
    
    # Make the request
    response = requests.post(url, files=files)
    
    # Print the response
    print("Status Code:", response.status_code)
    print("Response:", response.json())

if __name__ == "__main__":
    test_transcription()
