import requests
import json

def transcribe_audio_file(file_path):
    url = 'http://127.0.0.1:5000/transcribe'
    
    # Open and send the file
    with open(file_path, 'rb') as f:
        files = {'file': ('test_audio.mp3', f, 'audio/mp3')}
        response = requests.post(url, files=files)
    
    # Print the full response for debugging
    print("Response Status:", response.status_code)
    print("Full Response:", json.dumps(response.json(), indent=2))
    
    # Return the transcription if successful
    if response.status_code == 200:
        return response.json().get('transcription')
    else:
        return f"Error: {response.json().get('error', 'Unknown error')}"

if __name__ == "__main__":
    print("\nTranscribing test_audio.mp3...")
    result = transcribe_audio_file('test_audio.mp3')
    print("\nTranscription result:", result)
