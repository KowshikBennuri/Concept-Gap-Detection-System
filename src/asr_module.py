import whisper

class ASRModule:
    def __init__(self):
        # Using 'base' model for a good balance of speed and accuracy
        self.model = whisper.load_model("base")

    def transcribe(self, audio_path):
        # fp16=False allows this to run on CPUs without errors
        result = self.model.transcribe(audio_path, fp16=False)
        return result["text"].strip()