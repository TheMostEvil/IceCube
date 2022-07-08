#Libraries
import bpy
import os
import bpy.utils.previews
from bpy.props import EnumProperty
from bpy.types import WindowManager
from sys import platform

#Custom Libraries
from .defs import isRigSelected, main_face, getFiles, GetListIndex
from . import inventory_system
from . import operators
from . import properties

#UI Panels
from .ui_files import credits_info

from .ui_files.main import bone_layers, general_settings
from .ui_files.customization import custom_general, mesh, misc
from .ui_files.materials import skin_material, eye_material, misc_material
from .ui_files.advanced import dlc_ui, parenting, downloads

#File Variables
rig_id = "ice_cube"
script_file = script_file = os.path.realpath(__file__)

#InFileDefs
def presets_menu(self, context):
    """presets menu thing"""
    enum_items = []

    if context is None:
        return enum_items


    script_file = os.path.realpath(__file__)
    try:
        selected_file = operators.files_list[context.scene.get("selected_asset")]
        thumbnail_directory = os.path.dirname(script_file)+"/internal_files/user_packs/rigs/"+selected_file+"/thumbnails"
    except:
        thumbnail_directory = os.path.dirname(script_file)+"/internal_files/important/thumbnails"

    filepath  = thumbnail_directory


    wm = context.window_manager
    directory = filepath

    pcoll = preview_collections["main"]

    if directory == pcoll.my_previews_presets:
        return pcoll.my_previews_presets


    if directory and os.path.exists(directory):
        image_paths = []
        for img in os.listdir(directory):
            if img.lower().endswith(".png"):
                image_paths.append(img)

        for i, name in enumerate(image_paths):
            filepath = os.path.join(directory, name)
            icon = pcoll.get(name)
            if not icon:
                thumb = pcoll.load(name, filepath, 'IMAGE')
            else:
                thumb = pcoll[name]
            enum_items.append((name, name, "", thumb.icon_id, i))

    pcoll.my_previews_presets = enum_items
    pcoll.my_previews_presets_dir = directory
    return pcoll.my_previews_presets

def inventory_menu(self, context):
    """inventory menu thing"""
    enum_items = []

    if context is None:
        return enum_items


    script_file = os.path.realpath(__file__)
    try:
        selected_file = inventory_system.inv_files_list[context.scene.get("selected_inv_asset")]
        thumbnail_directory = os.path.dirname(script_file)+"/internal_files/user_packs/inventory/"+selected_file+"/thumbnails"
    except:
        thumbnail_directory = os.path.dirname(script_file)+"/internal_files/important/thumbnails"

    filepath  = thumbnail_directory


    wm = context.window_manager
    directory = filepath

    pcoll = preview_collections["main"]

    if directory == pcoll.inventory_preview:
        return pcoll.inventory_preview


    if directory and os.path.exists(directory):
        image_paths = []
        for img in os.listdir(directory):
            if img.lower().endswith(".png"):
                image_paths.append(img)

        for i, name in enumerate(image_paths):
            filepath = os.path.join(directory, name)
            icon = pcoll.get(name)
            if not icon:
                thumb = pcoll.load(name, filepath, 'IMAGE')
            else:
                thumb = pcoll[name]
            enum_items.append((name, name, "", thumb.icon_id, i))

    pcoll.inventory_preview = enum_items
    pcoll.inventory_preview_dir = directory
    return pcoll.inventory_preview

def skins_menu(self, context):
    """skins menu thing"""
    enum_items = []

    if context is None:
        return enum_items

    script_file = os.path.realpath(__file__)
    skin_path = os.path.dirname(script_file)+"/internal_files/skins"

    filepath  = skin_path

    wm = context.window_manager
    directory = filepath

    pcoll = preview_collections["main"]

    if directory == pcoll.skins_folder:
        return pcoll.skins_folder

    if directory and os.path.exists(directory):
        image_paths = []
        for img in os.listdir(directory):
            if img.lower().endswith(".png"):
                image_paths.append(img)

        for i, name in enumerate(image_paths):
            filepath = os.path.join(directory, name)
            icon = pcoll.get(name)
            if not icon:
                thumb = pcoll.load(name, filepath, 'IMAGE')
            else:
                thumb = pcoll[name]
            enum_items.append((name, name, "", thumb.icon_id, i))

    pcoll.skins_folder = enum_items
    pcoll.skins_folder_dir = directory
    return pcoll.skins_folder

class IC_Panel(bpy.types.Panel):
    bl_label = "Ice Cube"
    bl_idname = "ice_cube_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Ice Cube'
    
    @classmethod
    def poll(self, context):
        rig = isRigSelected(context)
        try:
            return (rig.data.get("rig_id") == rig_id)
        except (AttributeError, KeyError, TypeError):
            return False
        
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        obj = context.object
        row = layout.row()

        #custom variables
        rig = isRigSelected(context)
        face = main_face(rig)
        skin_nodes = face.material_slots[0].material.node_tree
        skin_mat = skin_nodes.nodes['Skin Tex']

        #Draw the panel
        credits_info.credits_ui_panel(self,context)

        #tab switcher
        box = layout.box() #UNCOMMENTING WILL DRAW BOX
        b = box.row(align=True)
        b.label(text= "Settings Tab", icon= 'EVENT_TAB')
        b = box.row(align=True)
        b.prop(obj, "ipaneltab1", text = "the funny", expand=True)
        b = box.row(align=True)
        for i in range(0,4):
            if obj.get("ipaneltab1") == i:
                b.prop(obj, f"ipaneltab{str(i + 2)}", text = "the funny", expand=True)
        if obj.get("ipaneltab1") == 3 and obj.get("ipaneltab5") == 0:
            b = box.row(align=True)
            b.prop(obj, "ipaneltab6", text = "the funny", expand=True)
        
        #tabs/Main
        if obj.get("ipaneltab1") == 0: #Main
            if obj.get("ipaneltab2") == 0: #Bone Layers
                bone_layers.bone_layers_UI(self, context, layout)
            if obj.get("ipaneltab2") == 1: #General Settings
                general_settings.general_settings_main_UI(self, context, layout, obj, preview_collections)
        #tabs/Customization
        if obj.get("ipaneltab1") == 1: #Customization
            if obj.get("ipaneltab3") == 0: #General
                custom_general.customization_general_UI(self, context, layout, obj)
            if obj.get("ipaneltab3") == 1: #Mesh
                mesh.custom_mesh_UI(self, context, layout, obj)
            if obj.get("ipaneltab3") == 2: #Misc
                misc.custom_misc_UI(self, context, layout, obj)
        #tabs/Materials
        if obj.get("ipaneltab1") == 2: #Materials
            if obj.get("ipaneltab4") == 0: #Skin
                skin_material.skin_material_UI(self, context, layout, skin_mat, face)
            if obj.get("ipaneltab4") == 1: #Eyes
                eye_material.eye_material_UI(self, context, layout, obj, face)
            if obj.get("ipaneltab4") == 2: #Misc
                misc_material.misc_material_UI(self, context, layout, face)
        #tabs/Advanced
        if obj.get("ipaneltab1") == 3: #Advanced
            if obj.get("ipaneltab5") == 0: #DLC
                if obj.get("ipaneltab6") == 0: #Assets
                    dlc_ui.dlc_assets_UI(self, context, script_file, layout, inventory_system.inv_files_list)
                if obj.get("ipaneltab6") == 1: #Presets
                    dlc_ui.dlc_presets_UI(self, context, script_file, layout, operators.files_list, properties.global_rig_baked)
            if obj.get("ipaneltab5") == 1: #Parenting
                parenting.parenting_UI(self, context, layout, properties.global_rig_baked)
            if obj.get("ipaneltab5") == 2: #Downloads
                downloads.downloads_UI(self, context, layout, obj, script_file, properties.update_available, getFiles, GetListIndex, operators.dlc_id, operators.dlc_type, operators.dlc_author)

def menu_function_thing(self, context):
    pcoll = preview_collections["main"]
    my_icon = pcoll["DarthLilo"]
    self.layout.menu("IceCubeAppendMenu", text = "Ice Cube Rig", icon_value = my_icon.icon_id)

class IceCubeAppendMenu(bpy.types.Menu):
        bl_label = "Append Rig"
        bl_idname = "IceCubeAppendMenu"
        bl_options = bl_options = {'REGISTER', 'UNDO'}
        
        def draw(self, context):
        
            layout = self.layout
            
            pcoll = preview_collections["main"]
            
            my_icon = pcoll["Steve"]
            layout.operator("append.defaultrig", icon_value = my_icon.icon_id)

class ToolsAppendMenu(bpy.types.Panel):
    bl_label = "Append Preset"
    bl_idname = "ToolsAppendIceCube"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        obj = context.object
        row = layout.row()

        dlc_ui.dlc_presets_UI(self, context, script_file, layout, operators.files_list, properties.global_rig_baked)



#Register

classes = [IC_Panel,
           ToolsAppendMenu,
           IceCubeAppendMenu
           ]
           
modules = (
            operators,
          )

preview_collections = {}

def register():
    WindowManager.my_previews_presets = EnumProperty(
        items=presets_menu)

    WindowManager.skins_folder = EnumProperty(
        items=skins_menu)
    
    WindowManager.inventory_preview = EnumProperty(
       items=inventory_menu)

    pcoll = bpy.utils.previews.new()
    
    my_icons_dir = os.path.join(os.path.dirname(__file__), "icons")
    pcoll.load("DarthLilo", os.path.join(my_icons_dir, "DarthLilo.png"), 'IMAGE')
    pcoll.load("Alex", os.path.join(my_icons_dir, "Alex.png"), 'IMAGE')
    pcoll.load("Steve", os.path.join(my_icons_dir, "Steve.png"), 'IMAGE')
    
    
    
    pcoll.my_previews_presets = ""
    pcoll.my_previews_presets = ()

    pcoll.skins_folder = ""
    pcoll.skins_folder= ()

    pcoll.inventory_preview = ""
    pcoll.inventory_preview = ()
    
    preview_collections["main"] = pcoll
    
    
    for m in modules:
        m.register()
    
    from bpy.utils import register_class
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_MT_add.append(menu_function_thing)
        
def unregister():
    from bpy.types import WindowManager
    
    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()
    
    for m in modules:
        m.unregister()
    
    from bpy.utils import unregister_class
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.types.VIEW3D_MT_add.remove(menu_function_thing)
    
if __name__=="__main__":
    register()