# 🎵 AI Lyrics Sync Tool

A desktop application that automatically aligns song lyrics with audio
extracted from MP4 videos, allowing you to edit timings and export
perfectly synchronized lyric files in **LRC**, **SRT**, and **TXT**
formats.

------------------------------------------------------------------------

## ✨ Features

-   🎬 Load MP4 and extract audio automatically\
-   🤖 AI-powered lyric--audio alignment\
-   📊 Interactive table view of timestamps & lyrics\
-   ▶ Built-in audio player with seek bar\
-   ✂ Split and 🔗 merge lyric segments\
-   ⬅ / ➡ Nudge timestamps by milliseconds\
-   📤 Export to LRC / SRT / TXT\
-   🪟 Modern PySide6 GUI

------------------------------------------------------------------------

## 📸 Workflow Overview

1.  Load an MP4 video\
2.  Paste lyrics\
3.  Click **Auto Sync**\
4.  Review timings in the table\
5.  Edit using split/merge/nudge\
6.  Export subtitle/lyric files

------------------------------------------------------------------------

## 🛠 Tech Stack

-   Python 3.9+
-   PySide6 (GUI)
-   MoviePy / FFmpeg
-   AI alignment engine (Whisper-based or similar)
-   Qt Multimedia

------------------------------------------------------------------------

## 📂 Project Structure

    lyrics_sync/
    │
    ├── main.py
    ├── ui/
    │   └── main_window.py
    │
    ├── core/
    │   ├── extractor.py
    │   └── aligner.py
    │
    ├── exporters/
    │   ├── lrc.py
    │   ├── srt.py
    │   └── txt.py
    │
    ├── requirements.txt
    └── README.md

------------------------------------------------------------------------

## 🚀 Installation

### 1️⃣ Clone the Repository

    git clone https://github.com/yourusername/lyrics-sync-tool.git
    cd lyrics-sync-tool

### 2️⃣ Create Virtual Environment

    python -m venv venv
    venv\Scripts\activate

### 3️⃣ Install Dependencies

    pip install -r requirements.txt

------------------------------------------------------------------------

## ▶ Usage

Run the application:

    python main.py

Steps:

-   Click **Load MP4**
-   Paste lyrics
-   Click **Auto Sync**
-   Edit segments if required
-   Export to LRC/SRT/TXT

------------------------------------------------------------------------

## 📄 Output Formats

-   **LRC** -- Karaoke-style lyrics
-   **SRT** -- Subtitle format for videos
-   **TXT** -- Plain text transcript

------------------------------------------------------------------------

## 🧪 Status

✅ Auto Sync\
✅ Table Visualization\
✅ Split & Merge\
✅ Manual Editing\
✅ Export Formats

Project is **feature complete** and ready for demonstration, academic
submission, or hackathons.

------------------------------------------------------------------------

## 📜 License

MIT License -- free to use, modify, and distribute.

------------------------------------------------------------------------

## 🙌 Credits

Developed by **Sachin Kumar**\
B.Tech AI & DS -- VIPS Delhi

Inspired by modern speech--text alignment systems.

------------------------------------------------------------------------

## ⭐ If you like this project

Give it a star on GitHub and share feedback!
