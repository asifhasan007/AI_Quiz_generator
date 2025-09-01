from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import logging

from quiz_pipeline.video_processing import extract_audio_from_url
from quiz_pipeline.transcription import transcribe_audio
from quiz_pipeline.keypoint_extraction import extract_keypoints_improved
from quiz_pipeline.quiz_generation import generate_quiz_with_gemini, parse_quiz_text

import whisper
whisper_model = whisper.load_model('base')

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
        
    input_source = data['video_url']
    
    if not input_source.startswith(('http://', 'https://')):
        app.logger.error(f"Invalid input: '{input_source}' is not a valid URL.")
        return jsonify({"error": "Invalid input source. Please provide a valid URL."}), 400
    try:
        app.logger.info(f"Step 1: Processing video URL: {input_source}")
        audio_file = extract_audio_from_url(input_source)
        if not audio_file:
            raise Exception("Failed to extract audio from URL.")
        app.logger.info("-> Audio extraction successful.")

        app.logger.info("Step 2: Transcribing audio...")
        transcribed_text = transcribe_audio(audio_file, whisper_model)
        if not transcribed_text:
            raise Exception("Transcription failed or resulted in empty text.")
        app.logger.info("-> Transcription successful.")

        app.logger.info("Step 3: Extracting key points...")
        key_points = extract_keypoints_improved(transcribed_text)
        if not key_points:
            raise Exception("Key point extraction failed.")
        app.logger.info(f"-> Successfully extracted {len(key_points)} key points.")

        app.logger.info("Step 4: Generating quiz with Gemini...")
        key_points_string = "\n- ".join(key_points)
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
    app.run(debug=True, port=5000)

