# Lighting Extraction Tool for Katana

## What this project is
A tool that ingests an **image sequence** of a real scene, analyses it, and produces a
**starting-point light rig** inside Katana: the actual physical lights placed in 3D with
colour, direction, type and a rough intensity.

**Philosophy:** the output is a *starting point*, not a perfect result. The artist refines
final values in Katana. The tool removes the boring blocking work, not the artistry.

## Architecture — three decoupled blocks
1. **Analysis** (the "brain") — runs externally, produces a USD file + JSON sidecar.
   - `track/` — camera poses + dense scene geometry.
   - `detect/` — find & segment the actual light sources across frames.
   - `fuse/` — **our own code**: triangulate masks to 3D, reject reflections (cross-view
     consistency), classify light type. This is the novel work, not a library.
   - `export/` — write USDLux lights + JSON.
2. **Validation** — a desktop UI where the artist confirms detections (keep / delete /
   reclassify, confirm source-vs-reflection, type, rough position). NOT for tweaking
   intensity/colour (that's done in Katana). Reads the brain's USD + JSON output.
3. **Katana translation** — import the validated USD and build the rig.

**Contract between blocks is USD.** Each block is independent and communicates via files.

## Tools to use (all verified commercial-safe — do not substitute without checking licence)
- **3D track:** COLMAP (new BSD). Call it as an **external executable** (subprocess), not
  static-linked, to avoid GPL optional dependencies.
- **AI light detection:** Grounded SAM 2 = Grounding DINO + SAM 2 (both Apache 2.0).
- **Fusion:** our own code; lean on NumPy and OpenCV for the triangulation maths.
- **Validation UI:** PySide6 (Qt for Python, LGPL). Same Qt as Katana/Nuke/Maya.
- **Katana:** import with `UsdIn`, manage with `GafferThree`, lights as USDLux
  (`SphereLight` = bulb, `RectLight` = panel, `DistantLight` = hard key/sun).
- **DO NOT USE:** DUSt3R / MASt3R (non-commercial CC BY-NC-SA — unusable in a studio).
- **DO NOT USE on the Katana side:** `UsdEngineWrite` / `UsdExport` / `KatanaToUsd`
  (those are the export direction, Katana -> USD; we go USD -> Katana).

## Repository structure (one monorepo)
```
lighting-tool/
├── brain/          # analysis package (Python)
│   ├── track/      # COLMAP wrapper
│   ├── detect/     # Grounded SAM 2 wrapper
│   ├── fuse/       # triangulation + reflection rejection (our code)
│   └── export/     # writes USDLux .usd + JSON sidecar
├── validation/     # PySide6 review app
├── katana/         # Katana Python tool (deploys to Katana resource path)
└── docs/           # design.md / design.html (full rationale + diagrams)
```

## Conventions & decisions
- **Language:** Python everywhere. **IDE:** VS Code. No Visual Studio (no C++ in this design).
- **One repository**, not several. `brain/`, `validation/`, `katana/` are folders/packages
  inside it, not separate repos. No shared library yet — only extract one if reuse demands it.
- **Validation** is the same repo, loosely coupled: it reads the brain's USD + JSON output.
- **Katana tool:** build a plain **Python menu/shelf tool** now. A **SuperTool only later**,
  if a polished self-contained custom node is wanted.
- **Reflection rejection** relies on the 3D track: a real emitter triangulates to a stable
  3D point across views; a reflection does not. Use this to auto-cull false positives.

## Open questions (NOT yet decided — ask before assuming)
- **Target renderer(s)** in Katana — decide first; drives USDLux -> light-shader mapping.
- **Intensity / HDR recovery** — deferred to v2; seed a rough value for now.
- **Dome / environment** light — deferred; plan is discrete lights only for now.
- **Scale** — SfM is up to unknown scale; auto metric cue vs artist-set, undecided.
- **Land lights as raw `UsdIn`, or wrap into `GafferThree` on import** — undecided.

## Full design
See @docs/design.md for the complete rationale, tables, and diagrams.
