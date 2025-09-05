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
from quiz_pipeline.os_video_handler import process_os_video_path
from quiz_pipeline.keypoint_extraction import extract_keypoints_improved
 
def is_local_path(path: str) -> bool:
    # Clean quote marks and whitespace from input
    clean_path = path.strip().strip('\'"')
    # Check if absolute path
    if os.path.isabs(clean_path) and os.path.exists(clean_path):
        return True
    # Exclude common URL schemes
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
 
load_dotenv()
 
@app.route('/api/generate-quiz', methods=['POST'])
def handle_quiz_generation():
    app.logger.info("API endpoint hit: /api/generate-quiz")
    content_type = request.content_type
 
    try:
        if 'application/json' in content_type:
            app.logger.info("Processing JSON request")
            data = request.get_json()
 
            if not data:
                return jsonify({"error": "Empty JSON body"}), 400
 
            if 'os_video_path' in data:
                video_path = data['os_video_path']
                if not (os.path.isabs(video_path) and os.path.exists(video_path)):
                    return jsonify({"error": "Invalid or non-existing file path."}), 400
                result = process_os_video_path(video_path)
                return jsonify([result])
 
            if 'video_url' in data:
                input_str = data['video_url']
                # Split only on commas or newlines to avoid breaking paths with spaces
                raw_items = re.split(r'[,\\n]+', input_str)
                clean_items = [i.strip().strip('\'"') for i in raw_items if i.strip()]
 
                app.logger.info(f"Received items: {clean_items}")
 
                # If first item looks like local path, treat all as local paths
                if clean_items and is_local_path(clean_items[0]):
                    results = []
                    for path in clean_items:
                        if is_local_path(path):
                            results.append(process_os_video_path(path))
                        else:
                            results.append({"error": f"Invalid or inaccessible path: {path}"})
                    return jsonify(results)
                else:
                    # treat as URLs
                    results = []
                    for url in clean_items:
                        app.logger.info(f"Processing URL: {url}")
                        try:
                            audio_file = extract_audio_from_url(url)
                            if not audio_file:
                                app.logger.warning(f"Audio extraction failed for {url}")
                                continue
                            transcribed_text = transcribe_audio(audio_file, whisper_model)
                            if not transcribed_text:
                                app.logger.warning(f"Transcription failed for {url}")
                                continue
                            key_points = extract_keypoints_improved(transcribed_text)
                            if not key_points:
                                app.logger.warning(f"Key point extraction failed for {url}")
                                continue
                            key_str = "\n- ".join(key_points)
                            quiz_raw = generate_quiz_with_gemini(key_str)
                            if not quiz_raw:
                                app.logger.warning(f"Quiz generation failed for {url}")
                                continue
                            mcq, tf = parse_quiz_text(quiz_raw)
                            results.append({
                                "source": url,
                                "quiz_data": mcq + tf
                            })
                        except Exception as ex:
                            app.logger.error(f"Error processing {url}: {ex}", exc_info=True)
                            results.append({"source": url, "error": str(ex)})
                    return jsonify(results)
            else:
                return jsonify({"error": "Missing 'video_url' or 'os_video_path' in request."}), 400
 
        elif 'multipart/form-data' in content_type:
            app.logger.info("Processing form-data request for file upload...")
            if 'file' not in request.files:
                return jsonify({"error": "Missing 'file' in form-data"}), 400
 
            file = request.files['file']
            if file.filename == '':
                return jsonify({"error": "No file selected"}), 400
           
            if file and file.filename.lower().endswith('.pdf'):
                app.logger.info(f"Step 1: Extracting text from PDF: {file.filename}")
                extracted_text = extract_text_from_pdf(file)
               
                if not extracted_text:
                    raise Exception("Text extraction from PDF failed.")
 
                app.logger.info("Step 2: Extracting key points...")
                key_points = extract_keypoints_improved(extracted_text)
                if not key_points:
                    raise Exception("Key point extraction failed.")
 
                app.logger.info("Step 3: Generating quiz...")
                key_points_string = "\n- ".join(key_points)
                raw_quiz_text = generate_quiz_with_gemini(key_points_string)
                if not raw_quiz_text:
                    raise Exception("Quiz generation failed.")
 
                app.logger.info("Step 4: Parsing quiz...")
                mcq_quiz, tf_quiz = parse_quiz_text(raw_quiz_text)
               
                single_quiz_response = [{
                    "source_name": file.filename,
                    "quiz_data": mcq_quiz + tf_quiz
                }]
                return jsonify(single_quiz_response)
            else:
                return jsonify({"error": "Invalid file type. Please upload a PDF."}), 400
        else:
            return jsonify({"error": f"Unsupported Content-Type: {content_type}"}), 415
 
    except Exception as e:
        app.logger.error(f"An error occurred in the pipeline: {e}", exc_info=True)
        return jsonify({"error": "An internal server error occurred. Please check the backend logs."}), 500
 
if __name__ == '__main__':
    if not whisper_model:
        logging.error("Application cannot start because the Whisper model failed to load.")
    else:
        app.run(debug=True, port=5000)
 