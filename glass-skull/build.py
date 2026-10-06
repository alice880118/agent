"""Build index.html: embeds the Blender script and the packed skull mesh.

    python3 build.py
"""
import base64, html, pathlib
here = pathlib.Path(__file__).parent
page = (here / "src/template.html").read_text()
py = (here / "frosted_glass_material.py").read_text()
skull = base64.b64encode((here / "assets/skull.bin").read_bytes()).decode()
page = page.replace("__BLENDER_PY__", html.escape(py)).replace("__SKULL_B64__", skull)
(here / "index.html").write_text(page)
print(f"wrote index.html ({len(page) / 1e6:.2f} MB)")
