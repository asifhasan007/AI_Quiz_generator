import os
from quiz_pipeline.video_processing import extract_audio_from_local_video
from quiz_pipeline.transcription import transcribe_audio
from quiz_pipeline.keypoint_extraction import extract_keypoints_improved
from quiz_pipeline.quiz_generation import generate_quiz_with_gemini, parse_quiz_text
import whisper
 
ALLOWED_VIDEO_EXTENSIONS = {'.mp4', '.mkv', '.webm', '.mov', '.avi'}
 
try:
    whisper_model = whisper.load_model('base')
except Exception as e:
    print(f"Failed to load Whisper model: {e}")
    whisper_model = None
 
def process_os_video_path(video_path, whisper_model_override=None):
    filename = os.path.basename(video_path)
    file_ext = os.path.splitext(filename)[1].lower()
 
    if file_ext not in ALLOWED_VIDEO_EXTENSIONS:
        return {"error": f"Unsupported file type: {file_ext}"}
    if not os.path.isfile(video_path):
        return {"error": "File does not exist."}
    model = whisper_model_override if whisper_model_override is not None else whisper_model
    if model is None:
        return {"error": "Whisper model is not loaded."}
 
    temp_audio_path = f"temp_{filename}.mp3"
    audio_file = extract_audio_from_local_video(video_path, temp_audio_path)
    if not audio_file:
        return {"error": "Audio extraction failed."}
 
    try:
        transcribed_text = transcribe_audio(audio_file, model)
    finally:
        try:
            os.remove(audio_file)
        except Exception:
            pass
 
    if not transcribed_text or len(transcribed_text.strip()) == 0:
        return {"error": "Transcription failed or text is empty."}
 
    key_points = extract_keypoints_improved(transcribed_text)
    if not key_points:
        return {"error": "Key point extraction failed."}
    key_points_string = "\n- ".join(key_points)
    raw_quiz_text = generate_quiz_with_gemini(key_points_string)
    if not raw_quiz_text:
        return {"error": "Quiz generation failed."}
 
    mcq_quiz, tf_quiz = parse_quiz_text(raw_quiz_text)
    quiz_data = mcq_quiz + tf_quiz
 
    return {"source_name": filename, "quiz_data": quiz_data}