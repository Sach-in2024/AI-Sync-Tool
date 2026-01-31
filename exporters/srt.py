def save_srt(segments, path):
    def fmt_time(s):
        h = int(s // 3600)
        m = int((s % 3600) // 60)
        sec = s % 60
        ms = int((sec - int(sec)) * 1000)
        return f"{h:02d}:{m:02d}:{int(sec):02d},{ms:03d}"

    with open(path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, 1):
            f.write(f"{i}\n")
            f.write(f"{fmt_time(seg['start'])} --> {fmt_time(seg['end'])}\n")
            f.write(f"{seg['text']}\n\n")