# Frosted Glass Skull

A transparent frosted-glass skull that really refracts what sits behind it, in two forms:

| File | What it is |
|---|---|
| `index.html` | Live Three.js scene you can rotate. A real skull mesh is rendered with `MeshPhysicalMaterial` transmission, so the grey grid and the large blackletter letters behind it are bent, blurred and colour-split through the glass. You can load your own `.glb`. |
| `frosted_glass_material.py` | Blender 4.2+ script that builds the same glass in Cycles and, optionally, a grey backdrop with big black letters for it to refract. |
| `assets/skull.bin` | Packed skull mesh (from `assets/convert_skull.py`). |
| `src/template.html` | Page source. Run `python3 build.py` to embed the Blender script and the mesh into `index.html`. |

No colour is painted on the surface. The dark shapes inside the glass are the
backdrop letters seen through it.

## Glass recipe

| Property | Three.js | Blender (Principled BSDF) |
|---|---|---|
| Transparency | `transmission` 0.9 | Transmission Weight 1.0 |
| Frost (blur of what is refracted) | `roughness` 0.22 | Roughness 0.28 |
| Refraction | `ior` 1.55, `thickness` 2.4 | IOR 1.5 (real geometry thickness in Cycles) |
| Colour fringes | `dispersion` 3.5 | Dispersion 0.08 |
| Holographic sheen | `iridescence` 0.55, lavender `sheen` | Thin Film 380 nm, IOR 1.35, Sheen |
| Milky scatter | transmission < 1 ("Milkiness") | Subsurface Weight 0.1 |
| Grain | post pass | 128 samples, denoising off |

## Credits

Skull mesh: "skull" from [Babylon.js Assets](https://github.com/BabylonJS/Assets)
(`meshes/skull.babylon`), licensed [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
`convert_skull.py` mirrors it into a right-handed frame, applies light Taubin
smoothing, recomputes normals and quantises it.
