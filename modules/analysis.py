import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from PySide6.QtCore import QThread, Signal
import brain.track as track

class AnalysisThread(QThread):

    status = Signal(str)
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, images, output_folder):
        super().__init__()
        self.images = images
        self.output_folder = output_folder

    def run(self):
        try:
            result = track.run(self.images, self.output_folder)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))