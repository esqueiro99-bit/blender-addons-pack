# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Blender Add-ons Pack — Animation Utilities Module
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
import bpy
from bpy.types import Operator, Panel
from bpy.props import IntProperty

class BAP_OT_SetPreviewRange(Operator):
    """Define o início e fim da timeline com base nos keyframes do objeto selecionado"""
    bl_idname = "bap.set_preview_range"
    bl_label = "Ajustar Range de Keyframes"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        if not obj or not obj.animation_data or not obj.animation_data.action:
            self.report({'WARNING'}, "Nenhuma animação/action encontrada no objeto ativo!")
            return {'CANCELLED'}

        action = obj.animation_data.action
        min_f, max_f = action.frame_range

        context.scene.frame_start = int(min_f)
        context.scene.frame_end = int(max_f)

        self.report({'INFO'}, f"Range definido: {int(min_f)} até {int(max_f)}")
        return {'FINISHED'}


class BAP_OT_BakeAction(Operator):
    """Bake de animação com visual keying para exportação FBX/GLTF limpa"""
    bl_idname = "bap.bake_action"
    bl_label = "Bake da Animação Selecionada"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        start = context.scene.frame_start
        end = context.scene.frame_end

        bpy.ops.nla.bake(
            frame_start=start,
            frame_end=end,
            step=1,
            only_selected=True,
            visual_keying=True,
            clear_constraints=False,
            clear_parents=False,
            use_current_action=True,
            clean_curves=True,
            bake_types={'POSE', 'OBJECT'}
        )

        self.report({'INFO'}, f"Animação assada (Bake) de {start} a {end}!")
        return {'FINISHED'}


classes = (
    BAP_OT_SetPreviewRange,
    BAP_OT_BakeAction,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
