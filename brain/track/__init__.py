from pathlib import Path

from .config import colmap_bin
from .image_sequence import load_sequence
from .runner import extract_features, match_features, reconstruct
from .parser import parse_and_write


def run(images_dir: str, output_dir: str, matcher: str = "sequential") -> str:
    """
    Runs the COLMAP sparse pipeline on images_dir.
    Returns the path to cameras.json written inside output_dir.

    matcher: "sequential" (ordered video frames) or "exhaustive" (unordered photo sets)
    """
    images_list = load_sequence(images_dir)
    print(f"[track] Found {len(images_list)} images in {images_dir}")

    images = Path(images_dir)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    colmap_exe = colmap_bin()
    db = out / "database.db"
    sparse_out = out / "sparse"

    print(f"[track] Feature extraction ...")
    extract_features(colmap_exe, db, images)

    print(f"[track] Feature matching ({matcher}) ...")
    match_features(colmap_exe, db, matcher)

    print(f"[track] Sparse reconstruction ...")
    reconstruct(colmap_exe, db, images, sparse_out)

    print(f"[track] Parsing results ...")
    cameras_json = parse_and_write(sparse_out / "0", out)

    print(f"[track] Done. Camera poses written to: {cameras_json}")
    return str(cameras_json)
