import os
import base64
import tempfile
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from datetime import datetime
from werkzeug.utils import secure_filename

# -----------------------------------
# 1) Basic Logging Setup
# -----------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# -----------------------------------
# 2) Load OpenAI API Key from ENV
#    (Set OPENAI_API_KEY in your environment)
# -----------------------------------
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("No OPENAI_API_KEY found in environment variables.")

# -----------------------------------
# 3) Initialize OpenAI Client
# -----------------------------------
client = OpenAI(api_key=api_key)

# -----------------------------------
# 4) Flask Setup
# -----------------------------------
app = Flask(__name__)
CORS(app)

# Allowed file extensions (change as needed)
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'm4a', 'ogg'}

# -----------------------------------
# Helper: Check File Extension
# -----------------------------------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# -----------------------------------
# Helper: Transcribe Audio with OpenAI
# -----------------------------------
def transcribe_audio(filepath):
    """
    Transcribe an audio file using OpenAI's Whisper API
    """
    logger.info(f"Starting transcription for file: {filepath}")
    try:
        start_time = datetime.now()

        # Read the audio file in binary mode
        with open(filepath, 'rb') as audio_file:
            logger.info("Sending request to OpenAI Whisper API...")
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"Transcription completed in {duration:.2f} seconds")
        return transcript.text

    except Exception as e:
        logger.error(f"Error in transcription: {e}", exc_info=True)
        return f"Error: {str(e)}"

# -----------------------------------
# 5) The Single POST Endpoint: /transcribe
# -----------------------------------
@app.route('/transcribe', methods=['POST'])
def transcribe():
    """
    Receives either:
      - form-data with a file:  { file: <audio-file> }
      - JSON with base64 audio: { "audio": "data:audio/mp3;base64,..." }
    Returns JSON: { transcription: "<text>" }
    """
    try:
        # 1) Check if 'file' is present (form-data)
        if 'file' in request.files:
            file = request.files['file']
            if not file or file.filename == '':
                return jsonify({"error": "No file selected"}), 400
            
            if not allowed_file(file.filename):
                return jsonify({"error": "File type not allowed"}), 400
            
            filename = secure_filename(file.filename)
            temp_path = os.path.join(tempfile.gettempdir(), filename)
            file.save(temp_path)
            
            try:
                text = transcribe_audio(temp_path)
                return jsonify({"transcription": text})
            finally:
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.remove(temp_path)

        # 2) If no 'file', try reading JSON with base64
        data = request.get_json()
        if data and 'audio' in data:
            # Remove any data URL prefix, e.g. "data:audio/mp3;base64,"
            base64_data = data['audio']
            if ',' in base64_data:
                base64_data = base64_data.split(',')[1]

            try:
                audio_binary = base64.b64decode(base64_data)
            except Exception as e:
                logger.error("Invalid base64 audio data", exc_info=True)
                return jsonify({"error": "Invalid base64 audio data"}), 400

            # Write to a temporary file
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
                tmp.write(audio_binary)
                temp_path = tmp.name

            try:
                text = transcribe_audio(temp_path)
                return jsonify({"transcription": text})
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

        # If neither file nor 'audio' in JSON was provided
        return jsonify({"error": "No audio data provided"}), 400

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

# -----------------------------------
# 6) (Optional) Root endpoint to confirm it's running
# -----------------------------------
@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "Hello from the transcribe server!"})

# -----------------------------------
# 7) Local Development Entry Point
# -----------------------------------
if __name__ == '__main__':
    # For local testing only:
    #   python app.py
    # Then open http://127.0.0.1:5000/
    app.run(debug=True, port=5000)
