"""
Frosted Holo Glass - Blender material setup
===========================================

A transparent, refracting frosted-glass material: rough transmission so
whatever sits behind the object is bent and blurred through it, chromatic
dispersion for violet/blue/pink fringes, thin-film iridescence, and a soft
milky scatter. No colour is painted onto the surface. The dark shapes you see
in the glass come from the backdrop being refracted, so the script can also
build a grey backdrop with large black letters behind the object.

Usage
-----
1. Select one or more mesh objects (e.g. a skull).
2. Open the Scripting workspace, paste this file and press Run Script.
3. Render with Cycles (F12). EEVEE shows a rougher approximation.

Targets Blender 4.2+ (dispersion and thin film need 4.2 or newer). Socket names
changed between versions, so every input goes through a helper that tries the
known names and skips anything your build does not have.
"""

import bpy
import math

MAT_NAME = "Frosted Holo Glass"

SETUP_RENDER = True      # Cycles, grainy samples, AgX, lens-dispersion compositor
SETUP_STUDIO = True      # grey world, key light and violet rim light
SETUP_BACKDROP = True    # grey card with big black letters behind the object
BACKDROP_TEXT = "ATEQ"
# Path to a blackletter .ttf/.otf (e.g. UnifrakturMaguntia from Google Fonts).
# Leave empty to use Blender's default font.
BACKDROP_FONT = ""

PARAMS = {
    "color":           (1.0, 1.0, 1.0, 1.0),
    "roughness":       0.15,   # frost: how much the refracted backdrop blurs
    "ior":             1.5,
    "transmission":    1.0,
    "dispersion":      0.08,   # Blender 4.2+: higher = stronger colour split
    "milk":            0.04,   # subsurface weight: soft milky scatter
    "milk_radius":     (0.3, 0.3, 0.45),
    "coat":            0.35,
    "coat_roughness":  0.08,
    "thin_film_nm":    380.0,  # Blender 4.2+ thin-film iridescence
    "thin_film_ior":   1.35,
    "sheen":           0.25,
    "sheen_tint":      (0.85, 0.8, 1.0, 1.0),
    "absorption":      (0.94, 0.92, 1.0, 1.0),
    "absorption_density": 0.15,
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


def build_material():
    p = PARAMS
    mat = bpy.data.materials.get(MAT_NAME) or bpy.data.materials.new(MAT_NAME)
    mat.use_nodes = True
    nt = mat.node_tree
    nodes, links = nt.nodes, nt.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputMaterial")
    out.location = (500, 0)

    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (100, 0)
    setv(bsdf, p["color"], "Base Color")
    setv(bsdf, p["roughness"], "Roughness")
    setv(bsdf, p["ior"], "IOR")
    setv(bsdf, p["transmission"], "Transmission Weight", "Transmission")
    setv(bsdf, p["dispersion"], "Dispersion")
    setv(bsdf, p["milk"], "Subsurface Weight", "Subsurface")
    setv(bsdf, p["milk_radius"], "Subsurface Radius")
    setv(bsdf, p["coat"], "Coat Weight", "Clearcoat")
    setv(bsdf, p["coat_roughness"], "Coat Roughness", "Clearcoat Roughness")
    setv(bsdf, p["sheen"], "Sheen Weight", "Sheen")
    setv(bsdf, p["sheen_tint"], "Sheen Tint")
    setv(bsdf, p["thin_film_nm"], "Thin Film Thickness")
    setv(bsdf, p["thin_film_ior"], "Thin Film IOR")
    links.new(bsdf.outputs[0], out.inputs["Surface"])

    # Faint absorption so thick parts (cranium, jaw) read slightly denser.
    vol = nodes.new("ShaderNodeVolumeAbsorption")
    vol.location = (100, -450)
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
    try:
        mat.refraction_depth = 0.2
    except AttributeError:
        pass
    mat.diffuse_color = (0.92, 0.92, 0.96, 0.6)
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
    cy.samples = 128                # no denoise on purpose: natural film grain
    cy.use_denoising = False
    cy.transmission_bounces = 24
    cy.glossy_bounces = 12
    cy.max_bounces = 24
    cy.caustics_refractive = True
    try:
        scene.view_settings.view_transform = "AgX"
        scene.view_settings.look = "AgX - Medium High Contrast"
    except TypeError:
        pass

    # Lens dispersion in the compositor adds the soft violet edge fringe.
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
        setv(lens, 0.02, "Dispersion")
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
        setv(bg, (0.75, 0.75, 0.78, 1.0), "Color")
        setv(bg, 0.7, "Strength")

    def area(name, loc, rot, energy, color, size):
        light = bpy.data.objects.get(name)
        if light is None:
            data = bpy.data.lights.new(name, "AREA")
            light = bpy.data.objects.new(name, data)
            scene.collection.objects.link(light)
        light.location, light.rotation_euler = loc, rot
        light.data.energy, light.data.color, light.data.size = energy, color, size

    area("FHG_Key", (-3.0, -3.0, 4.0), (0.8, 0.0, -0.8), 600, (1.0, 0.98, 0.96), 3.0)
    area("FHG_Rim", (2.5, 3.5, 1.5), (-1.3, 0.0, 2.6), 900, (0.65, 0.5, 1.0), 2.0)
    area("FHG_Fill", (3.5, -2.0, 0.5), (1.4, 0.0, 1.0), 200, (0.75, 0.88, 1.0), 4.0)


def emission_mat(name, color, strength=1.0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    em = nodes.new("ShaderNodeEmission")
    setv(em, color, "Color")
    setv(em, strength, "Strength")
    mat.node_tree.links.new(em.outputs[0], out.inputs["Surface"])
    return mat


def setup_backdrop(targets):
    """Grey card + big black letters behind the targets, facing the -Y camera axis."""
    scene = bpy.context.scene
    if targets:
        size = max(ob.dimensions.length for ob in targets)
        center = targets[0].matrix_world.translation.copy()
        for ob in targets[1:]:
            center += ob.matrix_world.translation
        center /= len(targets)
    else:
        size, center = 2.0, bpy.context.scene.cursor.location.copy()
    dist = size * 1.6

    card = bpy.data.objects.get("FHG_Backdrop")
    if card is None:
        mesh = bpy.data.meshes.new("FHG_Backdrop")
        mesh.from_pydata([(-1, 0, -1), (1, 0, -1), (1, 0, 1), (-1, 0, 1)], [], [(0, 1, 2, 3)])
        card = bpy.data.objects.new("FHG_Backdrop", mesh)
        scene.collection.objects.link(card)
    card.location = (center.x, center.y + dist, center.z)
    card.scale = (size * 3, 1, size * 3)
    card.data.materials.clear()
    card.data.materials.append(emission_mat("FHG_Grey", (0.74, 0.74, 0.77, 1.0), 1.0))

    txt = bpy.data.objects.get("FHG_Letters")
    if txt is None:
        curve = bpy.data.curves.new("FHG_Letters", "FONT")
        txt = bpy.data.objects.new("FHG_Letters", curve)
        scene.collection.objects.link(txt)
    txt.data.body = BACKDROP_TEXT
    txt.data.align_x, txt.data.align_y = "CENTER", "CENTER"
    txt.data.size = size * 1.1
    if BACKDROP_FONT:
        try:
            txt.data.font = bpy.data.fonts.load(BACKDROP_FONT, check_existing=True)
        except RuntimeError as exc:
            print(f"[{MAT_NAME}] font not loaded: {exc}")
    txt.location = (center.x, center.y + dist - 0.01, center.z)
    txt.rotation_euler = (math.radians(90), 0, 0)
    txt.data.materials.clear()
    txt.data.materials.append(emission_mat("FHG_Black", (0.005, 0.005, 0.008, 1.0), 1.0))


def main():
    targets = [ob for ob in bpy.context.selected_objects if ob.type == "MESH"]
    mat = build_material()
    n = assign(mat)
    if SETUP_RENDER:
        setup_render()
    if SETUP_STUDIO:
        setup_studio()
    if SETUP_BACKDROP:
        setup_backdrop(targets)
    print(f"[{MAT_NAME}] ready; assigned to {n} selected mesh(es).")


main()
