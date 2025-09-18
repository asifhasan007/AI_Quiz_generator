from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import logging
import re
import whisper
import os
from urllib.parse import urlparse
from quiz_pipeline.video_processing import extract_audio_from_url
from quiz_pipeline.pdf_processing import extract_text_from_pdf
from quiz_pipeline.transcription import transcribe_audio
from quiz_pipeline.quiz_generation import generate_quiz_with_gemini, parse_quiz_text
from quiz_pipeline.keypoint_extraction import extract_keypoints_improved
from quiz_pipeline.os_video_handler import process_local_path 
load_dotenv()

def is_local_path(path: str) -> bool:
    clean_path = path.strip().strip('\'"')
    if os.path.isabs(clean_path) and os.path.exists(clean_path):
        return True
    parsed = urlparse(clean_path)
    if parsed.scheme in ('http', 'https', 'ftp', 'ftps'):
        return False
    return False

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

try:
    whisper_model = whisper.load_model('base')
    logging.info("Whisper model loaded successfully.")
except Exception as e:
    logging.critical(f"Failed to load Whisper model: {e}", exc_info=True)
    whisper_model = None

def is_url(string):
    try:
        result = urlparse(string)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

@app.route('/api/generate-quiz', methods=['POST'])
def handle_quiz_generation():
    app.logger.info("API endpoint hit: /api/generate-quiz")
    content_type = request.content_type
    try:
        if 'application/json' in content_type:
            data = request.get_json()
            if not data or 'source' not in data:
                return jsonify({"error": "Request must contain a 'source' key in the JSON body."}), 400

            source = data['source'].strip()
            
            if not is_url(source):
                app.logger.info(f"Processing as a local path: {source}")
                
                if not os.path.exists(source):
                    return jsonify({"error": f"Path does not exist on the server: {source}"}), 404

                result = process_local_path(source)
                
                if 'error' in result:
                    return jsonify(result), 400
                return jsonify([result]) 

            else:
                app.logger.info(f"Processing as a URL: {source}")

                audio_file = extract_audio_from_url(source)
                if not audio_file:
                    return jsonify({"error": "Failed to download or extract audio from URL."}), 400

                transcribed_text = transcribe_audio(audio_file, whisper_model)
                if not transcribed_text:
                    return jsonify({"error": "Transcription failed for the URL."}), 400

                key_points = extract_keypoints_improved(transcribed_text)
                if not key_points:
                    return jsonify({"error": "Key point extraction failed."}), 400

                quiz_raw = generate_quiz_with_gemini("\n- ".join(key_points))
                mcq, tf = parse_quiz_text(quiz_raw)
                
                result = {"source_name": source, "quiz_data": mcq + tf}
                return jsonify([result])

        elif 'multipart/form-data' in content_type:
            app.logger.info("Processing PDF file upload.")
            if 'file' not in request.files:
                return jsonify({"error": "Missing 'file' in form-data"}), 400
            
            file = request.files['file']
            if file and file.filename.lower().endswith('.pdf'):
                text = extract_text_from_pdf(file.stream)
                key_points = extract_keypoints_improved(text)
                quiz_raw = generate_quiz_with_gemini("\n- ".join(key_points))
                mcq, tf = parse_quiz_text(quiz_raw)
                result = {"source_name": file.filename, "quiz_data": mcq + tf}
                return jsonify([result])
            else:
                return jsonify({"error": "Invalid file type. Please upload a PDF."}), 400

        else:
            return jsonify({"error": f"Unsupported Content-Type: {content_type}"}), 415
        
    except Exception as e:
        app.logger.error(f"An unhandled error occurred: {e}", exc_info=True)
        return jsonify({"error": "An internal server error occurred."}), 500
 
if __name__ == '__main__':
    if not whisper_model:
        logging.error("Application cannot start because the Whisper model failed to load.")
    else:
        app.run(debug=True, port=5000)