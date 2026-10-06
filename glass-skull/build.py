"""Embed frosted_glass_material.py into the page: python3 build.py"""
import html, pathlib
here = pathlib.Path(__file__).parent
page = (here / "src/template.html").read_text()
py = (here / "frosted_glass_material.py").read_text()
(here / "index.html").write_text(page.replace("__BLENDER_PY__", html.escape(py)))
print("wrote index.html")
