from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import logging
import re

from quiz_pipeline.video_processing import extract_audio_from_url
from quiz_pipeline.transcription import transcribe_audio
from quiz_pipeline.keypoint_extraction import extract_keypoints_improved
from quiz_pipeline.quiz_generation import generate_quiz_with_gemini, parse_quiz_text

import whisper

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
    
    data = request.get_json()
    if not data or 'video_url' not in data:
        app.logger.error("Request failed: Missing 'video_url' in request body")
        return jsonify({"error": "Missing 'video_url' in request body"}), 400
        
    input_urls = data['video_url']

    video_urls = [url.strip() for url in re.split(r'[,\s]+', input_urls) if url.strip()]

    if not video_urls:
        app.logger.error("No valid URLs provided after parsing.")
        return jsonify({"error": "Please provide at least one valid video URL."}), 400

    all_key_points = []
    
    try:
        for i, url in enumerate(video_urls, 1):
            if not url.startswith(('http://', 'https://')):
                app.logger.warning(f"Skipping invalid input: '{url}' is not a valid URL.")
                continue

            app.logger.info(f"--- Processing Video {i}/{len(video_urls)}: {url} ---")
            
            app.logger.info(f"Step 1: Extracting audio from {url}")
            audio_file = extract_audio_from_url(url)
            if not audio_file:
                app.logger.error(f"Failed to extract audio from {url}. Skipping this video.")
                continue
            app.logger.info("-> Audio extraction successful.")

            app.logger.info("Step 2: Transcribing audio...")
            transcribed_text = transcribe_audio(audio_file, whisper_model)
            if not transcribed_text:
                app.logger.error(f"Transcription failed for {url}. Skipping.")
                continue
            app.logger.info("-> Transcription successful.")

            app.logger.info("Step 3: Extracting key points...")
            key_points = extract_keypoints_improved(transcribed_text)
            if not key_points:
                app.logger.warning(f"No key points were extracted from {url}.")
            else:
                all_key_points.extend(key_points)
                app.logger.info(f"-> Extracted {len(key_points)} key points from this video.")

        if not all_key_points:
            raise Exception("No key points could be extracted from any of the provided videos.")

        app.logger.info(f"--- Combined Processing ---")
        app.logger.info(f"Total key points extracted from all videos: {len(all_key_points)}")
        
        app.logger.info("Step 4: Generating quiz with Gemini from combined key points...")
        key_points_string = "\n- ".join(all_key_points)
        raw_quiz_text = generate_quiz_with_gemini(key_points_string)
        if not raw_quiz_text:
            raise Exception("Quiz generation with Gemini API failed.")
        app.logger.info("-> Quiz generation successful.")

        app.logger.info("Step 5: Parsing final quiz text...")
        mcq_quiz, tf_quiz = parse_quiz_text(raw_quiz_text)
        combined_quiz = mcq_quiz + tf_quiz
        app.logger.info("-> Parsing successful.")

        app.logger.info("--- Pipeline complete. Sending final quiz data to frontend. ---")
        return jsonify(combined_quiz)

    except Exception as e:
        app.logger.error(f"An error occurred in the pipeline: {e}", exc_info=True)
        return jsonify({"error": "An internal server error occurred. Please check the backend logs."}), 500

if __name__ == '__main__':
    if not whisper_model:
        logging.error("Application cannot start because the Whisper model failed to load.")
    else:
        app.run(debug=True, port=5000)
