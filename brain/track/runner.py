import subprocess
from pathlib import Path


def _run(args: list[str]) -> None:
    process = subprocess.Popen(
        args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )
    for line in process.stdout:
        print(line, end="", flush=True)
    process.wait()
    if process.returncode != 0:
        raise RuntimeError(f"COLMAP command failed: {' '.join(args)}")


def extract_features(bin: str, db: Path, images: Path) -> None:
    _run([
        bin, "feature_extractor",
        "--database_path", str(db),
        "--image_path", str(images),
        "--ImageReader.single_camera", "1",
    ])


def match_features(bin: str, db: Path, matcher: str = "sequential") -> None:
    command = "sequential_matcher" if matcher == "sequential" else "exhaustive_matcher"
    _run([bin, command, "--database_path", str(db)])


def reconstruct(bin: str, db: Path, images: Path, sparse_out: Path) -> None:
    sparse_out.mkdir(parents=True, exist_ok=True)
    _run([
        bin, "mapper",
        "--database_path", str(db),
        "--image_path", str(images),
        "--output_path", str(sparse_out),
        "--Mapper.ba_global_function_tolerance", "0.000001",
    ])

    model_dir = sparse_out / "0"
    if not model_dir.exists() or not any(model_dir.iterdir()):
        raise RuntimeError(
            "COLMAP reconstruction produced no output in sparse/0/. "
            "The image set may have too few overlapping views or insufficient texture."
        )

    # Convert binary model to readable text format
    _run([
        bin, "model_converter",
        "--input_path", str(model_dir),
        "--output_path", str(model_dir),
        "--output_type", "TXT",
    ])
