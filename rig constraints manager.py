# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Rig Constraints Manager – Blender Add-on
#  Gerencia Copy Transforms entre dois rigs, cria bones de pé no R6,
#  e limpa constraints.
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

bl_info = {
    "name": "Rig Constraints Manager",
    "author": "Real Antigravity",
    "version": (1, 1, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > Rig Constraints",
    "description": "Gerencia constraints entre rigs R6/custom, cria foot bones, e limpa constraints.",
    "category": "Rigging",
}

import bpy
import mathutils
from bpy.props import PointerProperty, EnumProperty, BoolProperty
from bpy.types import PropertyGroup, Operator, Panel



# ─────────────────────────────────────────────────────────────────────────────
#  Utilidades
# ─────────────────────────────────────────────────────────────────────────────

def is_armature(obj):
    """Filtra apenas objetos do tipo Armature."""
    return obj and obj.type == 'ARMATURE'


def get_matching_bones(source_arm, target_arm):
    """Retorna lista de nomes de bones que existem em ambos os armatures."""
    src_names = set(source_arm.data.bones.keys())
    tgt_names = set(target_arm.data.bones.keys())
    return sorted(src_names & tgt_names)


# ─────────────────────────────────────────────────────────────────────────────
#  Propriedades da cena
# ─────────────────────────────────────────────────────────────────────────────

class RCM_Properties(PropertyGroup):
    # --- Seção 1: Dois rigs ---
    affected_rig: PointerProperty(
        name="Rig Afetado",
        description="O rig que vai RECEBER as constraints (Copy Transforms)",
        type=bpy.types.Object,
        poll=lambda self, obj: is_armature(obj),
    )
    source_rig: PointerProperty(
        name="Rig Customizado",
        description="O rig de ORIGEM cujos bones serão referenciados pelas constraints",
        type=bpy.types.Object,
        poll=lambda self, obj: is_armature(obj),
    )

    # --- Seção 2: Limpar constraints ---
    clear_rig: PointerProperty(
        name="Rig para Limpar",
        description="O rig do qual TODOS os bone constraints serão removidos",
        type=bpy.types.Object,
        poll=lambda self, obj: is_armature(obj),
    )


# ─────────────────────────────────────────────────────────────────────────────
#  Operadores – Seção 1
# ─────────────────────────────────────────────────────────────────────────────

class RCM_OT_AddConstraints(Operator):
    """Adiciona Copy Transforms nos bones em comum entre os dois rigs"""
    bl_idname = "rcm.add_constraints"
    bl_label = "Adicionar Constraints"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.rcm_props
        affected = props.affected_rig
        source = props.source_rig

        if not affected or not source:
            self.report({'ERROR'}, "Selecione ambos os rigs!")
            return {'CANCELLED'}

        if affected == source:
            self.report({'ERROR'}, "Os dois rigs devem ser diferentes!")
            return {'CANCELLED'}

        matching = get_matching_bones(affected, source)
        if not matching:
            self.report({'WARNING'}, "Nenhum bone com nome igual encontrado entre os dois rigs.")
            return {'CANCELLED'}

        added_count = 0

        for bone_name in matching:
            pose_bone = affected.pose.bones[bone_name]

            # Verifica se já existe um Copy Transforms apontando para o source
            already_exists = any(
                c.type == 'COPY_TRANSFORMS'
                and c.target == source
                and c.subtarget == bone_name
                for c in pose_bone.constraints
            )
            if not already_exists:
                con = pose_bone.constraints.new('COPY_TRANSFORMS')
                con.name = f"RCM_CopyTrans_{source.name}"
                con.target = source
                con.subtarget = bone_name
                con.target_space = 'LOCAL'
                con.owner_space = 'LOCAL'
                added_count += 1

        self.report({'INFO'}, f"✓ {added_count} Copy Transforms adicionadas em {len(matching)} bones.")
        return {'FINISHED'}


class RCM_OT_RemoveConstraints(Operator):
    """Remove as constraints Copy Transforms que apontam para o rig customizado"""
    bl_idname = "rcm.remove_constraints"
    bl_label = "Remover Constraints"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.rcm_props
        affected = props.affected_rig
        source = props.source_rig

        if not affected or not source:
            self.report({'ERROR'}, "Selecione ambos os rigs!")
            return {'CANCELLED'}

        removed_count = 0

        for pose_bone in affected.pose.bones:
            # Coletar constraints Copy Transforms a remover
            to_remove = [
                c for c in pose_bone.constraints
                if c.type == 'COPY_TRANSFORMS'
                and c.target == source
                and c.subtarget == pose_bone.name
            ]
            for c in to_remove:
                pose_bone.constraints.remove(c)
                removed_count += 1

        self.report({'INFO'}, f"✓ {removed_count} Copy Transforms removidas.")
        return {'FINISHED'}


# ─────────────────────────────────────────────────────────────────────────────
#  Operador – Seção 2: Limpar TODAS as constraints
# ─────────────────────────────────────────────────────────────────────────────

class RCM_OT_ClearAllConstraints(Operator):
    """Remove TODAS as bone constraints do rig selecionado"""
    bl_idname = "rcm.clear_all_constraints"
    bl_label = "Limpar Todas as Constraints"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        # Pede confirmação antes de apagar tudo
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        props = context.scene.rcm_props
        rig = props.clear_rig

        if not rig:
            self.report({'ERROR'}, "Selecione um rig!")
            return {'CANCELLED'}

        removed_count = 0
        bone_count = 0

        for pose_bone in rig.pose.bones:
            num = len(pose_bone.constraints)
            if num > 0:
                bone_count += 1
                removed_count += num
                # Remove de trás pra frente
                for i in range(num - 1, -1, -1):
                    pose_bone.constraints.remove(pose_bone.constraints[i])

        self.report({'INFO'}, f"✓ {removed_count} constraints removidas de {bone_count} bones em '{rig.name}'.")
        return {'FINISHED'}


# ─────────────────────────────────────────────────────────────────────────────
#  Operador – Seção 3: Criar Foot Bones no R6
# ─────────────────────────────────────────────────────────────────────────────

def _find_leg_mesh(rig, leg_bone_name):
    """Busca a mesh da perna associada ao bone.

    Procura por:
      1. Objeto mesh filho do rig com nome igual ao bone (ex: 'Right Leg')
      2. Objeto mesh filho que tenha vertex group com o nome do bone
      3. Qualquer mesh na cena com nome igual ao bone
    Retorna o objeto mesh ou None.
    """
    # 1 – Filhos diretos com nome igual
    for child in rig.children:
        if child.type == 'MESH' and child.name == leg_bone_name:
            return child

    # 2 – Filhos com vertex group correspondente
    for child in rig.children:
        if child.type == 'MESH':
            for vg in child.vertex_groups:
                if vg.name == leg_bone_name:
                    return child

    # 3 – Qualquer mesh na cena com o nome do bone
    for obj in bpy.data.objects:
        if obj.type == 'MESH' and obj.name == leg_bone_name:
            return obj

    return None


def _get_mesh_bbox_in_armature_space(mesh_obj, armature_obj):
    """Calcula a bounding box da mesh no espaço local do armature.

    Retorna (center_x, center_y, min_z, max_z) no espaço do armature.
    """
    # Matriz para converter do espaço da mesh para o espaço do armature
    mat = armature_obj.matrix_world.inverted() @ mesh_obj.matrix_world

    # Transformar todos os vértices da bounding box
    bbox_corners = [mat @ mathutils.Vector(corner) for corner in mesh_obj.bound_box]

    xs = [v.x for v in bbox_corners]
    ys = [v.y for v in bbox_corners]
    zs = [v.z for v in bbox_corners]

    center_x = (min(xs) + max(xs)) / 2.0
    center_y = (min(ys) + max(ys)) / 2.0
    min_z = min(zs)
    max_z = max(zs)

    return center_x, center_y, min_z, max_z


class RCM_OT_CreateFootBones(Operator):
    """Cria bones de pé (Right Foot / Left Foot) baseado na mesh da perna do R6"""
    bl_idname = "rcm.create_foot_bones"
    bl_label = "Criar Foot Bones no R6"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.rcm_props
        rig = props.affected_rig

        if not rig:
            self.report({'ERROR'}, "Selecione o Rig Afetado (R6)!")
            return {'CANCELLED'}

        # Mapeia perna -> nome do foot bone a criar
        leg_to_foot = {
            'Right Leg': 'Right Foot',
            'Left Leg': 'Left Foot',
        }

        # Verifica se as pernas existem
        existing_bones = set(rig.data.bones.keys())
        legs_found = [leg for leg in leg_to_foot if leg in existing_bones]

        if not legs_found:
            self.report({'ERROR'}, "Nenhum bone 'Right Leg' ou 'Left Leg' encontrado no rig!")
            return {'CANCELLED'}

        # Verificar quais foot bones já existem
        feet_already = [leg_to_foot[leg] for leg in legs_found if leg_to_foot[leg] in existing_bones]
        if len(feet_already) == len(legs_found):
            self.report({'WARNING'}, f"Foot bones já existem: {', '.join(feet_already)}")
            return {'CANCELLED'}

        # Buscar as meshes das pernas ANTES de entrar em Edit Mode
        # (bound_box não é acessível em Edit Mode)
        leg_mesh_data = {}
        for leg_name in legs_found:
            foot_name = leg_to_foot[leg_name]
            if foot_name in existing_bones:
                continue
            mesh_obj = _find_leg_mesh(rig, leg_name)
            if mesh_obj:
                cx, cy, min_z, max_z = _get_mesh_bbox_in_armature_space(mesh_obj, rig)
                leg_mesh_data[leg_name] = {
                    'mesh_name': mesh_obj.name,
                    'center_x': cx,
                    'center_y': cy,
                    'min_z': min_z,
                    'max_z': max_z,
                }

        # Guardar o modo atual e trocar para Edit Mode
        prev_active = context.view_layer.objects.active
        prev_mode = rig.mode if rig.mode != 'OBJECT' else None

        context.view_layer.objects.active = rig
        bpy.ops.object.mode_set(mode='EDIT')

        edit_bones = rig.data.edit_bones
        created = []

        for leg_name, foot_name in leg_to_foot.items():
            if leg_name not in existing_bones:
                continue
            if foot_name in existing_bones:
                continue

            leg_bone = edit_bones[leg_name]

            if leg_name in leg_mesh_data:
                # ── Posicionar baseado na mesh da perna ──
                data = leg_mesh_data[leg_name]

                # Head do foot bone: centro X/Y da mesh, no fundo -Z da mesh
                foot_head = mathutils.Vector((
                    data['center_x'],
                    data['center_y'],
                    data['min_z'],
                ))

                # Tail do foot bone: ligeiramente para frente (-Y) a partir do head
                foot_tail = foot_head + mathutils.Vector((0, -0.15, 0))

                foot_bone = edit_bones.new(foot_name)
                foot_bone.head = foot_head
                foot_bone.tail = foot_tail
                foot_bone.parent = leg_bone
                foot_bone.use_connect = False  # Não conectar, pois o head pode não coincidir com tail da perna

            else:
                # ── Fallback: offset padrão a partir do tail da perna ──
                foot_bone = edit_bones.new(foot_name)
                foot_bone.head = leg_bone.tail.copy()
                foot_bone.tail = leg_bone.tail + mathutils.Vector((0, -0.15, -0.05))
                foot_bone.parent = leg_bone
                foot_bone.use_connect = True

            # Copiar layers/collections do bone pai (compatível com Blender 3.x e 4.x)
            try:
                # Blender 4.0+ usa bone collections
                for coll in leg_bone.collections:
                    coll.assign(foot_bone)
            except AttributeError:
                # Blender 3.x usa layers
                foot_bone.layers = leg_bone.layers

            mesh_info = f" (mesh: '{leg_mesh_data[leg_name]['mesh_name']}')" if leg_name in leg_mesh_data else " (fallback)"
            created.append(f"{foot_name}{mesh_info}")

        # Voltar ao modo anterior
        bpy.ops.object.mode_set(mode='OBJECT')
        if prev_mode:
            bpy.ops.object.mode_set(mode=prev_mode)
        context.view_layer.objects.active = prev_active

        self.report({'INFO'}, f"✓ Foot bones criados: {', '.join(created)}")
        return {'FINISHED'}


# ─────────────────────────────────────────────────────────────────────────────
#  Painel na Sidebar (N-Panel)
# ─────────────────────────────────────────────────────────────────────────────

class RCM_PT_MainPanel(Panel):
    bl_label = "Rig Constraints Manager"
    bl_idname = "RCM_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Rig Constraints"

    def draw(self, context):
        layout = self.layout
        props = context.scene.rcm_props

        # ── Seção 1: Copy Transforms entre dois rigs ──
        box = layout.box()
        box.label(text="Copy Transforms entre Rigs", icon='CONSTRAINT_BONE')

        col = box.column(align=True)
        col.prop(props, "affected_rig", icon='ARMATURE_DATA')
        col.prop(props, "source_rig", icon='ARMATURE_DATA')

        col.separator()

        # Mostra quantos bones em comum
        if props.affected_rig and props.source_rig and props.affected_rig != props.source_rig:
            matching = get_matching_bones(props.affected_rig, props.source_rig)
            col.label(text=f"Bones em comum: {len(matching)}", icon='BONE_DATA')
            col.separator()

        row = col.row(align=True)
        row.scale_y = 1.4
        row.operator("rcm.add_constraints", icon='ADD')
        row.operator("rcm.remove_constraints", icon='REMOVE')

        # ── Seção 2: Criar Foot Bones no R6 ──
        layout.separator()
        box = layout.box()
        box.label(text="Criar Foot Bones (R6)", icon='BONE_DATA')

        col = box.column(align=True)
        col.label(text="Usa o Rig Afetado acima", icon='INFO')

        # Mostrar status dos foot bones
        if props.affected_rig:
            bones = set(props.affected_rig.data.bones.keys())
            has_rf = 'Right Foot' in bones
            has_lf = 'Left Foot' in bones
            status_r = "✓" if has_rf else "✗"
            status_l = "✓" if has_lf else "✗"
            col.label(text=f"Right Foot: {status_r}  |  Left Foot: {status_l}")

        col.separator()
        row = col.row()
        row.scale_y = 1.4
        row.operator("rcm.create_foot_bones", icon='ADD')

        # ── Seção 3: Limpar todas as constraints ──
        layout.separator()
        box = layout.box()
        box.label(text="Limpar Todas as Constraints", icon='TRASH')

        col = box.column(align=True)
        col.prop(props, "clear_rig", icon='ARMATURE_DATA')

        # Mostra contagem de constraints existentes
        if props.clear_rig:
            total = sum(len(pb.constraints) for pb in props.clear_rig.pose.bones)
            col.label(text=f"Total de constraints: {total}", icon='INFO')

        col.separator()
        row = col.row()
        row.scale_y = 1.4
        row.alert = True  # Botão vermelho de alerta
        row.operator("rcm.clear_all_constraints", icon='CANCEL')


# ─────────────────────────────────────────────────────────────────────────────
#  Registro
# ─────────────────────────────────────────────────────────────────────────────

classes = (
    RCM_Properties,
    RCM_OT_AddConstraints,
    RCM_OT_RemoveConstraints,
    RCM_OT_ClearAllConstraints,
    RCM_OT_CreateFootBones,
    RCM_PT_MainPanel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.rcm_props = PointerProperty(type=RCM_Properties)


def unregister():
    del bpy.types.Scene.rcm_props
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
