from flask import Flask, request, jsonify
import os
from openai import OpenAI
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from flask_cors import CORS
import base64
import tempfile
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()
logger.info("Environment variables loaded")

# Initialize the OpenAI client
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    logger.error("No OpenAI API key found in environment variables")
    raise ValueError("OPENAI_API_KEY environment variable is required")

logger.info("Found OpenAI API key in environment")
client = OpenAI(
    api_key=api_key
)
logger.info("OpenAI client initialized")

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
logger.info("Flask app initialized with CORS enabled")

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'm4a', 'ogg'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    logger.info(f"Created uploads directory at {UPLOAD_FOLDER}")

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def transcribe_audio(audio_file_path):
    """
    Transcribe an audio file using OpenAI's Whisper API
    """
    try:
        logger.info(f"Starting transcription for file: {audio_file_path}")
        file_size = os.path.getsize(audio_file_path)
        logger.info(f"Audio file size: {file_size} bytes")

        with open(audio_file_path, "rb") as audio_file:
            start_time = datetime.now()
            logger.info("Sending request to OpenAI Whisper API")
            
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            logger.info(f"Transcription completed in {duration:.2f} seconds")
            
            return transcript.text
    except Exception as e:
        logger.error(f"Error in transcription: {str(e)}", exc_info=True)
        return str(e)

@app.route('/transcribe', methods=['POST'])
def transcribe():
    try:
        if 'file' not in request.files:
            logger.info("No file in request, checking for base64 audio data")
            # Check if the request contains base64 data
            data = request.get_json()
            if data and 'audio' in data:
                logger.info("Found base64 audio data in request")
                # Create a temporary file to store the audio
                with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                    # Remove the data URL prefix if present
                    base64_data = data['audio']
                    if ',' in base64_data:
                        base64_data = base64_data.split(',')[1]
                        logger.debug("Removed data URL prefix from base64 data")
                    
                    # Decode base64 and write to temp file
                    try:
                        audio_data = base64.b64decode(base64_data)
                        temp_file.write(audio_data)
                        temp_file_path = temp_file.name
                        logger.info(f"Successfully wrote base64 audio data to temporary file: {temp_file_path}")
                    except Exception as e:
                        logger.error(f"Error decoding base64 data: {str(e)}", exc_info=True)
                        return jsonify({'error': 'Invalid base64 audio data'}), 400

                try:
                    transcription = transcribe_audio(temp_file_path)
                    logger.info("Successfully transcribed base64 audio")
                    return jsonify({'transcription': transcription})
                finally:
                    # Clean up the temporary file
                    if os.path.exists(temp_file_path):
                        os.remove(temp_file_path)
                        logger.debug(f"Cleaned up temporary file: {temp_file_path}")
            
            logger.warning("No audio data provided in request")
            return jsonify({'error': 'No audio data provided'}), 400

        file = request.files['file']
        if file.filename == '':
            logger.warning("Empty filename provided")
            return jsonify({'error': 'No selected file'}), 400
        
        logger.info(f"Processing file upload: {file.filename}")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            logger.debug(f"Saving file to: {filepath}")
            file.save(filepath)
            
            try:
                transcription = transcribe_audio(filepath)
                logger.info("Successfully transcribed uploaded file")
                return jsonify({'transcription': transcription})
            finally:
                # Clean up the uploaded file
                if os.path.exists(filepath):
                    os.remove(filepath)
                    logger.debug(f"Cleaned up uploaded file: {filepath}")
        
        logger.warning(f"File type not allowed: {file.filename}")
        return jsonify({'error': 'File type not allowed'}), 400

    except Exception as e:
        logger.error(f"Unexpected error in transcribe endpoint: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    logger.info("Starting Flask application")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))
