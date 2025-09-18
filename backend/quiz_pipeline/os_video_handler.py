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

def _process_single_video(video_path, model):
    filename = os.path.basename(video_path)

    if model is None:
        return {"error": "Whisper model is not loaded."}

    temp_audio_path = f"temp_{filename}.mp3"
    audio_file = extract_audio_from_local_video(video_path, temp_audio_path)
    if not audio_file:
        return {"error": f"Audio extraction failed for {filename}"}

    transcribed_text = ""
    try:
        transcribed_text = transcribe_audio(audio_file, model)
    finally:
        if os.path.exists(audio_file):
            os.remove(audio_file)

    if not transcribed_text or len(transcribed_text.strip()) == 0:
        return {"error": "Transcription failed or produced no text."}
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

def _process_video_directory(directory_path, model):
    all_transcriptions = []
    
    video_files = [
        os.path.join(directory_path, f) for f in sorted(os.listdir(directory_path))
        if os.path.isfile(os.path.join(directory_path, f)) and os.path.splitext(f)[1].lower() in ALLOWED_VIDEO_EXTENSIONS
    ]

    if not video_files:
        return {"error": f"No supported video files found in directory: {os.path.basename(directory_path)}"}
        
    if model is None:
        return {"error": "Whisper model is not loaded."}

    for video_path in video_files:
        print(f"Processing video in directory: {os.path.basename(video_path)}")
        temp_audio_path = f"temp_{os.path.basename(video_path)}.mp3"
        audio_file = extract_audio_from_local_video(video_path, temp_audio_path)
        
        if not audio_file:
            print(f"Warning: Could not extract audio from {os.path.basename(video_path)}")
            continue

        try:
            transcribed_text = transcribe_audio(audio_file, model)
            if transcribed_text:
                all_transcriptions.append(transcribed_text)
        finally:
            if os.path.exists(audio_file):
                os.remove(audio_file)

    if not all_transcriptions:
        return {"error": "Could not transcribe any videos in the directory."}

    combined_text = "\n\n--- End of Video ---\n\n".join(all_transcriptions)
    key_points = extract_keypoints_improved(combined_text)
    if not key_points:
        return {"error": "Key point extraction failed for the combined video content."}

    key_points_string = "\n- ".join(key_points)
    raw_quiz_text = generate_quiz_with_gemini(key_points_string)
    if not raw_quiz_text:
        return {"error": "Combined quiz generation failed."}

    mcq_quiz, tf_quiz = parse_quiz_text(raw_quiz_text)
    
    source_name = f"Combined Quiz from directory: {os.path.basename(directory_path)}"
    return {"source_name": source_name, "quiz_data": mcq_quiz + tf_quiz}

def process_local_path(path):
    if os.path.isdir(path): 
        return _process_video_directory(path, whisper_model)
    elif os.path.isfile(path): 
        file_ext = os.path.splitext(path)[1].lower()
        if file_ext not in ALLOWED_VIDEO_EXTENSIONS:
            return {"error": f"Unsupported file type: {file_ext}. Only video files are processed."}
        return _process_single_video(path, whisper_model)
    else:
        return {"error": f"The provided path does not exist or is not a valid file/directory: {path}"}