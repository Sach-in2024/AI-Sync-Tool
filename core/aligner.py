import re
from faster_whisper import WhisperModel

def normalize(text: str):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def split_lyrics(lyrics_text: str):
    return [line.strip() for line in lyrics_text.splitlines() if line.strip()]

def align_audio(audio_path, lyrics_text=None, progress_callback=None):
    """
    Align pasted lyrics to audio using Faster-Whisper transcription.
    Returns list of segments: [{"start", "end", "text"}, ...]
    """

    model = WhisperModel("tiny", device="cpu", compute_type="float32")

    segments_gen, _ = model.transcribe(
        audio_path,
        beam_size=5,
        vad_filter=True,
        word_timestamps=True
    )

    whisper_words = []
    for seg in segments_gen:
        for w in seg.words:
            whisper_words.append({
                "start": float(w.start),
                "end": float(w.end),
                "text": w.word.strip()
            })

    # No lyrics -> just return words
    if not lyrics_text:
        results = []
        for w in whisper_words:
            results.append({"start": w["start"], "end": w["end"], "text": w["text"]})
            if progress_callback:
                progress_callback(results.copy())
        return results

    # Lyrics mode
    lyric_lines = split_lyrics(lyrics_text)
    lyric_norm = [normalize(l) for l in lyric_lines]

    results = []
    w_i = 0
    for idx, (line, norm_line) in enumerate(zip(lyric_lines, lyric_norm)):
        words = norm_line.split()
        start_t, end_t = None, None
        for lw in words:
            while w_i < len(whisper_words):
                ww = normalize(whisper_words[w_i]["text"])
                if ww == lw:
                    if start_t is None:
                        start_t = whisper_words[w_i]["start"]
                    end_t = whisper_words[w_i]["end"]
                    w_i += 1
                    break
                w_i += 1
        if start_t is None:
            start_t = results[-1]["end"] if results else 0.0
            end_t = start_t + 1.0
        seg = {"start": start_t, "end": end_t, "text": line}
        results.append(seg)
        if progress_callback:
            progress_callback(results.copy())
    return results