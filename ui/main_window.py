import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QTextEdit, QTableWidget,
    QTableWidgetItem, QMessageBox, QProgressBar, QLabel,
    QSlider, QGroupBox
)
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtCore import QTimer, Qt, QUrl, QObject, Signal, QThread

# Windows fixes
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["QT_MULTIMEDIA_HWACCEL"] = "0"

from core.extractor import extract_audio
from core.aligner import align_audio
from exporters.lrc import save_lrc
from exporters.srt import save_srt
from exporters.txt import save_txt


# ------------------ Worker for Auto Sync ------------------
class AlignWorker(QObject):
    finished = Signal(list)
    progress = Signal(list)
    error = Signal(str)

    def __init__(self, audio_path, lyrics):
        super().__init__()
        self.audio_path = audio_path
        self.lyrics = lyrics

    def run(self):
        try:
            def callback(partial):
                self.progress.emit(partial)

            segments = align_audio(
                self.audio_path,
                lyrics_text=self.lyrics,
                progress_callback=callback
            )
            self.finished.emit(segments)
        except Exception as e:
            self.error.emit(str(e))


# ------------------ Main Window ------------------
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("🎵 AI Lyrics Sync Tool")
        self.resize(1150, 820)

        self.audio_path = None
        self.segments = []

        # ---------------- AUDIO PLAYER ----------------
        self.player = QMediaPlayer()
        self.audio_out = QAudioOutput()
        self.player.setAudioOutput(self.audio_out)

        self.seek_slider = QSlider(Qt.Horizontal)
        self.seek_slider.sliderReleased.connect(self.seek_audio)

        self.play_btn = QPushButton("▶ Play")
        self.pause_btn = QPushButton("⏸ Pause")

        # ---------------- BUTTONS ----------------
        self.load_btn = QPushButton("Load MP4")
        self.sync_btn = QPushButton("Auto Sync")

        self.lrc_btn = QPushButton("Export LRC")
        self.srt_btn = QPushButton("Export SRT")
        self.txt_btn = QPushButton("Export TXT")

        self.nudge_left_btn = QPushButton("⬅ -0.1s")
        self.nudge_right_btn = QPushButton("➡ +0.1s")
        self.split_btn = QPushButton("✂ Split")
        self.merge_btn = QPushButton("🔗 Merge")

        # ---------------- TABLE ----------------
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Start", "End", "Text"])
        self.table.horizontalHeader().setStretchLastSection(True)

        # ---------------- PROGRESS ----------------
        self.progress_label = QLabel("Idle")
        self.progress_bar = QProgressBar()

        # ---------------- LYRICS ----------------
        self.lyrics_box = QTextEdit()
        self.lyrics_box.setPlaceholderText("Paste lyrics here...")

        # ---------------- LAYOUT ----------------
        root = QWidget()
        main = QVBoxLayout(root)

        controls = QHBoxLayout()
        controls.addWidget(self.load_btn)
        controls.addWidget(self.sync_btn)
        controls.addWidget(self.play_btn)
        controls.addWidget(self.pause_btn)

        main.addLayout(controls)
        main.addWidget(self.seek_slider)
        main.addWidget(self.table)

        lyrics_group = QGroupBox("🎤 Lyrics (Paste here)")
        lyrics_layout = QVBoxLayout(lyrics_group)
        lyrics_layout.addWidget(self.lyrics_box)
        main.addWidget(lyrics_group)

        edit_box = QHBoxLayout()
        edit_box.addWidget(self.nudge_left_btn)
        edit_box.addWidget(self.nudge_right_btn)
        edit_box.addWidget(self.split_btn)
        edit_box.addWidget(self.merge_btn)
        main.addLayout(edit_box)

        export_box = QHBoxLayout()
        export_box.addWidget(self.lrc_btn)
        export_box.addWidget(self.srt_btn)
        export_box.addWidget(self.txt_btn)
        main.addLayout(export_box)

        main.addWidget(self.progress_label)
        main.addWidget(self.progress_bar)

        self.setCentralWidget(root)

        # ---------------- SIGNALS ----------------
        self.load_btn.clicked.connect(self.load_mp4)
        self.sync_btn.clicked.connect(self.auto_sync)

        self.play_btn.clicked.connect(self.player.play)
        self.pause_btn.clicked.connect(self.player.pause)

        self.player.positionChanged.connect(self.update_slider)
        self.player.durationChanged.connect(self.set_slider_range)

        self.table.cellClicked.connect(self.jump_to_segment)

        self.nudge_left_btn.clicked.connect(lambda: self.nudge(-0.1))
        self.nudge_right_btn.clicked.connect(lambda: self.nudge(0.1))
        self.split_btn.clicked.connect(self.split_segment)
        self.merge_btn.clicked.connect(self.merge_segment)

        self.lrc_btn.clicked.connect(self.export_lrc)
        self.srt_btn.clicked.connect(self.export_srt)
        self.txt_btn.clicked.connect(self.export_txt)

    # ---------------- AUDIO LOADING ----------------
    def load_mp4(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open MP4", "", "Video Files (*.mp4)"
        )
        if path:
            self.audio_path = extract_audio(path)
            self.player.setSource(QUrl.fromLocalFile(self.audio_path))
            QMessageBox.information(self, "Loaded", "Audio extracted and ready.")

    # ---------------- AUTO SYNC ----------------
    def auto_sync(self):
        if not self.audio_path:
            QMessageBox.warning(self, "No Audio", "Load an MP4 first.")
            return

        lyrics = self.lyrics_box.toPlainText().strip()
        if not lyrics:
            QMessageBox.warning(self, "No Lyrics", "Paste lyrics before syncing.")
            return

        self.segments = []
        self.progress_bar.setValue(0)
        self.progress_label.setText("Running AI alignment...")

        # Setup QThread worker
        self.thread = QThread()
        self.worker = AlignWorker(self.audio_path, lyrics)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.on_alignment_progress)
        self.worker.finished.connect(self.on_alignment_done)
        self.worker.error.connect(self.on_alignment_error)

        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def on_alignment_progress(self, partial):
        self.segments = partial
        self.populate_table()
        self.progress_bar.setValue(min(len(partial) * 5, 95))

    def on_alignment_done(self, segments):
        self.segments = segments
        self.populate_table()
        self.progress_bar.setValue(100)
        self.progress_label.setText("Completed")

    def on_alignment_error(self, msg):
        QMessageBox.critical(self, "Auto Sync Error", msg)
        self.progress_label.setText("Failed")

    # ---------------- TABLE & AUDIO ----------------
    def populate_table(self):
        self.table.setRowCount(0)
        for s in self.segments:
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(f"{s['start']:.2f}"))
            self.table.setItem(r, 1, QTableWidgetItem(f"{s['end']:.2f}"))
            self.table.setItem(r, 2, QTableWidgetItem(s["text"]))

    def set_slider_range(self, dur):
        self.seek_slider.setRange(0, dur)

    def update_slider(self, pos):
        self.seek_slider.blockSignals(True)
        self.seek_slider.setValue(pos)
        self.seek_slider.blockSignals(False)

    def seek_audio(self):
        self.player.setPosition(self.seek_slider.value())

    def jump_to_segment(self, row, _):
        t = int(float(self.table.item(row, 0).text()) * 1000)
        self.player.setPosition(t)

    # ---------------- EDIT FUNCTIONS ----------------
    def nudge(self, delta):
        row = self.table.currentRow()
        if row < 0:
            return
        self.segments[row]["start"] += delta
        self.segments[row]["end"] += delta
        self.populate_table()
        self.table.selectRow(row)

    def split_segment(self):
        row = self.table.currentRow()
        if row < 0:
            return
        seg = self.segments[row]
        mid = (seg["start"] + seg["end"]) / 2
        left = dict(seg)
        right = dict(seg)
        left["end"] = mid
        right["start"] = mid
        self.segments[row] = left
        self.segments.insert(row + 1, right)
        self.populate_table()

    def merge_segment(self):
        row = self.table.currentRow()
        if row < 0 or row >= len(self.segments) - 1:
            return
        a = self.segments[row]
        b = self.segments[row + 1]
        merged = {
            "start": a["start"],
            "end": b["end"],
            "text": a["text"] + " " + b["text"]
        }
        self.segments[row] = merged
        del self.segments[row + 1]
        self.populate_table()

    # ---------------- EXPORT ----------------
    def export_lrc(self):
        if self.segments:
            path, _ = QFileDialog.getSaveFileName(self, "Save LRC", "", "*.lrc")
            save_lrc(self.segments, path)

    def export_srt(self):
        if self.segments:
            path, _ = QFileDialog.getSaveFileName(self, "Save SRT", "", "*.srt")
            save_srt(self.segments, path)

    def export_txt(self):
        if self.segments:
            path, _ = QFileDialog.getSaveFileName(self, "Save TXT", "", "*.txt")
            save_txt(self.segments, path)