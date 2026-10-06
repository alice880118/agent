# Frosted Glass Skull

A transparent frosted-glass skull that really refracts what sits behind it, in two forms:

| File | What it is |
|---|---|
| `index.html` | Live Three.js scene you can rotate. A custom shader traces light through a real skull mesh: refraction in and out with Snell's law, real thickness from a back-face depth pass, dispersion per colour channel, Fresnel reflection, total internal reflection, Beer–Lambert absorption, and frosted (rough-surface) scattering. The grid and blackletter backdrop is what you see refracted. You can load your own `.glb`. |
| `frosted_glass_material.py` | Blender 4.2+ script that builds the same glass in Cycles and, optionally, a grey backdrop with big black letters for it to refract. |
| `assets/skull.bin` | Packed skull mesh (from `assets/convert_skull.py`). |
| `src/template.html` | Page source. Run `python3 build.py` to embed the Blender script and the mesh into `index.html`. |

No colour is painted on the surface. Everything inside the glass is the
backdrop seen through it.

## How the glass is traced (index.html)

1. **Back-face pass.** The mesh's back faces are drawn into a float target that stores the view-space normal and depth where light leaves the glass.
2. **Entry.** At each front-face pixel the view ray refracts with Snell's law (n = IOR). Frost tilts the surface normal inside a cone set by roughness, like a sandblasted surface, using 5 samples per pixel.
3. **Through the volume.** The refracted ray is ray-marched in screen space against the back-face depth to find where it exits, which gives the real path length.
4. **Exit.** The ray refracts again at the rough back surface, once per R, G and B, using indices from the Abbe number (n_C, n_d, n_F). Past the critical angle it reflects internally.
5. **Background.** The exit ray is intersected exactly with the backdrop plane. The texture is sampled with a mip level that grows with distance, so frosted glass blurs far things more than near ones.
6. **Energy.** Schlick Fresnel at both surfaces, thin-film interference on the reflection, Beer–Lambert absorption, and in-scattering, all along the path length.

**Known approximations:** only the first exit surface is found (rays that leave the glass and re-enter it are not followed), the studio light is procedural, and the backdrop is a single plane.

## Blender

`frosted_glass_material.py` builds the material for Cycles, which path-traces it fully: all bounces, rough transmission, dispersion and thin film.

## Credits

Skull mesh: "skull" from [Babylon.js Assets](https://github.com/BabylonJS/Assets)
(`meshes/skull.babylon`), licensed [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
`convert_skull.py` mirrors it into a right-handed frame, applies light Taubin
smoothing, recomputes normals and quantises it.
