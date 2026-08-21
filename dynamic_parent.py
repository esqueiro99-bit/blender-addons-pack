# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

import bpy


bl_info = {
    "name": "Dynamic Parent (Blender 5.0)",
    "author": "Roman Volodin, roman.volodin@gmail.com | wzrd",
    "version": (2, 1, 0),
    "blender": (5, 0, 0),
    "location": "View3D > Sidebar (N-Panel) > Animation / Item / Tool",
    "description": "Allows to create, enable, and disable an animated Child Of constraint.",
    "category": "Animation",
}


def get_rotation_mode(obj):
    if obj.rotation_mode in ("QUATERNION", "AXIS_ANGLE"):
        return obj.rotation_mode.lower()
    return "euler"


def get_selected_objects(context):
    if context.mode not in ("OBJECT", "POSE"):
        return []

    if context.mode == "OBJECT":
        active = context.active_object
        if not active:
            return []
        selected = [obj for obj in context.selected_objects if obj != active]

    if context.mode == "POSE":
        active = context.active_pose_bone
        if not active:
            return []
        selected = [bone for bone in context.selected_pose_bones if bone != active]

    selected.append(active)
    return selected


def get_last_dynamic_parent_constraint(obj):
    if not hasattr(obj, "constraints") or not obj.constraints:
        return None
    for const in reversed(obj.constraints):
        if const.name.startswith("DP_") and const.influence > 0:
            return const
    return None


def get_disabled_dynamic_parent_constraint(obj):
    if not hasattr(obj, "constraints") or not obj.constraints:
        return None
    for const in reversed(obj.constraints):
        if const.name.startswith("DP_"):
            return const
    return None


def insert_keyframe(obj, frame):
    rotation_mode = get_rotation_mode(obj)
    if isinstance(obj, bpy.types.PoseBone):
        arm = obj.id_data
        prefix = f'pose.bones["{obj.name}"].'
        arm.keyframe_insert(data_path=f"{prefix}location", frame=frame)
        arm.keyframe_insert(data_path=f"{prefix}rotation_{rotation_mode}", frame=frame)
        arm.keyframe_insert(data_path=f"{prefix}scale", frame=frame)
    else:
        obj.keyframe_insert(data_path="location", frame=frame)
        obj.keyframe_insert(data_path=f"rotation_{rotation_mode}", frame=frame)
        obj.keyframe_insert(data_path="scale", frame=frame)


def insert_keyframe_constraint(obj, constraint, frame):
    if isinstance(obj, bpy.types.PoseBone):
        arm = obj.id_data
        data_path = f'pose.bones["{obj.name}"].constraints["{constraint.name}"].influence'
        arm.keyframe_insert(data_path=data_path, frame=frame)
    else:
        data_path = f'constraints["{constraint.name}"].influence'
        obj.keyframe_insert(data_path=data_path, frame=frame)


def set_childof_inverse(obj, constraint):
    """Set the inverse matrix for a Child Of constraint accurately without unwanted jumps."""
    bpy.context.view_layer.update()
    
    if isinstance(obj, bpy.types.PoseBone):
        arm = obj.id_data
        target = constraint.target
        if not target:
            return
            
        try:
            with bpy.context.temp_override(active_object=arm, active_pose_bone=obj, constraint=constraint):
                bpy.ops.constraint.childof_set_inverse(owner="BONE", constraint=constraint.name)
                bpy.context.view_layer.update()
                return
        except Exception:
            pass

        if constraint.subtarget and target.type == "ARMATURE":
            sub_bone = target.pose.bones.get(constraint.subtarget)
            target_mat = target.matrix_world @ sub_bone.matrix if sub_bone else target.matrix_world
        else:
            target_mat = target.matrix_world
            
        bone_world_mat = arm.matrix_world @ obj.matrix
        try:
            constraint.inverse_matrix = target_mat.inverted() @ bone_world_mat
        except Exception:
            pass
    else:
        target = constraint.target
        if not target:
            return
            
        try:
            with bpy.context.temp_override(active_object=obj, constraint=constraint):
                bpy.ops.constraint.childof_set_inverse(owner="OBJECT", constraint=constraint.name)
                bpy.context.view_layer.update()
                return
        except Exception:
            pass

        if constraint.subtarget and target.type == "ARMATURE":
            sub_bone = target.pose.bones.get(constraint.subtarget)
            target_mat = target.matrix_world @ sub_bone.matrix if sub_bone else target.matrix_world
        else:
            target_mat = target.matrix_world
            
        try:
            constraint.inverse_matrix = target_mat.inverted() @ obj.matrix_world
        except Exception:
            pass
            
    bpy.context.view_layer.update()


def dp_keyframe_insert_obj(obj, frame=None):
    if frame is None:
        frame = bpy.context.scene.frame_current
    insert_keyframe(obj, frame=frame)


def dp_keyframe_insert_pbone(arm, pbone, frame=None):
    if frame is None:
        frame = bpy.context.scene.frame_current
    insert_keyframe(pbone, frame=frame)


def dp_create_dynamic_parent_obj(op):
    obj = bpy.context.active_object
    scn = bpy.context.scene
    list_selected_obj = list(bpy.context.selected_objects)

    if len(list_selected_obj) == 2:
        i = list_selected_obj.index(obj)
        list_selected_obj.pop(i)
        parent_obj = list_selected_obj[0]
        current_frame = scn.frame_current

        orig_matrix = obj.matrix_world.copy()

        dp_keyframe_insert_obj(obj, frame=current_frame)
        last_constraint = obj.constraints.new(type="CHILD_OF")
        last_constraint.target = parent_obj

        if parent_obj.type == "ARMATURE":
            subtarget_name = parent_obj.data.bones.active.name if parent_obj.data.bones.active else ""
            last_constraint.subtarget = subtarget_name
            last_constraint.name = (
                "DP_" + last_constraint.target.name + "." + last_constraint.subtarget
            )
        else:
            last_constraint.name = "DP_" + last_constraint.target.name

        bpy.context.view_layer.update()
        set_childof_inverse(obj, last_constraint)
        obj.matrix_world = orig_matrix

        last_constraint.influence = 0
        insert_keyframe_constraint(obj, last_constraint, frame=current_frame - 1)

        last_constraint.influence = 1
        insert_keyframe_constraint(obj, last_constraint, frame=current_frame)
        dp_keyframe_insert_obj(obj, frame=current_frame)

        for ob in list_selected_obj:
            ob.select_set(False)

        obj.select_set(True)
    else:
        op.report({"ERROR"}, "Selecione 2 objetos: primeiro o Filho, depois o Pai.")


def dp_create_dynamic_parent_pbone(op):
    arm = bpy.context.active_object
    pbone = bpy.context.active_pose_bone
    scn = bpy.context.scene
    list_selected_obj = list(bpy.context.selected_objects)

    if len(list_selected_obj) == 2 or len(list_selected_obj) == 1:
        if len(list_selected_obj) == 2:
            i = list_selected_obj.index(arm)
            list_selected_obj.pop(i)
            parent_obj = list_selected_obj[0]
            if parent_obj.type == "ARMATURE":
                parent_obj_pbone = parent_obj.data.bones.active
                if parent_obj_pbone is None:
                    op.report(
                        {"ERROR"},
                        "Selecione um osso pai no outro armature",
                    )
                    return
        else:
            parent_obj = arm
            selected_bones = list(bpy.context.selected_pose_bones)
            if pbone in selected_bones:
                selected_bones.remove(pbone)
            if not selected_bones:
                op.report({"ERROR"}, "Selecione pelo menos 2 ossos: o Filho e o Pai.")
                return
            parent_obj_pbone = selected_bones[0]

        current_frame = scn.frame_current
        orig_matrix = pbone.matrix.copy()

        dp_keyframe_insert_pbone(arm, pbone, frame=current_frame)
        last_constraint = pbone.constraints.new(type="CHILD_OF")
        last_constraint.target = parent_obj

        if parent_obj.type == "ARMATURE":
            last_constraint.subtarget = parent_obj_pbone.name
            last_constraint.name = (
                "DP_" + last_constraint.target.name + "." + last_constraint.subtarget
            )
        else:
            last_constraint.name = "DP_" + last_constraint.target.name

        bpy.context.view_layer.update()
        set_childof_inverse(pbone, last_constraint)
        pbone.matrix = orig_matrix

        last_constraint.influence = 0
        insert_keyframe_constraint(pbone, last_constraint, frame=current_frame - 1)

        last_constraint.influence = 1
        insert_keyframe_constraint(pbone, last_constraint, frame=current_frame)
        dp_keyframe_insert_pbone(arm, pbone, frame=current_frame)
    else:
        op.report({"ERROR"}, "Selecione 2 objetos/armatures")


def enable_constraint(obj, const, frame):
    if isinstance(obj, bpy.types.PoseBone):
        matrix_final = obj.matrix.copy()
    else:
        matrix_final = obj.matrix_world.copy()

    # Keyframe position and constraint influence at frame - 1 (when influence is 0)
    insert_keyframe(obj, frame=frame - 1)
    insert_keyframe_constraint(obj, const, frame=frame - 1)

    # Recalculate inverse matrix at frame before turning influence to 1
    set_childof_inverse(obj, const)

    const.influence = 1
    if hasattr(bpy.context, "view_layer") and bpy.context.view_layer:
        bpy.context.view_layer.update()

    if isinstance(obj, bpy.types.PoseBone):
        obj.matrix = matrix_final
    else:
        obj.matrix_world = matrix_final

    insert_keyframe(obj, frame=frame)
    insert_keyframe_constraint(obj, const, frame=frame)


def disable_constraint(obj, const, frame):
    if isinstance(obj, bpy.types.PoseBone):
        matrix_final = obj.matrix.copy()
    else:
        matrix_final = obj.matrix_world.copy()

    insert_keyframe(obj, frame=frame - 1)
    insert_keyframe_constraint(obj, const, frame=frame - 1)

    const.influence = 0
    if hasattr(bpy.context, "view_layer") and bpy.context.view_layer:
        bpy.context.view_layer.update()

    if isinstance(obj, bpy.types.PoseBone):
        obj.matrix = matrix_final
    else:
        obj.matrix_world = matrix_final

    insert_keyframe(obj, frame=frame)
    insert_keyframe_constraint(obj, const, frame=frame)


def dp_clear(obj, pbone):
    """Remove all Dynamic Parent constraints and their animation keys."""
    target_item = pbone if pbone else obj
    anim = getattr(obj, "animation_data", None)
    action = getattr(anim, "action", None) if anim else None

    if hasattr(target_item, "constraints"):
        for const in list(target_item.constraints):
            if const.name.startswith("DP_"):
                target_item.constraints.remove(const)

    if not action or not hasattr(action, "fcurves"):
        return

    dp_curves = []
    dp_keys = []
    for fcurve in action.fcurves:
        if "constraints" in fcurve.data_path and "DP_" in fcurve.data_path:
            dp_curves.append(fcurve)

    for f in dp_curves:
        for key in f.keyframe_points:
            dp_keys.append(key.co[0])

    dp_keys = list(set(dp_keys))
    dp_keys.sort()

    for fcurve in action.fcurves[:]:
        if fcurve.data_path.startswith("constraints") and "DP_" in fcurve.data_path:
            action.fcurves.remove(fcurve)
        else:
            for frame in dp_keys:
                for key in fcurve.keyframe_points[:]:
                    if key.co[0] == frame:
                        fcurve.keyframe_points.remove(key)
            if not fcurve.keyframe_points:
                action.fcurves.remove(fcurve)


class DYNAMIC_PARENT_OT_create(bpy.types.Operator):
    """Create a new animated Child Of constraint"""

    bl_idname = "dynamic_parent.create"
    bl_label = "Create Constraint"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = context.active_object
        frame = context.scene.frame_current

        if not obj:
            self.report({"ERROR"}, "No active object selected.")
            return {"CANCELLED"}

        if obj.type == "ARMATURE":
            if obj.mode != "POSE":
                self.report({"ERROR"}, "Armature objects must be in Pose mode.")
                return {"CANCELLED"}
            pbone = bpy.context.active_pose_bone
            if not pbone:
                self.report({"ERROR"}, "No active pose bone selected.")
                return {"CANCELLED"}
            const = get_last_dynamic_parent_constraint(pbone)
            if const:
                disable_constraint(pbone, const, frame)
            dp_create_dynamic_parent_pbone(self)
        else:
            const = get_last_dynamic_parent_constraint(obj)
            if const:
                disable_constraint(obj, const, frame)
            dp_create_dynamic_parent_obj(self)

        return {"FINISHED"}


class DYNAMIC_PARENT_OT_enable(bpy.types.Operator):
    """Enable the current animated Child Of constraint"""

    bl_idname = "dynamic_parent.enable"
    bl_label = "Enable Constraint"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.mode in ("OBJECT", "POSE")

    def execute(self, context):
        frame = context.scene.frame_current
        objects = get_selected_objects(context)
        counter = 0

        if not objects:
            self.report({"ERROR"}, "Nothing selected.")
            return {"CANCELLED"}

        for obj in objects:
            const = get_disabled_dynamic_parent_constraint(obj)
            if const is None:
                continue
            enable_constraint(obj, const, frame)
            counter += 1

        if counter == 0:
            self.report({"WARNING"}, "No Dynamic Parent constraint found to enable.")
            return {"CANCELLED"}

        self.report({"INFO"}, f"{counter} constraints were enabled.")
        return {"FINISHED"}


class DYNAMIC_PARENT_OT_disable(bpy.types.Operator):
    """Disable the current animated Child Of constraint"""

    bl_idname = "dynamic_parent.disable"
    bl_label = "Disable Constraint"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.mode in ("OBJECT", "POSE")

    def execute(self, context):
        frame = context.scene.frame_current
        objects = get_selected_objects(context)
        counter = 0

        if not objects:
            self.report({"ERROR"}, "Nothing selected.")
            return {"CANCELLED"}

        for obj in objects:
            const = get_last_dynamic_parent_constraint(obj)
            if const is None:
                continue
            disable_constraint(obj, const, frame)
            counter += 1

        if counter == 0:
            self.report({"WARNING"}, "No active Dynamic Parent constraint found to disable.")
            return {"CANCELLED"}

        self.report({"INFO"}, f"{counter} constraints were disabled.")
        return {"FINISHED"}


class DYNAMIC_PARENT_OT_clear(bpy.types.Operator):
    """Clear Dynamic Parent constraints"""

    bl_idname = "dynamic_parent.clear"
    bl_label = "Clear Dynamic Parent"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        pbone = None
        obj = bpy.context.active_object
        if obj and obj.type == "ARMATURE":
            pbone = bpy.context.active_pose_bone

        if obj:
            dp_clear(obj, pbone)

        return {"FINISHED"}


class DYNAMIC_PARENT_OT_bake(bpy.types.Operator):
    """Bake Dynamic Parent animation"""

    bl_idname = "dynamic_parent.bake"
    bl_label = "Bake Dynamic Parent"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = bpy.context.active_object
        scn = bpy.context.scene

        if not obj:
            return {"CANCELLED"}

        if obj.type == "ARMATURE":
            pbone = bpy.context.active_pose_bone
            bpy.ops.nla.bake(
                frame_start=scn.frame_start,
                frame_end=scn.frame_end,
                step=1,
                only_selected=True,
                visual_keying=True,
                clear_constraints=False,
                clear_parents=False,
                bake_types={"POSE"},
            )
            if pbone and hasattr(pbone, "constraints"):
                for const in list(pbone.constraints):
                    if const.name.startswith("DP_"):
                        pbone.constraints.remove(const)
        else:
            bpy.ops.nla.bake(
                frame_start=scn.frame_start,
                frame_end=scn.frame_end,
                step=1,
                only_selected=True,
                visual_keying=True,
                clear_constraints=False,
                clear_parents=False,
                bake_types={"OBJECT"},
            )
            for const in list(obj.constraints):
                if const.name.startswith("DP_"):
                    obj.constraints.remove(const)

        return {"FINISHED"}


class DYNAMIC_PARENT_MT_clear_menu(bpy.types.Menu):
    """Clear or bake Dynamic Parent constraints"""

    bl_label = "Clear Dynamic Parent?"
    bl_idname = "DYNAMIC_PARENT_MT_clear_menu"

    def draw(self, context):
        layout = self.layout
        layout.operator("dynamic_parent.clear", text="Clear", icon="X")
        layout.operator("dynamic_parent.bake", text="Bake and clear", icon="REC")


def draw_dp_panel_layout(self, context):
    layout = self.layout
    col = layout.column(align=True)
    col.operator("dynamic_parent.create", text="Create", icon="KEY_HLT")
    col.operator("dynamic_parent.enable", text="Enable", icon="CHECKMARK")
    col.operator("dynamic_parent.disable", text="Disable", icon="KEY_DEHLT")
    col.menu("DYNAMIC_PARENT_MT_clear_menu", text="Clear")


class DYNAMIC_PARENT_PT_ui_animation(bpy.types.Panel):
    bl_label = "Dynamic Parent"
    bl_idname = "DYNAMIC_PARENT_PT_ui_animation"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Animation"

    def draw(self, context):
        draw_dp_panel_layout(self, context)


class DYNAMIC_PARENT_PT_ui_item(bpy.types.Panel):
    bl_label = "Dynamic Parent"
    bl_idname = "DYNAMIC_PARENT_PT_ui_item"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Item"

    def draw(self, context):
        draw_dp_panel_layout(self, context)


class DYNAMIC_PARENT_PT_ui_tool(bpy.types.Panel):
    bl_label = "Dynamic Parent"
    bl_idname = "DYNAMIC_PARENT_PT_ui_tool"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Tool"

    def draw(self, context):
        draw_dp_panel_layout(self, context)


class DYNAMIC_PARENT_PT_ui_dp(bpy.types.Panel):
    bl_label = "Dynamic Parent"
    bl_idname = "DYNAMIC_PARENT_PT_ui_dp"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Dynamic Parent"

    def draw(self, context):
        draw_dp_panel_layout(self, context)


classes = (
    DYNAMIC_PARENT_OT_create,
    DYNAMIC_PARENT_OT_enable,
    DYNAMIC_PARENT_OT_disable,
    DYNAMIC_PARENT_OT_clear,
    DYNAMIC_PARENT_OT_bake,
    DYNAMIC_PARENT_MT_clear_menu,
    DYNAMIC_PARENT_PT_ui_animation,
    DYNAMIC_PARENT_PT_ui_item,
    DYNAMIC_PARENT_PT_ui_tool,
    DYNAMIC_PARENT_PT_ui_dp,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
