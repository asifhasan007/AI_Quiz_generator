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

app = Flask(__name__)
CORS(app)

@app.route('/api/generate-quiz', methods=['POST'])
def handle_quiz_generation():
    app.logger.info("API endpoint hit: /api/generate-quiz") # Use logger instead of print
    
    data = request.get_json()
    if not data or 'input_source' not in data:
        app.logger.error("Request failed: Missing 'input_source' in request body")
        return jsonify({"error": "Missing 'input_source' in request body"}), 400
        
    input_source = data['input_source']
    
    try:
        app.logger.info(f"Step 1: Processing input source: {input_source}")
        transcribed_text = "..." # Placeholder for actual transcription
        
        if not transcribed_text:
            raise Exception("Transcription resulted in empty text.")

        app.logger.info("Step 2: Extracting key points...")
        key_points = extract_keypoints_improved(transcribed_text)
        if not key_points:
            raise Exception("Key point extraction failed.")

        app.logger.info("Step 3: Generating quiz with Gemini...")
        raw_quiz_text = "..." 
    
        app.logger.info("Step 4: Parsing final quiz...")
        mcq_quiz, tf_quiz = parse_quiz_text(raw_quiz_text)
        combined_quiz = mcq_quiz + tf_quiz

        app.logger.info("Pipeline complete. Sending final quiz data to frontend.")
        return jsonify(combined_quiz)

    except Exception as e:
        app.logger.error(f"An error occurred in the pipeline: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)