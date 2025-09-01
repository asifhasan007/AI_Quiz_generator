def transcribe_audio(audio_path, model):
    try:
        print("--> Transcribing audio...")
        result = model.transcribe(audio_path)
        print("---> Transcription successful.")
        return result['text']
    except Exception as e:
        print(f"Error during transcription: {e}")
        return ""
