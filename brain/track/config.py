import os
import shutil


def colmap_bin() -> str:
    path = os.environ.get("COLMAP_BIN", "colmap")
    if not shutil.which(path):
        raise EnvironmentError(
            f"COLMAP not found at '{path}'. "
            "Install it from https://github.com/colmap/colmap/releases and either "
            "add it to PATH or set the COLMAP_BIN environment variable to its full path."
        )
    return path
