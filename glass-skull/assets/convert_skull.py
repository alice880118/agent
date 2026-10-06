"""Pack BabylonJS skull.babylon (CC BY 4.0) into a compact binary for the page.

Seam vertices are welded so the surface is closed, then it is lightly Taubin-smoothed (volume-preserving) so the glass
reads as polished rather than lumpy, and normals are recomputed.

Layout (little endian):
  uint32 vertexCount, uint32 triangleCount, float32 reserved
  int16  positions[vertexCount*3]   (value / 32767, centred, fits [-1, 1])
  int8   normals[vertexCount*3]     (value / 127), then pad to 2 bytes
  uint16 indices[triangleCount*3]
Babylon is left-handed, so z is negated (which also fixes the winding).

Usage: python3 convert_skull.py skull.babylon skull.bin [iterations]
"""
import json, struct, sys
import numpy as np

src, dst = sys.argv[1], sys.argv[2]
iters = int(sys.argv[3]) if len(sys.argv) > 3 else 12
m = json.load(open(src))["meshes"][0]
P = np.array(m["positions"], dtype=np.float64).reshape(-1, 3)
F = np.array(m["indices"], dtype=np.int64).reshape(-1, 3)
P[:, 2] *= -1

# The scan stores duplicate vertices along its UV seams. Weld them first:
# smoothing unwelded copies separately would pull the seams open into cracks.
_, first, inv = np.unique(np.round(P, 5), axis=0, return_index=True, return_inverse=True)
inv = inv.reshape(-1)
P = P[first]
F = inv[F]
F = F[(F[:, 0] != F[:, 1]) & (F[:, 1] != F[:, 2]) & (F[:, 2] != F[:, 0])]
# Negating z mirrors the mesh, which already turns Babylon's clockwise fronts
# into three.js counter-clockwise fronts, so the index order stays as is.

# Uniform-weight adjacency as a sparse average via edge lists.
E = np.concatenate([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]])
E = np.unique(np.sort(E, axis=1), axis=0)
deg = np.bincount(E.ravel(), minlength=len(P)).astype(np.float64)[:, None]

def laplacian(X):
    acc = np.zeros_like(X)
    np.add.at(acc, E[:, 0], X[E[:, 1]])
    np.add.at(acc, E[:, 1], X[E[:, 0]])
    return acc / np.maximum(deg, 1) - X

for _ in range(iters):                      # Taubin: shrink then inflate
    P += 0.5 * laplacian(P)
    P += -0.53 * laplacian(P)

fn = np.cross(P[F[:, 1]] - P[F[:, 0]], P[F[:, 2]] - P[F[:, 0]])
N = np.zeros_like(P)
for k in range(3):
    np.add.at(N, F[:, k], fn)
N /= np.maximum(np.linalg.norm(N, axis=1, keepdims=True), 1e-12)

P -= (P.min(0) + P.max(0)) / 2
P /= np.abs(P).max()

out = bytearray(struct.pack("<IIf", len(P), len(F), 1.0))
out += np.round(P * 32767).astype("<i2").tobytes()
out += np.clip(np.round(N * 127), -127, 127).astype("i1").tobytes()
if len(out) % 2:
    out += b"\0"
out += F.astype("<u2").tobytes()
open(dst, "wb").write(out)
print(len(P), "verts", len(F), "tris", len(out), "bytes")
