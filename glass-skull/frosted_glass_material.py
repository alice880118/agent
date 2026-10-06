"""
Frosted Holo Glass - Blender material setup
===========================================

Recreates the milky frosted-glass look from the skull references: translucent
white glass, dark navy/black "ink" pooling in cavities with cyan bleed at the
edges, violet rim light, thin-film iridescence, chromatic fringing and grain.

Usage
-----
1. Select one or more mesh objects (e.g. a skull).
2. Open the Scripting workspace, paste this file and press Run Script.

Targets Blender 4.2+ and renders best in Cycles. Socket names changed between
versions, so every input is set through a helper that tries the known names
and skips anything that does not exist in your build.

The ink mask uses the Ambient Occlusion node (cavities) plus object-space noise,
so it adapts to any mesh. Tune the values in PARAMS below.
"""

import bpy

MAT_NAME = "Frosted Holo Glass"

# Set to False to only create/assign the material and leave your scene alone.
SETUP_RENDER = True      # Cycles, grainy samples, AgX, chromatic-fringe compositor
SETUP_STUDIO = True      # grey world, key light and violet rim light

PARAMS = {
    # Glass body
    "milk":            (0.93, 0.93, 0.96, 1.0),
    "roughness":       0.42,   # frost amount
    "ior":             1.45,
    "transmission":    0.92,
    "subsurface":      0.12,
    "coat":            0.35,
    "coat_roughness":  0.25,
    # Holographic sheen
    "thin_film_nm":    420.0,  # Blender 4.2+ thin-film iridescence
    "thin_film_ior":   1.6,
    "sheen":           0.6,
    "rim":             (0.55, 0.35, 1.0, 1.0),
    "rim_strength":    0.6,
    # Ink voids
    "ink_cyan":        (0.03, 0.35, 0.45, 1.0),
    "ink_navy":        (0.012, 0.014, 0.09, 1.0),
    "ink_black":       (0.003, 0.003, 0.008, 1.0),
    "ink_amount":      0.55,   # 0 = clear glass, 1 = heavy ink
    "ink_noise_scale": 2.2,
    "ao_distance":     0.25,   # in object units; raise for larger meshes
    "stipple":         0.12,   # dithered/grainy ink edges
    # Volume
    "absorption":      (0.85, 0.82, 1.0, 1.0),
    "absorption_density": 0.6,
}


def sock(node, *names, out=False):
    sockets = node.outputs if out else node.inputs
    for name in names:
        if name in sockets:
            return sockets[name]
    return None


def setv(node, value, *names):
    s = sock(node, *names)
    if s is not None:
        try:
            s.default_value = value
        except (TypeError, ValueError):
            pass
    return s


def math(nodes, op, a=None, b=None, loc=(0, 0)):
    n = nodes.new("ShaderNodeMath")
    n.operation = op
    n.location = loc
    if a is not None and not hasattr(a, "is_linked"):
        n.inputs[0].default_value = a
    if b is not None and not hasattr(b, "is_linked"):
        n.inputs[1].default_value = b
    return n


def build_material():
    p = PARAMS
    mat = bpy.data.materials.get(MAT_NAME) or bpy.data.materials.new(MAT_NAME)
    mat.use_nodes = True
    nt = mat.node_tree
    nodes, links = nt.nodes, nt.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputMaterial")
    out.location = (1400, 0)

    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (1000, 0)
    setv(bsdf, p["roughness"], "Roughness")
    setv(bsdf, p["ior"], "IOR")
    setv(bsdf, p["transmission"], "Transmission Weight", "Transmission")
    setv(bsdf, p["subsurface"], "Subsurface Weight", "Subsurface")
    setv(bsdf, (0.4, 0.35, 0.6), "Subsurface Radius")
    setv(bsdf, p["coat"], "Coat Weight", "Clearcoat")
    setv(bsdf, p["coat_roughness"], "Coat Roughness", "Clearcoat Roughness")
    setv(bsdf, p["sheen"], "Sheen Weight", "Sheen")
    setv(bsdf, p["rim"], "Sheen Tint")
    setv(bsdf, p["thin_film_nm"], "Thin Film Thickness")
    setv(bsdf, p["thin_film_ior"], "Thin Film IOR")
    setv(bsdf, p["rim"], "Emission Color", "Emission")
    links.new(bsdf.outputs[0], out.inputs["Surface"])

    # --- Ink mask: cavity (AO) + object-space noise + stipple -------------
    coord = nodes.new("ShaderNodeTexCoord")
    coord.location = (-1200, 200)

    noise = nodes.new("ShaderNodeTexNoise")
    noise.location = (-950, 300)
    setv(noise, p["ink_noise_scale"], "Scale")
    setv(noise, 6.0, "Detail")
    setv(noise, 0.55, "Roughness")
    setv(noise, 0.3, "Distortion")
    links.new(coord.outputs["Object"], noise.inputs["Vector"])

    ao = nodes.new("ShaderNodeAmbientOcclusion")
    ao.location = (-950, 0)
    ao.samples = 16
    setv(ao, p["ao_distance"], "Distance")

    stipple = nodes.new("ShaderNodeTexWhiteNoise")
    stipple.location = (-950, -250)
    stipple.noise_dimensions = "3D"
    scale_uv = nodes.new("ShaderNodeVectorMath")
    scale_uv.operation = "SCALE"
    scale_uv.location = (-1100, -250)
    setv(scale_uv, 400.0, "Scale")
    links.new(coord.outputs["Object"], scale_uv.inputs[0])
    links.new(scale_uv.outputs[0], stipple.inputs["Vector"])

    cavity = math(nodes, "SUBTRACT", 1.0, None, (-700, 0))
    links.new(sock(ao, "AO", out=True), cavity.inputs[1])
    cavity_w = math(nodes, "MULTIPLY", None, 1.6, (-520, 0))
    links.new(cavity.outputs[0], cavity_w.inputs[0])

    noise_c = math(nodes, "SUBTRACT", None, 0.5, (-700, 300))
    links.new(sock(noise, "Fac", out=True), noise_c.inputs[0])
    noise_w = math(nodes, "MULTIPLY", None, 1.2, (-520, 300))
    links.new(noise_c.outputs[0], noise_w.inputs[0])

    stip_c = math(nodes, "SUBTRACT", None, 0.5, (-700, -250))
    links.new(sock(stipple, "Value", out=True), stip_c.inputs[0])
    stip_w = math(nodes, "MULTIPLY", None, p["stipple"], (-520, -250))
    links.new(stip_c.outputs[0], stip_w.inputs[0])

    ink = math(nodes, "ADD", None, None, (-340, 100))
    links.new(cavity_w.outputs[0], ink.inputs[0])
    links.new(noise_w.outputs[0], ink.inputs[1])
    ink2 = math(nodes, "ADD", None, None, (-180, 0))
    links.new(ink.outputs[0], ink2.inputs[0])
    links.new(stip_w.outputs[0], ink2.inputs[1])
    ink3 = math(nodes, "ADD", None, p["ink_amount"] - 0.55, (-20, 0))
    ink3.use_clamp = True
    links.new(ink2.outputs[0], ink3.inputs[0])

    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.location = (200, 150)
    els = ramp.color_ramp.elements
    els[0].position, els[0].color = 0.0, p["milk"]
    els[1].position, els[1].color = 0.42, p["milk"]
    for pos, col in ((0.5, p["ink_cyan"]), (0.6, p["ink_navy"]), (0.85, p["ink_black"])):
        e = els.new(pos)
        e.color = col
    links.new(ink3.outputs[0], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])

    # Slightly rougher where the ink sits, like the dense sandblasted patches.
    rough = nodes.new("ShaderNodeMapRange")
    rough.location = (500, -100)
    setv(rough, p["roughness"], "To Min")
    setv(rough, min(1.0, p["roughness"] + 0.2), "To Max")
    links.new(ink3.outputs[0], rough.inputs["Value"])
    links.new(rough.outputs["Result"], bsdf.inputs["Roughness"])

    # --- Violet rim: facing -> emission strength --------------------------
    lw = nodes.new("ShaderNodeLayerWeight")
    lw.location = (300, -350)
    setv(lw, 0.35, "Blend")
    rim_pow = math(nodes, "POWER", None, 2.5, (500, -350))
    links.new(sock(lw, "Facing", out=True), rim_pow.inputs[0])
    rim_amt = math(nodes, "MULTIPLY", None, p["rim_strength"], (680, -350))
    links.new(rim_pow.outputs[0], rim_amt.inputs[0])
    em = sock(bsdf, "Emission Strength")
    if em is not None:
        links.new(rim_amt.outputs[0], em)

    # --- Volume: glass thickness reads as depth ---------------------------
    vol = nodes.new("ShaderNodeVolumeAbsorption")
    vol.location = (1000, -500)
    setv(vol, p["absorption"], "Color")
    setv(vol, p["absorption_density"], "Density")
    links.new(vol.outputs[0], out.inputs["Volume"])

    # EEVEE refraction settings (names differ across versions).
    for attr, val in (("surface_render_method", "DITHERED"),
                      ("use_raytrace_refraction", True),
                      ("use_screen_refraction", True),
                      ("blend_method", "HASHED")):
        try:
            setattr(mat, attr, val)
        except (AttributeError, TypeError):
            pass
    mat.diffuse_color = p["milk"]
    return mat


def assign(mat):
    count = 0
    for ob in bpy.context.selected_objects:
        if ob.type != "MESH":
            continue
        if ob.data.materials:
            ob.data.materials[0] = mat
        else:
            ob.data.materials.append(mat)
        count += 1
    return count


def setup_render():
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    cy = scene.cycles
    cy.samples = 96                 # low-ish on purpose: natural grain
    cy.use_denoising = False
    cy.transmission_bounces = 16
    cy.max_bounces = 16
    try:
        scene.view_settings.view_transform = "AgX"
        scene.view_settings.look = "AgX - Medium High Contrast"
    except TypeError:
        pass

    # Chromatic fringe via Lens Distortion dispersion in the compositor.
    try:
        if hasattr(scene, "compositing_node_group"):          # Blender 5.0+
            tree = scene.compositing_node_group
            if tree is None:
                tree = bpy.data.node_groups.new("Compositing", "CompositorNodeTree")
                scene.compositing_node_group = tree
        else:
            scene.use_nodes = True
            tree = scene.node_tree
        nodes = tree.nodes
        rl = next((n for n in nodes if n.bl_idname == "CompositorNodeRLayers"), None) \
            or nodes.new("CompositorNodeRLayers")
        comp = next((n for n in nodes if n.bl_idname in
                     ("CompositorNodeComposite", "NodeGroupOutput")), None)
        lens = nodes.new("CompositorNodeLensdist")
        lens.location = (rl.location.x + 300, rl.location.y)
        setv(lens, 0.035, "Dispersion")
        setv(lens, -0.01, "Distortion", "Distort")
        tree.links.new(rl.outputs["Image"], lens.inputs["Image"])
        if comp is not None:
            tree.links.new(lens.outputs["Image"], comp.inputs[0])
    except Exception as exc:  # compositor API differs; material still works
        print(f"[{MAT_NAME}] compositor skipped: {exc}")


def setup_studio():
    scene = bpy.context.scene
    world = scene.world or bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        setv(bg, (0.78, 0.78, 0.8, 1.0), "Color")
        setv(bg, 0.8, "Strength")

    def area(name, loc, rot, energy, color, size):
        light = bpy.data.objects.get(name)
        if light is None:
            data = bpy.data.lights.new(name, "AREA")
            light = bpy.data.objects.new(name, data)
            scene.collection.objects.link(light)
        light.location, light.rotation_euler = loc, rot
        light.data.energy, light.data.color, light.data.size = energy, color, size

    area("FHG_Key", (-3.0, -3.0, 4.0), (0.8, 0.0, -0.8), 600, (1.0, 0.98, 0.96), 3.0)
    area("FHG_Rim", (2.5, 3.5, 1.5), (-1.3, 0.0, 2.6), 900, (0.6, 0.4, 1.0), 2.0)
    area("FHG_Fill", (3.5, -2.0, 0.5), (1.4, 0.0, 1.0), 200, (0.7, 0.85, 1.0), 4.0)


def main():
    mat = build_material()
    n = assign(mat)
    if SETUP_RENDER:
        setup_render()
    if SETUP_STUDIO:
        setup_studio()
    print(f"[{MAT_NAME}] ready; assigned to {n} selected mesh(es).")


main()
