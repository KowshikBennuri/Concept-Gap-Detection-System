import whisper
import os

def perform_initial_guard(audio_path, keywords, whisper_model):
    # Full transcription for word count and relevance check
    result = whisper_model.transcribe(audio_path)
    transcript = result['text']
    words = transcript.split()
    
    # Minimum word count validation
    if len(words) < 15:
        return False, "Explanation too short. Please provide more detail.", transcript

    # Keyword presence validation
    found_keywords = [k for k in keywords if k.lower() in transcript.lower()]
    
    if len(found_keywords) == 0:
        return False, "Topic relevance not found. Explanation inappropriate.", transcript
        
    return True, "Passed Guard", transcript