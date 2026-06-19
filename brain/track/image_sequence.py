from pathlib import Path

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".exr"}
MIN_IMAGES = 5


def load_sequence(images_dir: str) -> list[Path]:
    """
    Validates images_dir and returns a sorted list of image paths.
    Raises ValueError if the folder is missing or has too few images.
    """
    folder = Path(images_dir)

    if not folder.exists():
        raise ValueError(f"Images folder does not exist: {folder}")
    if not folder.is_dir():
        raise ValueError(f"Not a directory: {folder}")

    images = sorted(
        p for p in folder.iterdir()
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
    )

    if len(images) < MIN_IMAGES:
        raise ValueError(
            f"Found only {len(images)} image(s) in '{folder}'. "
            f"COLMAP needs at least {MIN_IMAGES} overlapping images for a useful reconstruction."
        )

    return images
