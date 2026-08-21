# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Blender Add-ons Pack — Unified Sidebar UI Panels
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
import bpy
from bpy.types import Panel

class BAP_PT_MainPanel(Panel):
    """Painel principal do Blender Add-ons Pack na Sidebar (N-Panel)"""
    bl_label = "Add-ons Pack (Plugin Hub)"
    bl_idname = "BAP_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Add-ons Pack"

    def draw(self, context):
        layout = self.layout
        layout.label(text="Central de Ferramentas", icon='PACKAGE')


class BAP_PT_DynamicParentPanel(Panel):
    """Sub-painel para Dynamic Parent"""
    bl_label = "Dynamic Parent"
    bl_idname = "BAP_PT_dynamic_parent"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Add-ons Pack"
    bl_parent_id = "BAP_PT_main_panel"

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.scale_y = 1.2
        col.operator("dynamic_parent.create", text="Criar Parent", icon='KEY_HLT')
        col.operator("dynamic_parent.enable", text="Ativar Parent", icon='CHECKMARK')
        col.operator("dynamic_parent.disable", text="Desativar Parent", icon='KEY_DEHLT')
        
        row = layout.row(align=True)
        row.scale_y = 1.1
        row.operator("dynamic_parent.clear", text="Limpar", icon='X')
        row.operator("dynamic_parent.bake", text="Bake & Limpar", icon='REC')


class BAP_PT_RigConstraintsPanel(Panel):
    """Sub-painel para Rig Constraints Manager"""
    bl_label = "Rig Constraints (R6 & Copy Transforms)"
    bl_idname = "BAP_PT_rig_constraints"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Add-ons Pack"
    bl_parent_id = "BAP_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        if hasattr(context.scene, "rcm_props"):
            props = context.scene.rcm_props
            
            box1 = layout.box()
            box1.label(text="Copy Transforms entre Rigs:", icon='LINKED')
            box1.prop(props, "affected_rig", text="Rig Alvo")
            box1.prop(props, "source_rig", text="Rig Origem")
            
            row = box1.row()
            row.scale_y = 1.2
            row.operator("rcm.add_constraints", text="Adicionar Constraints", icon='ADD')
            
            box2 = layout.box()
            box2.label(text="Gerador de Foot Bones (R6):", icon='BONE_DATA')
            box2.operator("rcm.create_foot_bones", text="Criar Bones nos Pés (R6)", icon='AUTOMERGE_ON')

            box3 = layout.box()
            box3.label(text="Limpar Constraints:", icon='TRASH')
            box3.prop(props, "clear_rig", text="Rig para Limpar")
            box3.operator("rcm.clear_constraints", text="Remover Todas Constraints", icon='X')


class BAP_PT_RigToolsPanel(Panel):
    """Sub-painel para Ferramentas de Rig & Viewport"""
    bl_label = "Ferramentas de Rig & Viewport"
    bl_idname = "BAP_PT_rig_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Add-ons Pack"
    bl_parent_id = "BAP_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.operator("bap.toggle_in_front", text="Alternar 'In Front'", icon='HIDE_OFF')
        col.operator("bap.toggle_bone_names", text="Exibir Nomes dos Bones", icon='SORTALPHA')
        col.operator("bap.toggle_bone_axes", text="Exibir Eixos Locais (XYZ)", icon='ORIENTATION_GIMBAL')
        col.separator()
        col.operator("bap.reset_pose", text="Resetar Pose (Rest Pose)", icon='POSE_HLT')


class BAP_PT_AnimUtilsPanel(Panel):
    """Sub-painel para Utilitários de Animação"""
    bl_label = "Utilitários de Animação"
    bl_idname = "BAP_PT_anim_utils"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Add-ons Pack"
    bl_parent_id = "BAP_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.operator("bap.set_preview_range", text="Ajustar Frame Range", icon='PREVIEW_RANGE')
        col.operator("bap.bake_action", text="Bake Animação (Visual Keying)", icon='ACTION')


class BAP_PT_AboutPanel(Panel):
    """Sub-painel Sobre e Informações"""
    bl_label = "Sobre o Pacote"
    bl_idname = "BAP_PT_about"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Add-ons Pack"
    bl_parent_id = "BAP_PT_main_panel"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text="Blender Add-ons Pack v3.0", icon='INFO')
        box.label(text="Central Oficial de Plugins Open Source")
        box.operator("wm.url_open", text="Repositório no GitHub", icon='URL').url = "https://github.com/esqueiro99-bit/blender-addons-pack"


classes = (
    BAP_PT_MainPanel,
    BAP_PT_DynamicParentPanel,
    BAP_PT_RigConstraintsPanel,
    BAP_PT_RigToolsPanel,
    BAP_PT_AnimUtilsPanel,
    BAP_PT_AboutPanel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
