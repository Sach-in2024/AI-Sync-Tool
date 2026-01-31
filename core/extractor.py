import os
from pathlib import Path
from pydub import AudioSegment

def extract_audio(video_path: str) -> str:
    """
    Extracts audio from MP4 and saves as WAV.
    Returns the WAV file path.
    """
    video_path = Path(video_path)
    audio_path = video_path.with_suffix(".wav")

    if not audio_path.exists():
        try:
            audio = AudioSegment.from_file(str(video_path), format="mp4")
            audio = audio.set_frame_rate(16000)
            audio.export(str(audio_path), format="wav")
        except Exception as e:
            raise RuntimeError(f"Failed to extract audio: {e}")

    return str(audio_path)