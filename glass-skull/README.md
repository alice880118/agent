# Frosted Glass Skull

A milky frosted-glass material with holographic edges, in two forms:

| File | What it is |
|---|---|
| `index.html` | Live Three.js scene you can rotate. It builds a procedural skull from a signed distance field (marching cubes), renders it with the glass material, and adds a chromatic-fringe and grain post pass, a blackletter and grid backdrop, and HUD callouts. You can load your own `.glb`. |
| `frosted_glass_material.py` | Blender 4.2+ script that rebuilds the same material in Cycles and assigns it to the selected meshes. |
| `src/template.html` | Page source. Run `python3 build.py` to embed the Blender script and write `index.html`. |

## Material recipe

| Layer | Three.js | Blender |
|---|---|---|
| Frosted body | `MeshPhysicalMaterial` with transmission 0.82, roughness 0.45, ior 1.38 | Principled BSDF with Transmission 0.92, Roughness 0.42, IOR 1.45 |
| Ink voids | Per-vertex cavity (SDF ambient-occlusion probe, or Laplacian curvature for an imported mesh) plus object-space fbm noise, thresholded with screen-space dither | Ambient Occlusion node plus Noise and White Noise, through a Color Ramp (milk → cyan → navy → black) |
| Holographic sheen | `iridescence` 0.6 plus a lavender `sheen` | Thin Film thickness 420 nm, IOR 1.6, plus Sheen |
| Violet rim | Fresnel emission added in `onBeforeCompile` | Layer Weight (Facing) driving Emission Strength |
| Depth | `attenuationColor` / `attenuationDistance` | Volume Absorption |
| Chromatic fringe | Post pass: radial RGB split plus a violet/cyan edge glow | Compositor Lens Distortion with Dispersion 0.035 |
| Grain | Animated hash noise in the post pass, stronger in shadows | Cycles at 96 samples with denoising off |
