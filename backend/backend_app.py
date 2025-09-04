from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import logging
import re
import whisper
from quiz_pipeline.video_processing import extract_audio_from_url
from quiz_pipeline.pdf_processing import extract_text_from_pdf
from quiz_pipeline.transcription import transcribe_audio
from quiz_pipeline.keypoint_extraction import extract_keypoints_improved
from quiz_pipeline.quiz_generation import generate_quiz_with_gemini, parse_quiz_text

try:
    whisper_model = whisper.load_model('base')
    logging.info("Whisper model loaded successfully.")
except Exception as e:
    logging.critical(f"Failed to load Whisper model: {e}", exc_info=True)
    whisper_model = None

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
load_dotenv()
app = Flask(__name__)
CORS(app)

@app.route('/api/generate-quiz', methods=['POST'])
def handle_quiz_generation():
    app.logger.info("API endpoint hit: /api/generate-quiz")
    content_type = request.content_type
    
    try:
        if 'application/json' in content_type:
            app.logger.info("Processing JSON request for video URL(s)...")
            data = request.get_json()
            if not data or 'video_url' not in data:
                return jsonify({"error": "Missing 'video_url' in request body"}), 400

            input_urls = data['video_url']
            video_urls = [url.strip() for url in re.split(r'[,\s]+', input_urls) if url.strip()]
            
            if not video_urls:
                return jsonify({"error": "Please provide at least one valid video URL."}), 400

            all_quizzes = []

            for i, url in enumerate(video_urls, 1):
                app.logger.info(f"--- Processing Video {i}/{len(video_urls)}: {url} ---")
                try:
                    audio_file = extract_audio_from_url(url)
                    if not audio_file:
                        app.logger.warning(f"Audio extraction failed for {url}")
                        continue
                    
                    transcribed_text = transcribe_audio(audio_file, whisper_model)
                    if not transcribed_text:
                        app.logger.warning(f"Transcription failed for {url}")
                        continue

                    app.logger.info(f"Extracting key points for {url}...")
                    key_points = extract_keypoints_improved(transcribed_text)
                    if not key_points:
                        app.logger.warning(f"Key point extraction failed for {url}")
                        continue
                    app.logger.info(f"-> Successfully extracted {len(key_points)} key points for {url}.")

                    app.logger.info(f"Generating quiz with Gemini for {url}...")
                    key_points_string = "\\n- ".join(key_points)
                    raw_quiz_text = generate_quiz_with_gemini(key_points_string)
                    if not raw_quiz_text:
                        app.logger.warning(f"Quiz generation with Gemini API failed for {url}")
                        continue
                    
                    mcq_quiz, tf_quiz = parse_quiz_text(raw_quiz_text)
                    combined_quiz = mcq_quiz + tf_quiz
                    
                    all_quizzes.append({
                        "source_name": url,
                        "quiz_data": combined_quiz
                    })
                    app.logger.info(f"-> Successfully generated and parsed quiz for {url}")

                except Exception as e:
                    app.logger.error(f"An error occurred processing video {url}: {e}", exc_info=True)
                    all_quizzes.append({
                        "source_name": url,
                        "error": f"Failed to process video. See logs for details: {e}"
                    })

            app.logger.info("--- All videos processed. Sending final quizzes to frontend. ---")
            return jsonify(all_quizzes)

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
