import argparse
from . import run

parser = argparse.ArgumentParser(description="RealLight — COLMAP sparse reconstruction")
parser.add_argument("--images", required=True, help="Path to folder of input images")
parser.add_argument("--out", required=True, help="Path to output working directory")
parser.add_argument(
    "--matcher",
    choices=["sequential", "exhaustive"],
    default="sequential",
    help="Feature matcher (sequential for video frames, exhaustive for unordered sets)",
)
args = parser.parse_args()
run(args.images, args.out, args.matcher)
