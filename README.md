# Whisper API Transcription Service

A Flask API service that uses OpenAI's Whisper API to transcribe audio files.

## Features

- Transcribe audio files using OpenAI's Whisper API
- Support for multiple audio formats (MP3, WAV, M4A, OGG)
- Simple REST API endpoint

## Setup

1. Clone the repository
```bash
git clone <your-repo-url>
cd whisper-api-demo
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory and add your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

4. Run the application
```bash
python app.py
```

The API will be available at `http://127.0.0.1:8000`

## API Usage

### Transcribe Endpoint

`POST /transcribe`

Send a POST request with a form-data body containing an audio file:
- Key: `file`
- Value: Your audio file (supported formats: MP3, WAV, M4A, OGG)

Example response:
```json
{
    "transcription": "Your transcribed text here"
}
```

Example usage with curl:
```bash
curl -X POST -F "file=@your-audio-file.mp3" http://127.0.0.1:8000/transcribe
```

## Deployment

This application is configured for deployment on Render. The `render.yaml` file contains the necessary configuration.

1. Push your code to GitHub
2. Create a new Web Service on Render
3. Connect your GitHub repository
4. Add your `OPENAI_API_KEY` to the environment variables
5. Deploy!

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (set in Render dashboard)
- `PORT`: Port number (default: 8000)

## License

MIT
