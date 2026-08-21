# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Blender Add-ons Pack — Rig & Bone Tools Module
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
import bpy
from bpy.types import Operator

class BAP_OT_ResetPose(Operator):
    """Reseta a pose atual do rig selecionado para o Rest Pose"""
    bl_idname = "bap.reset_pose"
    bl_label = "Resetar Pose"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'ARMATURE':
            self.report({'ERROR'}, "Selecione uma Armature!")
            return {'CANCELLED'}

        if context.mode != 'POSE':
            bpy.ops.object.mode_set(mode='POSE')

        for bone in obj.pose.bones:
            bone.location = (0, 0, 0)
            bone.rotation_euler = (0, 0, 0)
            bone.rotation_quaternion = (1, 0, 0, 0)
            bone.scale = (1, 1, 1)

        self.report({'INFO'}, "Pose resetada com sucesso!")
        return {'FINISHED'}


class BAP_OT_ToggleInFront(Operator):
    """Alterna a visibilidade 'In Front' (Na Frente) da Armature"""
    bl_idname = "bap.toggle_in_front"
    bl_label = "Alternar In Front"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'ARMATURE':
            self.report({'ERROR'}, "Selecione uma Armature!")
            return {'CANCELLED'}

        obj.show_in_front = not obj.show_in_front
        status = "Ativado" if obj.show_in_front else "Desativado"
        self.report({'INFO'}, f"In Front {status}!")
        return {'FINISHED'}


class BAP_OT_ToggleBoneNames(Operator):
    """Alterna a exibição dos nomes dos bones na Viewport"""
    bl_idname = "bap.toggle_bone_names"
    bl_label = "Exibir Nomes dos Bones"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'ARMATURE':
            self.report({'ERROR'}, "Selecione uma Armature!")
            return {'CANCELLED'}

        obj.data.show_names = not obj.data.show_names
        status = "visíveis" if obj.data.show_names else "ocultos"
        self.report({'INFO'}, f"Nomes dos bones {status}!")
        return {'FINISHED'}


class BAP_OT_ToggleBoneAxes(Operator):
    """Alterna a exibição dos eixos locais (XYZ) dos bones"""
    bl_idname = "bap.toggle_bone_axes"
    bl_label = "Exibir Eixos Locais"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'ARMATURE':
            self.report({'ERROR'}, "Selecione uma Armature!")
            return {'CANCELLED'}

        obj.data.show_axes = not obj.data.show_axes
        status = "visíveis" if obj.data.show_axes else "ocultos"
        self.report({'INFO'}, f"Eixos dos bones {status}!")
        return {'FINISHED'}


classes = (
    BAP_OT_ResetPose,
    BAP_OT_ToggleInFront,
    BAP_OT_ToggleBoneNames,
    BAP_OT_ToggleBoneAxes,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
