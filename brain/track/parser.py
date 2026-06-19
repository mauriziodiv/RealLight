import json
import numpy as np
from pathlib import Path


def _parse_cameras(cameras_txt: Path) -> dict[int, dict]:
    cameras = {}
    with cameras_txt.open() as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            cam_id = int(parts[0])
            model = parts[1]
            # width = int(parts[2])  # unused for now
            # height = int(parts[3])
            params = [float(p) for p in parts[4:]]

            # SIMPLE_RADIAL / PINHOLE / SIMPLE_PINHOLE all have f, cx, cy as first params
            cameras[cam_id] = {
                "model": model,
                "f": params[0],
                "cx": params[1],
                "cy": params[2],
            }
    return cameras


def _parse_images(images_txt: Path, cameras: dict[int, dict]) -> list[dict]:
    images = []
    with images_txt.open() as f:
        lines = [l.strip() for l in f if l.strip() and not l.startswith("#")]

    # images.txt has pairs of lines: pose line, then keypoints line
    for i in range(0, len(lines), 2):
        parts = lines[i].split()
        # IMAGE_ID QW QX QY QZ TX TY TZ CAMERA_ID NAME
        qw, qx, qy, qz = float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])
        tx, ty, tz = float(parts[5]), float(parts[6]), float(parts[7])
        cam_id = int(parts[8])
        name = parts[9]

        R = _quat_to_rotation(qw, qx, qy, qz)
        cam = cameras.get(cam_id, {})
        images.append({
            "name": name,
            "R": R.tolist(),
            "t": [tx, ty, tz],
            "f": cam.get("f"),
            "cx": cam.get("cx"),
            "cy": cam.get("cy"),
        })

    return sorted(images, key=lambda x: x["name"])


def _quat_to_rotation(qw: float, qx: float, qy: float, qz: float) -> np.ndarray:
    # COLMAP quaternion convention: (w, x, y, z) for world-to-camera rotation
    R = np.array([
        [1 - 2*qy**2 - 2*qz**2,     2*qx*qy - 2*qz*qw,     2*qx*qz + 2*qy*qw],
        [    2*qx*qy + 2*qz*qw, 1 - 2*qx**2 - 2*qz**2,     2*qy*qz - 2*qx*qw],
        [    2*qx*qz - 2*qy*qw,     2*qy*qz + 2*qx*qw, 1 - 2*qx**2 - 2*qy**2],
    ])
    return R


def parse_and_write(model_dir: Path, output_dir: Path) -> Path:
    cameras = _parse_cameras(model_dir / "cameras.txt")
    images = _parse_images(model_dir / "images.txt", cameras)

    out_path = output_dir / "cameras.json"
    with out_path.open("w") as f:
        json.dump({"images": images}, f, indent=2)

    return out_path
