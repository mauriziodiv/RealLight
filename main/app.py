import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "modules"))
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
from PySide6.QtWidgets import QFileDialog
from brain.track.image_sequence import load_sequence
from PySide6.QtGui import QPixmap, Qt
from PySide6.QtCore import QTimer
from modules.analysis import AnalysisThread

class RealLightApp(QMainWindow):
    def __init__(self):
        super().__init__()

        loader = QUiLoader()
        ui_file = QFile("UI/mainwindow.ui")
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file)
        ui_file.close()
        self.setCentralWidget(self.ui)
        self.resize(1021, 773)
        self.ui.show()

        self.ui.compute.clicked.connect(self.compute)

        self.ui.compute_progress_bar.setVisible(False)
        self.ui.compute_progress_bar.setValue(0)

        self.current_frame = 0

        self.is_playing = False

        self.timer = QTimer()
        self.timer.setInterval(42)
        #self.timer.timeout.connect(self.next_frame)
        #self.timer.timeout.connect(self.previous_frame)

        self.ui.load_footage.clicked.connect(self.load_footage)
        self.ui.frame_scrubber.valueChanged.connect(self.update_frame)

        self.ui.play_forward.clicked.connect(self.next_frame_timer_connect)
        self.ui.play_forward.clicked.connect(self.timer.start)
        self.ui.play_forward.clicked.connect(self.update_playing_state)
        self.ui.play_forward.clicked.connect(self.next_frame)

        self.ui.play_backwards.clicked.connect(self.previous_frame_timer_connect)
        self.ui.play_backwards.clicked.connect(self.timer.start)
        self.ui.play_backwards.clicked.connect(self.update_playing_state)
        self.ui.play_backwards.clicked.connect(self.previous_frame)

    def show_frame(self, frame_index):
        pixmap = QPixmap(str(self.images[frame_index]))
        self.ui.frame_viewer.setPixmap(pixmap.scaled(self.ui.frame_viewer.size(),Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.ui.frame_counter.setText(f"Frame: {frame_index + 1}/{len(self.images)}")

    def load_footage(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Footage Folder")
        if folder:
            self.ui.footage_path.setText(folder)

            self.images = load_sequence(folder)

            if self.images:
                self.ui.frame_scrubber.setMinimum(0)
                self.ui.frame_scrubber.setMaximum(len(self.images) - 1)
                self.ui.frame_scrubber.setValue(0)
                self.ui.frame_counter.setText(f"Frame: {self.current_frame + 1}/{len(self.images)}")
                self.show_frame(0)

    def update_frame(self, frame_index):
        self.current_frame = frame_index
        self.show_frame(frame_index)

    def update_playing_state(self):
        self.is_playing = not self.is_playing

    def next_frame_timer_connect(self):
        if self.timer.isActive():
            self.timer.timeout.disconnect()

        self.timer.timeout.connect(self.next_frame)

    def previous_frame_timer_connect(self):
        if self.timer.isActive():
            self.timer.timeout.disconnect()

        self.timer.timeout.connect(self.previous_frame)

    def next_frame(self):
        if self.is_playing:
            if self.current_frame < len(self.images) - 1:
                self.current_frame += 1
                self.ui.frame_scrubber.setValue(self.current_frame)
            else:
                self.timer.stop()

    def previous_frame(self):
        if self.is_playing:
            if self.current_frame > 0:
                self.current_frame -= 1
                self.ui.frame_scrubber.setValue(self.current_frame)
            else:
                self.timer.stop()

    def compute(self):
        if not hasattr(self, 'images'):
            self.statusBar().showMessage("No footage loaded. Please load footage before computing.")
            return
        
        output_dir = str(Path(self.ui.footage_path.text()).parent / "output")
        self.worker = AnalysisThread(self.ui.footage_path.text(), output_dir)
        self.worker.finished.connect(self.on_analysis_finished)
        self.worker.error.connect(self.on_analysis_error)
        self.worker.start()

        self.ui.compute.setEnabled(False)
        self.ui.load_footage.setEnabled(False)
        self.ui.compute_progress_bar.setVisible(True)
        self.ui.compute_progress_bar.setRange(0, 0)
        self.statusBar().showMessage("Computing...")

    def on_analysis_finished(self, result):
        self.ui.load_footage.setEnabled(True)
        self.ui.compute_progress_bar.setVisible(False)
        self.ui.compute.setEnabled(True)
        self.statusBar().showMessage(f"Analysis finished: {result}")

    def on_analysis_error(self, error_message):
        self.ui.load_footage.setEnabled(True)
        self.ui.compute_progress_bar.setVisible(False)
        self.ui.compute.setEnabled(True)
        self.statusBar().showMessage(f"Error during analysis: {error_message}")

def main():
    app = QApplication(sys.argv)
    window = RealLightApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()