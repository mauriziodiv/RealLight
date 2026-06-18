# Lighting Extraction Tool for Katana — Design Document

> **Status:** Living draft, updated as we go.
> Items marked **`[PARKED]`** are deliberately deferred.

---

## 1. Goal & Philosophy

A tool that ingests an **image sequence** of a real scene, analyses it, and produces a
**starting-point light rig** inside Katana — the actual physical lights placed in 3D with
colour, direction, type, and a rough intensity.

**Guiding principle:** *not perfect — a strong starting point.* The artist refines the
final values in Katana. The tool removes the boring blocking work, not the artistry.

---

## 2. The Pipeline — three blocks

```
                       INPUT: image sequence
                                |
   ============================ 1 · ANALYSIS ============================
   |                                                                     |
   |    [ 3D track ]                      [ AI light detection ]         |
   |    -> COLMAP                         -> Grounded SAM 2              |
   |          \________________________________/                        |
   |                          |                                          |
   |                    [ Fusion ]                                       |
   |                    triangulate + reject reflections + classify      |
   ======================================================================
                                |
                    candidate lights  (USD + JSON)
                                |
   =========================== 2 · VALIDATION ===========================
   |                                                                     |
   |    [ Artist review UI ]  <---- artist input: keep / delete /        |
   |    -> PySide6 (Qt)                          reclassify              |
   |    confirm legit sources, cull reflections                          |
   ======================================================================
                                |
                       validated rig  (USD)
                                |
   ============================= 3 · KATANA =============================
   |                                                                     |
   |    [ Import — Python tool ]:  UsdIn  ->  GafferThree                |
   ======================================================================
                                |
                     lights in the Katana scene
```

**The contract between blocks is USD.** Analysis writes a `.usd` (USDLux lights) plus a
JSON sidecar for the UI; validation culls/confirms and writes the final `.usd`; Katana
reads it. This keeps the three blocks cleanly decoupled.

---

## 3. Block 1 — Analysis · what to use

A **hybrid pipeline**: classical geometry as the reliable backbone, a learned model for
detection. Not one end-to-end AI.

| Module | What it does | **Use** | Licence (commercial-safe?) |
|---|---|---|---|
| **3D track** | Camera poses + dense scene geometry (turns a 2D bright blob into a 3D position). | **COLMAP** | new BSD — **yes** |
| **AI light detection** | Find & segment the actual light sources across the sequence, temporally consistent. | **Grounded SAM 2** (Grounding DINO + SAM 2) | Apache 2.0 — **yes** |
| **Fusion** | Triangulate masks to 3D; reject reflections by cross-view consistency; classify type. | Your own code | — |

- **Reflection rejection:** a real emitter triangulates to a stable 3D point across views;
  a reflection doesn't — so the 3D track auto-culls most false positives before the artist sees them.
- **Avoid:** DUSt3R / MASt3R — non-commercial (CC BY-NC-SA 4.0). Not usable in a studio pipeline.
- **Intensity / HDR:** `[PARKED]` for v1 — colour is reliable now; true intensity from saturated
  footage is fragile, so seed a rough value and let the artist set it in Katana.

---

## 4. Block 2 — Validation · what to use

**Not** about tweaking values (intensity/colour are easy in Katana). It's about confirming
the analysis is **structurally correct** before committing.

- **Use:** **PySide6** (Qt for Python) — LGPL, commercial-safe. Same Qt as Katana/Nuke/Maya.
- **Needs:** show the plate, overlay detected lights, simple click-to **keep / delete / reclassify**,
  optional position nudge and a lightweight 3D preview.
- **Artist confirms:** legit source vs. reflection, light type, rough position. **Not** intensity.

---

## 5. Block 3 — Katana · what to use

The validated `.usd` becomes real lights. **Decide the target renderer(s) on day one** —
light shaders differ per renderer.

- **Import:** **UsdIn**
- **Light types:** **USDLux** — `SphereLight` (bulb), `RectLight` (panel), `DistantLight` (hard key/sun), etc.
- **Manage / make editable:** **GafferThree** (gives the artist mute/solo, linking, the full UI).
- **How to build it:** a plain **Python menu/shelf tool** now. A **SuperTool only later**, if you
  want a polished self-contained custom node.
- **Avoid:** `UsdEngineWrite` / `UsdExport` / `KatanaToUsd` — those are the export side (Katana -> USD).

---

## 6. Dome / Environment — `[PARKED]`

Plan: express everything as discrete lights. Caveat — soft/sky/ambient light isn't cleanly
reducible to a few point lights; a `DomeLight` from the residual environment is the honest
model for those cases. Revisit on an outdoor/sky scene.

---

## 7. Project / repository structure

**One repository (monorepo). Python throughout. VS Code.** (Full Visual Studio is only for
C++, which this design avoids.)

```
lighting-tool/                 # one repo, one analysis project
├── brain/                     # analysis package (Python)
│   ├── track/                 # COLMAP wrapper
│   ├── detect/                # Grounded SAM 2 wrapper
│   ├── fuse/                  # triangulation + reflection rejection
│   └── export/                # writes USDLux .usd + JSON sidecar
├── validation/                # PySide6 review app
└── katana/                    # Katana Python tool (deploys to Katana resource path)
```

**Decisions:**

| Question | Decision |
|---|---|
| Analysis: one solution or two linked? | **One project**, track + detect + fuse + export as **modules**. No separate solutions, no shared library yet. |
| Need a shared library? | **No** — only factor one out later if a piece needs reuse elsewhere. |
| Validation: independent or linked? | **Same repo**, separate app folder. Linked loosely — it reads the brain's `USD + JSON` output. |
| Katana: SuperTool or not? | **Python menu/shelf tool** now. SuperTool only later if you want a productized custom node. |
| Language / IDE | **Python + VS Code** everywhere. No Visual Studio needed. |

**Licence summary (all commercial-safe):**

| Tool | Licence |
|---|---|
| COLMAP | new BSD |
| Grounding DINO + SAM 2 (Grounded SAM 2) | Apache 2.0 |
| PySide6 (Qt for Python) | LGPL |
| USD / USDLux, Katana plug-ins | bundled with Katana |

> Note on COLMAP: call it as an **external executable** (subprocess) rather than statically
> linking, to stay clear of any GPL-licensed optional dependencies in a custom build.

---

## 8. Open Questions / To Refine

- [ ] **Target renderer(s)** in Katana — drives USDLux -> light-shader behaviour. *Decide first.*
- [ ] **Intensity / HDR** — defer to v2, or attempt recovery in v1?
- [ ] **Dome / environment** strategy (§6).
- [ ] **Scale** — auto metric cue, or always artist-set?
- [ ] **Land lights as raw UsdIn, or wrap into GafferThree on import?**

---

## 9. One-line summary

> The novel work is the **fusion logic + the Katana tool**. Track, detection and segmentation
> are off-the-shelf, free, commercial-safe components — you're integrating, not inventing.
