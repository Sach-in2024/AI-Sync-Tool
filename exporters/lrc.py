def save_lrc(segments, path):
    with open(path, "w", encoding="utf-8") as f:
        for seg in segments:
            start_min = int(seg["start"] // 60)
            start_sec = seg["start"] % 60
            f.write(f"[{start_min:02d}:{start_sec:05.2f}]{seg['text']}\n")