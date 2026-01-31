def save_txt(segments, path):
    with open(path, "w", encoding="utf-8") as f:
        for seg in segments:
            f.write(f"{seg['text']}\n")