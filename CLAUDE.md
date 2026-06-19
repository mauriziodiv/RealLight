# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## What this project is

**RealLight** ingests an image sequence of a real scene, analyses it, and produces a starting-point USDLux light rig inside Katana — physical lights placed in 3D with colour, direction, and type. The artist refines values in Katana; the tool removes the blocking work, not the artistry.

---

## Architecture — three decoupled blocks

```
image sequence
      │
  ┌───▼──────────────────────────────────┐
  │  BLOCK 1 · brain/  (runs standalone) │
  │  track/   → COLMAP (subprocess)      │
  │  detect/  → Grounded SAM 2           │
  │  fuse/    → our code (novel work)    │
  │  export/  → USDLux .usd + JSON       │
  └───────────────────┬──────────────────┘
                      │  USD + JSON sidecar
  ┌───────────────────▼──────────────────┐
  │  BLOCK 2 · validation/  (PySide6)    │
  │  artist: keep / delete / reclassify  │
  └───────────────────┬──────────────────┘
                      │  validated USD
  ┌───────────────────▼──────────────────┐
  │  BLOCK 3 · katana/  (Python tool)    │
  │  UsdIn → GafferThree                 │
  └──────────────────────────────────────┘
```

**Contract between blocks is USD files on disk.** Each block is independent. Never couple them in memory or via direct imports across block boundaries.

---

## Key decisions (settled)

| Question | Decision |
|---|---|
| Target renderer | **None — pure USDLux output.** Renderer-agnostic; artist handles shader mapping in Katana. |
| Katana tool type | Python menu/shelf tool now. SuperTool only later if needed. |
| Intensity / HDR | **Deferred to v2.** Seed a rough value; artist sets final in Katana. |
| Dome / environment light | **Deferred.** Discrete lights only for now. |
| Shared library | **No.** Only extract one if reuse actually demands it. |
| COLMAP linking | **subprocess only** — never statically link (avoids GPL optional deps). |

## Open questions (ask before assuming)

- **Scale** — SfM is up to unknown scale; auto metric cue vs artist-set, undecided.
- **GafferThree wrapping** — import lights as raw `UsdIn` or wrap into `GafferThree` on import?

---

## Tools & licences (all commercial-safe — do not substitute without checking)

| Tool | Role | Licence |
|---|---|---|
| COLMAP | 3D track (external executable) | new BSD |
| Grounding DINO + SAM 2 | AI light detection | Apache 2.0 |
| NumPy + OpenCV | Fusion maths | BSD / Apache |
| usd-core | USD read/write | Apache 2.0 |
| PySide6 | Validation UI | LGPL |

**Do NOT use:** DUSt3R / MASt3R (CC BY-NC-SA — non-commercial).  
**Do NOT use on the Katana side:** `UsdEngineWrite` / `UsdExport` / `KatanaToUsd` (those go Katana → USD; we go USD → Katana).

---

## Development setup

COLMAP must be installed as a system executable (not via pip):
- Windows: download the binary from https://github.com/colmap/colmap/releases
- Verify: `colmap help`

Python dependencies (uncomment and install as each block is built):
```
pip install torch torchvision          # detect
pip install numpy opencv-python        # fuse
pip install usd-core                   # export
pip install PySide6                    # validation
```

Grounded SAM 2 is installed from source — see its repo for instructions (Grounding DINO + SAM 2, both Apache 2.0).

---

## Running the pipeline (once implemented)

```bash
# Block 1 — analyse an image sequence
python -m brain.track   --images /path/to/frames --out /tmp/rl_work
python -m brain.detect  --images /path/to/frames --out /tmp/rl_work
python -m brain.fuse    --work /tmp/rl_work       --out /tmp/rl_work
python -m brain.export  --work /tmp/rl_work       --out /tmp/rl_out/lights.usd

# Block 2 — validate
python -m validation    --usd /tmp/rl_out/lights.usd

# Block 3 — load in Katana via the shelf tool (no CLI)
```

---

## Implementation order

1. `brain/track` — COLMAP wrapper (foundation; everything else depends on geometry)
2. `brain/detect` — Grounded SAM 2 wrapper
3. `brain/fuse` — triangulation + reflection rejection (the novel work)
4. `brain/export` — USDLux writer
5. `validation` — PySide6 review app
6. `katana` — Python shelf tool

---

## Full design rationale

See [docs/design.md](docs/design.md).
