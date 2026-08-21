# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Blender Add-ons Pack — All-in-One Unified Plugin
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
bl_info = {
    "name": "Blender Add-ons Pack (All-in-One)",
    "author": "Plugin Hub Team (Roman Volodin, Real Antigravity)",
    "version": (3, 0, 0),
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar (N-Panel) > Add-ons Pack",
    "description": "Pacote unificado de add-ons para Blender: Dynamic Parent, Rig Constraints Manager (R6), Rig Tools e Animation Utilities.",
    "category": "Animation",
    "doc_url": "https://github.com/esqueiro99/blender-addons-pack",
    "tracker_url": "https://github.com/esqueiro99/blender-addons-pack/issues",
}

import bpy
from . import dynamic_parent
from . import rig_constraints_manager
from . import rig_tools
from . import anim_utils
from . import ui_panels

modules = (
    dynamic_parent,
    rig_constraints_manager,
    rig_tools,
    anim_utils,
    ui_panels,
)

def register():
    for module in modules:
        if hasattr(module, "register"):
            module.register()

def unregister():
    for module in reversed(modules):
        if hasattr(module, "unregister"):
            module.unregister()

if __name__ == "__main__":
    register()
