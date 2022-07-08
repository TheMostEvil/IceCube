#Libraries
import bpy
import os
import subprocess
from urllib import request
import json
import zipfile
from sys import platform
import shutil
import distutils.dir_util
from bpy.props import EnumProperty

#Custom Libraries
from . import properties
from . import bl_info
from .defs import isRigSelected, CustomErrorBox, CustomLink, GetListIndex, IsVersionUpdated, getFiles, ClearDirectory

#file variables
final_list = []
files_list = []
rig_id = "ice_cube"

mainfile = os.path.realpath(__file__)
internalfiles = os.path.dirname(mainfile)
internalfiles = os.path.join(internalfiles, "internal_files/user_packs/rigs")
user_packs = os.path.normpath(internalfiles)
get_test_files = getFiles(user_packs)
count = 0
try:
    for file in get_test_files:
        count += 1
        addition_map = ["rig_", str(count)]
        ID = "".join(addition_map)
        description = "Rig ID Number: " + ID
        test_thing = (ID, file, description)
        final_list.append(test_thing)
        files_list.append(file)
except:
    pass



class rig_baked_class(bpy.types.Operator):
    """Changes whether the imported rig is baked or not"""
    bl_idname = "rig.bakedbutton"
    bl_label = "Is the rig baked?"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        obj = context.object

        properties.global_rig_baked = not properties.global_rig_baked
        

        return {'FINISHED'}

class parent_struct_class(bpy.types.Operator):
    """Only applies when using the \"_IgnoreBend\" tag"""
    bl_idname = "rig.parentstruct"
    bl_label = "Which half of the part do you want to parent the asset to?"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        obj = context.object

        properties.global_parent_half = not properties.global_parent_half
        

        return {'FINISHED'}

class append_preset(bpy.types.Operator):
    """Imports a preset or rig from your library"""
    bl_idname = "append.preset"
    bl_label = "append preset"
    bl_options = {'REGISTER', 'UNDO'}
    
    
    def execute(self, context):
        #sets up variables
        normals = {};
        baked = {};
        obj = context.object
        script_file = os.path.realpath(__file__)
        try:
            selected_file = files_list[context.scene.get("selected_asset")]
            asset_directory = os.path.dirname(script_file)+"/internal_files/user_packs/rigs/"+selected_file+"/rigs"
            thumbnails_directory = os.path.dirname(script_file)+"/internal_files/user_packs/rigs/"+selected_file+"/thumbnails"
        except:
            selected_file = "important"
            asset_directory = os.path.dirname(script_file)+"/internal_files/"+selected_file+"/rigs"
            thumbnails_directory = os.path.dirname(script_file)+"/internal_files/"+selected_file+"/thumbnails"
        asset_directory = os.path.normpath(asset_directory)
        thumbnails_directory = os.path.normpath(thumbnails_directory)

        dirs = getFiles(asset_directory)

        try:
            for dir in dirs:
                newDir = os.path.join(asset_directory, dir);

                for file in os.listdir(newDir):
                
                    newFile = os.path.join(newDir, file)
                    if (file.__contains__('BAKED')):
                        baked[dir] = newFile;
                    elif (file.__contains__('NORMAL')):
                        normals[dir] = newFile;
        except:
            CustomErrorBox(message="Unknown Error", title="Append Exception", icon='ERROR')
        
        thumbnailnopngmis = bpy.data.window_managers["WinMan"].my_previews_presets.split(".")[0]

        #detects if the current preset is baked or not
        def getPreset(thumbnail, isBaked):
            try:
                if isBaked:
                    return baked[thumbnail];
                else:
                    return normals[thumbnail];
            except KeyError:
                if properties.global_rig_baked == True:
                    CustomErrorBox("Missing \'BAKED\' file.","Append Exception",'ERROR')
                elif properties.global_rig_baked == False:
                    CustomErrorBox("Missing \'NORMAL\' file.", "Append Exception", 'ERROR')
                elif():
                    CustomErrorBox(message="Couldn't find file or folder for \""+thumbnailnopngmis+"\" from \""+selected_file+"\"", title="Append Exception", icon='ERROR')
            except:
                CustomErrorBox("Unknown Error" "Append Exception", 'ERROR')

        #sets up appending variables
        thumbnail = bpy.data.window_managers["WinMan"].my_previews_presets
        thumbnailnopng = thumbnail.split(".")[0]

        blendfile = getPreset(thumbnailnopng,properties.global_rig_baked)
        if properties.global_rig_baked == True:
            isBaked = "_BAKED"
        else:
            isBaked = "_NORMAL"
        blendfile_name = thumbnailnopng+isBaked+".blend"
        section = "Collection"
        obj = thumbnailnopng


        #Attemps to append it based on the previously established variables, if not, draw a custom error box
        try:
            filepath  = os.path.join(blendfile,section,obj)
            directory = os.path.join(blendfile,section)
            filename  = obj
            bpy.ops.wm.append(filepath=filepath,filename=filename,directory=directory,link=False,active_collection=True)
            CustomErrorBox("Appended \""+thumbnailnopng+"\" from \""+blendfile_name+"\" in \""+selected_file+"\"", "Operation Completed", 'CHECKMARK')
        except:
            CustomErrorBox("An unknown error has occured.", "Unknown Error", 'ERROR')

        return{'FINISHED'}

class append_defaultrig(bpy.types.Operator):
    """Appends the default rig into your scene"""
    bl_idname = "append.defaultrig"
    bl_label = "Ice Cube [DEFAULT]"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        #sets up variables
        script_file = os.path.realpath(__file__)
        
        script_directory = os.path.dirname(script_file)
        script_directory = os.path.join(script_directory, "rigs")
        script_directory = os.path.normpath(script_directory)
        blendfile = os.path.join(script_directory, "Ice Cube.blend")
        section = "Collection"
        obj = "Ice Cube"
        filepath = os.path.join(blendfile,section,obj)
        directory = os.path.join(blendfile,section)
        filename = obj
        #appends the rig
        bpy.ops.wm.append(filepath=filepath,filename=filename,directory=directory,link=False,active_collection=True)
        return {'FINISHED'}

class parent_leftarm(bpy.types.Operator):
    """Parents anything with the \"_LeftArmChild\" tag to the left arm"""
    bl_idname = "parent.leftarm"
    bl_label = "parent left arm"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        #lists
        named_meshes_list = []
        ignore_bend_meshes_list = []
        dynamic_obj_L_list = []
        #terms
        no_bend_term = ["_IgnoreBend"]
        key_term = ["_LeftArmChild"]
        dynamic_objs_L = ["Arm Twist Empty L", "Arm Deform LAT L", "Arm Bulge LAT L", "Arm Squish LAT L", "Lattice SMOOTH Arm L", "Sharp LAT Arm L"]
        #other variables
        bl_str = ""
        key_term_to_str = (bl_str.join(key_term))
        no_bend_term_to_str = (bl_str.join(no_bend_term))
        rig = isRigSelected(context)


        #checks if they have the proper name
        for obj in bpy.data.objects:
            if any(x in obj.name for x in key_term):
                if any(x in obj.name for x in no_bend_term):
                    ignore_bend_meshes_list.append(obj.name)
                else:
                    named_meshes_list.append(obj.name)
        for obj in rig.children:
            if any(x in obj.name for x in dynamic_objs_L):
                dynamic_obj_L_list.append(obj.name)


        #gives the meshes their attributes
        for obj in named_meshes_list:
            left_leg_parent = bpy.data.objects[obj]
            rig = isRigSelected(context)
            
            

            #Arm Deform
            modifier = left_leg_parent.modifiers.new(name="Arm Deform", type='LATTICE')
            modifier.object = bpy.data.objects[dynamic_obj_L_list[GetListIndex("Arm Deform LAT L", dynamic_obj_L_list)]]

            #Arm Bulge
            modifier = left_leg_parent.modifiers.new(name="Arm Bulge", type='LATTICE')
            modifier.object = bpy.data.objects[dynamic_obj_L_list[GetListIndex("Arm Bulge LAT L", dynamic_obj_L_list)]]

            #twist
            modifier = left_leg_parent.modifiers.new(name="Twist", type='SIMPLE_DEFORM')
            modifier.deform_method = 'TWIST'
            modifier.deform_axis = 'Z'
            modifier.origin = bpy.data.objects[dynamic_obj_L_list[GetListIndex("Arm Twist Empty L", dynamic_obj_L_list)]]

            spot = modifier.driver_add("angle")
            driver = spot.driver
            driver.type = 'AVERAGE'
            var = driver.variables.new()
            var.type = 'TRANSFORMS'
            var.name = "twist"
            target = var.targets[0]
            target.id = rig
            target.bone_target = "Arm Twist L"
            target.transform_type = 'ROT_Y'
            target.rotation_mode = 'AUTO'
            target.transform_space = 'LOCAL_SPACE'

            #Arm Squish
            modifier = left_leg_parent.modifiers.new(name="Arm Squish", type='LATTICE')
            modifier.object = bpy.data.objects[dynamic_obj_L_list[GetListIndex("Arm Squish LAT L", dynamic_obj_L_list)]]

            spot = modifier.driver_add("show_viewport")
            driver = spot.driver
            driver.type = 'SCRIPTED'
            var = driver.variables.new()
            var.type = 'SINGLE_PROP'
            var.name = "var"
            target = var.targets[0]
            target.id_type = 'OBJECT'
            target.id = rig
            target.data_path = "[\"antilag\"]"
            driver.expression = "+1 -var"

            #Smooth Bend
            modifier = left_leg_parent.modifiers.new(name="Smooth Bend", type='LATTICE')
            modifier.object = bpy.data.objects[dynamic_obj_L_list[GetListIndex("Lattice SMOOTH Arm L", dynamic_obj_L_list)]]

            spot = modifier.driver_add("strength")
            driver = spot.driver
            driver.type = 'SCRIPTED'
            var = driver.variables.new()
            var.type = 'SINGLE_PROP'
            var.name = "var"
            target = var.targets[0]
            target.id_type = 'OBJECT'
            target.id = rig
            target.data_path = "[\"bendstyle\"]"
            driver.expression = "1 if (var==1) else 0"

            #Sharp Bend
            modifier = left_leg_parent.modifiers.new(name="Sharp Bend", type='LATTICE')
            modifier.object = bpy.data.objects[dynamic_obj_L_list[GetListIndex("Sharp LAT Arm L", dynamic_obj_L_list)]]

            spot = modifier.driver_add("strength")
            driver = spot.driver
            driver.type = 'SCRIPTED'
            var = driver.variables.new()
            var.type = 'SINGLE_PROP'
            var.name = "var"
            target = var.targets[0]
            target.id_type = 'OBJECT'
            target.id = rig
            target.data_path = "[\"bendstyle\"]"
            driver.expression = "1 if (var==0) else 0"

            #Parenting
            left_leg_parent.parent = rig

        #make the lower or upper parenting system
        for obj in ignore_bend_meshes_list:
            left_leg_parent = bpy.data.objects[obj]
            rig = isRigSelected(context)

            

            #Arm Deform
            modifier = left_leg_parent.modifiers.new(name="Arm Deform", type='LATTICE')
            modifier.object = bpy.data.objects[dynamic_obj_L_list[GetListIndex("Arm Deform LAT L", dynamic_obj_L_list)]]

            #Arm Bulge
            modifier = left_leg_parent.modifiers.new(name="Arm Bulge", type='LATTICE')
            modifier.object = bpy.data.objects[dynamic_obj_L_list[GetListIndex("Arm Bulge LAT L", dynamic_obj_L_list)]]

            #twist
            modifier = left_leg_parent.modifiers.new(name="Twist", type='SIMPLE_DEFORM')
            modifier.deform_method = 'TWIST'
            modifier.deform_axis = 'Z'
            modifier.origin = bpy.data.objects[dynamic_obj_L_list[GetListIndex("Arm Twist Empty L", dynamic_obj_L_list)]]

            spot = modifier.driver_add("angle")
            driver = spot.driver
            driver.type = 'AVERAGE'
            var = driver.variables.new()
            var.type = 'TRANSFORMS'
            var.name = "twist"
            target = var.targets[0]
            target.id = rig
            target.bone_target = "Arm Twist L"
            target.transform_type = 'ROT_Y'
            target.rotation_mode = 'AUTO'
            target.transform_space = 'LOCAL_SPACE'

            #Arm Squish
            modifier = left_leg_parent.modifiers.new(name="Arm Squish", type='LATTICE')
            modifier.object = bpy.data.objects[dynamic_obj_L_list[GetListIndex("Arm Squish LAT L", dynamic_obj_L_list)]]

            spot = modifier.driver_add("show_viewport")
            driver = spot.driver
            driver.type = 'SCRIPTED'
            var = driver.variables.new()
            var.type = 'SINGLE_PROP'
            var.name = "var"
            target = var.targets[0]
            target.id_type = 'OBJECT'
            target.id = rig
            target.data_path = "[\"antilag\"]"
            driver.expression = "+1 -var"

            #refresh
            bpy.context.view_layer.update()
            #Parenting Variable Setup
            objP = left_leg_parent
            rigP = rig
            if properties.global_parent_half == True:
                bone = rig.pose.bones["Arm Lower L"]
            else:
                bone = rig.pose.bones["Arm Upper L"]
            #save position data
            test_matrix = objP.matrix_world.copy()
            #parent objects
            objP.parent = rigP
            objP.parent_bone = bone.name
            objP.parent_type = 'BONE'
            objP.matrix_world = test_matrix
            


            
            




        #removes the key term from the name
        for obj in ignore_bend_meshes_list:
            clean_mesh_name = (obj.split(no_bend_term_to_str)[0])
            clean_mesh_name = (clean_mesh_name.split(key_term_to_str)[0])
            bpy.data.objects[obj].name = clean_mesh_name

        for obj in named_meshes_list:
            clean_mesh_name = (obj.split(key_term_to_str)[0])
            bpy.data.objects[obj].name = clean_mesh_name

        #error message
        
        if obj in named_meshes_list:
            pass
        elif obj in ignore_bend_meshes_list:
            pass
        else:
            CustomErrorBox("Nothing to parent!", "Parenting Exception", 'ERROR')
        
        return {'FINISHED'}

class parent_rightarm(bpy.types.Operator):
    """Parents anything with the \"_RightArmChild\" tag to the right arm"""
    bl_idname = "parent.rightarm"
    bl_label = "parent right arm"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        
        named_meshes_list = []
        ignore_bend_meshes_list = []
        dynamic_obj_R_list = []
        no_bend_term = ["_IgnoreBend"]
        key_term = ["_RightArmChild"]
        dynamic_objs_R = ["Arm Twist Empty R", "Arm Deform LAT R", "Arm Bulge LAT R", "Arm Squish LAT R", "Lattice SMOOTH Arm R", "Sharp LAT Arm R"]
        bl_str = ""
        key_term_to_str = (bl_str.join(key_term))
        no_bend_term_to_str = (bl_str.join(key_term))
        rig = isRigSelected(context)

        #checks if they have the proper name
        for obj in bpy.data.objects:
            if any(x in obj.name for x in key_term):
                if any(x in obj.name for x in no_bend_term):
                    ignore_bend_meshes_list.append(obj.name)
                else:
                    named_meshes_list.append(obj.name)

        for obj in rig.children:
            if any(x in obj.name for x in dynamic_objs_R):
                dynamic_obj_R_list.append(obj.name)



        #gives the meshes their attributes
        for obj in named_meshes_list:
            right_leg_parent = bpy.data.objects[obj]
            rig = isRigSelected(context)


            #Arm Deform
            modifier = right_leg_parent.modifiers.new(name="Arm Deform", type='LATTICE')
            modifier.object = bpy.data.objects[dynamic_obj_R_list[GetListIndex("Arm Deform LAT R", dynamic_obj_R_list)]]

            #Arm Bulge
            modifier = right_leg_parent.modifiers.new(name="Arm Bulge", type='LATTICE')
            modifier.object = bpy.data.objects[dynamic_obj_R_list[GetListIndex("Arm Bulge LAT R", dynamic_obj_R_list)]]

            #twist
            modifier = right_leg_parent.modifiers.new(name="Twist", type='SIMPLE_DEFORM')
            modifier.deform_method = 'TWIST'
            modifier.deform_axis = 'Z'
            modifier.origin = bpy.data.objects[dynamic_obj_R_list[GetListIndex("Arm Twist Empty R", dynamic_obj_R_list)]]

            spot = modifier.driver_add("angle")
            driver = spot.driver
            driver.type = 'AVERAGE'
            var = driver.variables.new()
            var.type = 'TRANSFORMS'
            var.name = "twist"
            target = var.targets[0]
            target.id = rig
            target.bone_target = "Arm Twist R"
            target.transform_type = 'ROT_Y'
            target.rotation_mode = 'AUTO'
            target.transform_space = 'LOCAL_SPACE'

            #Arm Squish
            modifier = right_leg_parent.modifiers.new(name="Arm Squish", type='LATTICE')
            modifier.object = bpy.data.objects[dynamic_obj_R_list[GetListIndex("Arm Squish LAT R", dynamic_obj_R_list)]]

            spot = modifier.driver_add("show_viewport")
            driver = spot.driver
            driver.type = 'SCRIPTED'
            var = driver.variables.new()
            var.type = 'SINGLE_PROP'
            var.name = "var"
            target = var.targets[0]
            target.id_type = 'OBJECT'
            target.id = rig
            target.data_path = "[\"antilag\"]"
            driver.expression = "+1 -var"

            #Smooth Bend
            modifier = right_leg_parent.modifiers.new(name="Smooth Bend", type='LATTICE')
            modifier.object = bpy.data.objects[dynamic_obj_R_list[GetListIndex("Lattice SMOOTH Arm R", dynamic_obj_R_list)]]

            spot = modifier.driver_add("strength")
            driver = spot.driver
            driver.type = 'SCRIPTED'
            var = driver.variables.new()
            var.type = 'SINGLE_PROP'
            var.name = "var"
            target = var.targets[0]
            target.id_type = 'OBJECT'
            target.id = rig
            target.data_path = "[\"bendstyle\"]"
            driver.expression = "1 if (var==1) else 0"

            #Sharp Bend
            modifier = right_leg_parent.modifiers.new(name="Sharp Bend", type='LATTICE')
            modifier.object = bpy.data.objects[dynamic_obj_R_list[GetListIndex("Sharp LAT Arm R", dynamic_obj_R_list)]]

            spot = modifier.driver_add("strength")
            driver = spot.driver
            driver.type = 'SCRIPTED'
            var = driver.variables.new()
            var.type = 'SINGLE_PROP'
            var.name = "var"
            target = var.targets[0]
            target.id_type = 'OBJECT'
            target.id = rig
            target.data_path = "[\"bendstyle\"]"
            driver.expression = "1 if (var==0) else 0"

            #Parenting
            right_leg_parent.parent = rig

            

        #ignore attributes
        for obj in ignore_bend_meshes_list:
            right_leg_parent = bpy.data.objects[obj]
            rig = isRigSelected(context)

            

            #Arm Deform
            modifier = right_leg_parent.modifiers.new(name="Arm Deform", type='LATTICE')
            modifier.object = bpy.data.objects[dynamic_obj_R_list[GetListIndex("Arm Deform LAT R", dynamic_obj_R_list)]]

            #Arm Bulge
            modifier = right_leg_parent.modifiers.new(name="Arm Bulge", type='LATTICE')
            modifier.object = bpy.data.objects[dynamic_obj_R_list[GetListIndex("Arm Bulge LAT R", dynamic_obj_R_list)]]

            #twist
            modifier = right_leg_parent.modifiers.new(name="Twist", type='SIMPLE_DEFORM')
            modifier.deform_method = 'TWIST'
            modifier.deform_axis = 'Z'
            modifier.origin = bpy.data.objects[dynamic_obj_R_list[GetListIndex("Arm Twist Empty R", dynamic_obj_R_list)]]

            spot = modifier.driver_add("angle")
            driver = spot.driver
            driver.type = 'AVERAGE'
            var = driver.variables.new()
            var.type = 'TRANSFORMS'
            var.name = "twist"
            target = var.targets[0]
            target.id = rig
            target.bone_target = "Arm Twist R"
            target.transform_type = 'ROT_Y'
            target.rotation_mode = 'AUTO'
            target.transform_space = 'LOCAL_SPACE'

            #Arm Squish
            modifier = right_leg_parent.modifiers.new(name="Arm Squish", type='LATTICE')
            modifier.object = bpy.data.objects[dynamic_obj_R_list[GetListIndex("Arm Squish LAT R", dynamic_obj_R_list)]]

            spot = modifier.driver_add("show_viewport")
            driver = spot.driver
            driver.type = 'SCRIPTED'
            var = driver.variables.new()
            var.type = 'SINGLE_PROP'
            var.name = "var"
            target = var.targets[0]
            target.id_type = 'OBJECT'
            target.id = rig
            target.data_path = "[\"antilag\"]"
            driver.expression = "+1 -var"

            #refresh
            bpy.context.view_layer.update()
            #Parenting Variable Setup
            objP = right_leg_parent
            rigP = rig
            if properties.global_parent_half == True:
                bone = rig.pose.bones["Arm Lower R"]
            else:
                bone = rig.pose.bones["Arm Upper R"]
            #save position data
            test_matrix = objP.matrix_world.copy()
            #parent objects
            objP.parent = rigP
            objP.parent_bone = bone.name
            objP.parent_type = 'BONE'
            objP.matrix_world = test_matrix


        #removes the key term from the name
        for obj in ignore_bend_meshes_list:
            clean_mesh_name = (obj.split(no_bend_term_to_str)[0])
            clean_mesh_name = (clean_mesh_name.split(key_term_to_str)[0])
            bpy.data.objects[obj].name = clean_mesh_name

        for obj in named_meshes_list:
            clean_mesh_name = (obj.split(key_term_to_str)[0])
            bpy.data.objects[obj].name = clean_mesh_name

        #error message
        if obj in named_meshes_list:
            pass
        elif obj in ignore_bend_meshes_list:
            pass
        else:
            CustomErrorBox("Nothing to parent!", "Parenting Exception", 'ERROR')
        
        return {'FINISHED'}

class parent_rightleg(bpy.types.Operator):
    """Parents anything with the \"_RightLegChild\" tag to the right leg"""
    bl_idname = "parent.rightleg"
    bl_label = "parent right leg"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        rig = isRigSelected(context)
        named_meshes_list = []
        ignore_bend_meshes_list = []
        dynamic_obj_R_leg_list = []
        no_bend_term = ["_IgnoreBend"]
        key_term = ["_RightLegChild"]
        dynamic_objs_R_leg = ["Leg Twist Empty R", "Leg Deform LAT R", "Leg Bulge LAT R", "Leg Squish LAT R", "Lattice SMOOTH R", "Sharp LAT R"]
        bl_str = ""
        key_term_to_str = (bl_str.join(key_term))
        no_bend_term_to_str = (bl_str.join(no_bend_term))

        #checks if they have the proper name
        for obj in bpy.data.objects:
            if any(x in obj.name for x in key_term):
                if any(x in obj.name for x in no_bend_term):
                    ignore_bend_meshes_list.append(obj.name)
                else:
                    named_meshes_list.append(obj.name)
        for obj in rig.children:
            if any(x in obj.name for x in dynamic_objs_R_leg):
                dynamic_obj_R_leg_list.append(obj.name)

        #gives the meshes their attributes
        for obj in named_meshes_list:
            right_leg_parent = bpy.data.objects[obj]
            rig = isRigSelected(context)


            #Arm Deform
            modifier = right_leg_parent.modifiers.new(name="Leg Deform", type='LATTICE')
            modifier.object = bpy.data.objects[dynamic_obj_R_leg_list[GetListIndex("Leg Deform LAT R", dynamic_obj_R_leg_list)]]

            #Arm Bulge
            modifier = right_leg_parent.modifiers.new(name="Leg Bulge", type='LATTICE')
            modifier.object = bpy.data.objects[dynamic_obj_R_leg_list[GetListIndex("Leg Bulge LAT R", dynamic_obj_R_leg_list)]]


            #Simple Deform
            modifier = right_leg_parent.modifiers.new(name="Twist", type='SIMPLE_DEFORM')
            modifier.deform_method = 'TWIST'
            modifier.deform_axis = 'Z'
            modifier.origin = bpy.data.objects[dynamic_obj_R_leg_list[GetListIndex("Leg Twist Empty R", dynamic_obj_R_leg_list)]]

            spot = modifier.driver_add("angle")
            driver = spot.driver
            driver.type = 'AVERAGE'
            var = driver.variables.new()
            var.type = 'TRANSFORMS'
            var.name = "twist"
            target = var.targets[0]
            target.id = rig
            target.bone_target = "Leg Twist R"
            target.transform_type = 'ROT_Y'
            target.rotation_mode = 'AUTO'
            target.transform_space = 'LOCAL_SPACE'

            #Arm Squish
            modifier = right_leg_parent.modifiers.new(name="Leg Squish", type='LATTICE')
            modifier.object = bpy.data.objects[dynamic_obj_R_leg_list[GetListIndex("Leg Squish LAT R", dynamic_obj_R_leg_list)]]

            spot = modifier.driver_add("show_viewport")
            driver = spot.driver
            driver.type = 'SCRIPTED'
            var = driver.variables.new()
            var.type = 'SINGLE_PROP'
            var.name = "var"
            target = var.targets[0]
            target.id_type = 'OBJECT'
            target.id = rig
            target.data_path = "[\"antilag\"]"
            driver.expression = "+1 -var"

            #Smooth Bend
            modifier = right_leg_parent.modifiers.new(name="Smooth Bend", type='LATTICE')
            modifier.object = bpy.data.objects[dynamic_obj_R_leg_list[GetListIndex("Lattice SMOOTH R", dynamic_obj_R_leg_list)]]

            spot = modifier.driver_add("strength")
            driver = spot.driver
            driver.type = 'SCRIPTED'
            var = driver.variables.new()
            var.type = 'SINGLE_PROP'
            var.name = "var"
            target = var.targets[0]
            target.id_type = 'OBJECT'
            target.id = rig
            target.data_path = "[\"bendstyle\"]"
            driver.expression = "1 if (var==1) else 0"

            #Sharp Bend
            modifier = right_leg_parent.modifiers.new(name="Sharp Bend", type='LATTICE')
            modifier.object = bpy.data.objects[dynamic_obj_R_leg_list[GetListIndex("Sharp LAT R", dynamic_obj_R_leg_list)]]

            spot = modifier.driver_add("strength")
            driver = spot.driver
            driver.type = 'SCRIPTED'
            var = driver.variables.new()
            var.type = 'SINGLE_PROP'
            var.name = "var"
            target = var.targets[0]
            target.id_type = 'OBJECT'
            target.id = rig
            target.data_path = "[\"bendstyle\"]"
            driver.expression = "1 if (var==0) else 0"

            #Parenting
            right_leg_parent.parent = rig

            
    
        for obj in ignore_bend_meshes_list:
            right_leg_parent = bpy.data.objects[obj]
            rig = isRigSelected(context)


            #Arm Deform
            modifier = right_leg_parent.modifiers.new(name="Leg Deform", type='LATTICE')
            modifier.object = bpy.data.objects[dynamic_obj_R_leg_list[GetListIndex("Leg Deform LAT R", dynamic_obj_R_leg_list)]]

            #Arm Bulge
            modifier = right_leg_parent.modifiers.new(name="Leg Bulge", type='LATTICE')
            modifier.object = bpy.data.objects[dynamic_obj_R_leg_list[GetListIndex("Leg Bulge LAT R", dynamic_obj_R_leg_list)]]

            #Simple Deform
            modifier = right_leg_parent.modifiers.new(name="Twist", type='SIMPLE_DEFORM')
            modifier.deform_method = 'TWIST'
            modifier.deform_axis = 'Z'
            modifier.origin = bpy.data.objects[dynamic_obj_R_leg_list[GetListIndex("Leg Twist Empty R", dynamic_obj_R_leg_list)]]

            spot = modifier.driver_add("angle")
            driver = spot.driver
            driver.type = 'AVERAGE'
            var = driver.variables.new()
            var.type = 'TRANSFORMS'
            var.name = "twist"
            target = var.targets[0]
            target.id = rig
            target.bone_target = "Leg Twist R"
            target.transform_type = 'ROT_Y'
            target.rotation_mode = 'AUTO'
            target.transform_space = 'LOCAL_SPACE'

            #Arm Squish
            modifier = right_leg_parent.modifiers.new(name="Leg Squish", type='LATTICE')
            modifier.object = bpy.data.objects[dynamic_obj_R_leg_list[GetListIndex("Leg Squish LAT R", dynamic_obj_R_leg_list)]]

            spot = modifier.driver_add("show_viewport")
            driver = spot.driver
            driver.type = 'SCRIPTED'
            var = driver.variables.new()
            var.type = 'SINGLE_PROP'
            var.name = "var"
            target = var.targets[0]
            target.id_type = 'OBJECT'
            target.id = rig
            target.data_path = "[\"antilag\"]"
            driver.expression = "+1 -var"

            #refresh
            bpy.context.view_layer.update()
            #Parenting Variable Setup
            objP = right_leg_parent
            rigP = rig
            if properties.global_parent_half == True:
                bone = rig.pose.bones["Leg Lower R"]
            else:
                bone = rig.pose.bones["Leg Upper R"]
            #save position data
            test_matrix = objP.matrix_world.copy()
            #parent objects
            objP.parent = rigP
            objP.parent_bone = bone.name
            objP.parent_type = 'BONE'
            objP.matrix_world = test_matrix  

        #removes the key term from the name

        for obj in ignore_bend_meshes_list:
            clean_mesh_name = (obj.split(no_bend_term_to_str)[0])
            clean_mesh_name = (clean_mesh_name.split(key_term_to_str)[0])
            bpy.data.objects[obj].name = clean_mesh_name

        for obj in named_meshes_list:
            clean_mesh_name = (obj.split(key_term_to_str)[0])
            bpy.data.objects[obj].name = clean_mesh_name
        
        

        #error message
        if obj in named_meshes_list:
            pass
        elif obj in ignore_bend_meshes_list:
            pass
        else:
            CustomErrorBox("Nothing to parent!", "Parenting Exception", 'ERROR')
        
        return {'FINISHED'}

class parent_leftleg(bpy.types.Operator):
    """Parents anything with the \"_LeftLegChild\" tag to the left leg"""
    bl_idname = "parent.leftleg"
    bl_label = "parent left leg"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        rig = isRigSelected(context)
        named_meshes_list = []
        ignore_bend_meshes_list = []
        dynamic_obj_L_list = []
        no_bend_term = ["_IgnoreBend"]
        key_term = ["_LeftLegChild"]
        dynamic_objs_L = ["Leg Twist Empty L", "Leg Deform LAT L", "Leg Bulge LAT L", "Leg Squish LAT L", "Lattice SMOOTH L", "Sharp LAT L"]
        bl_str = ""
        key_term_to_str = (bl_str.join(key_term))
        no_bend_term_to_str = (bl_str.join(no_bend_term))


        #checks if they have the proper name
        for obj in bpy.data.objects:
            if any(x in obj.name for x in key_term):
                if any(x in obj.name for x in no_bend_term):
                    ignore_bend_meshes_list.append(obj.name)
                else:
                    named_meshes_list.append(obj.name)
        
        for obj in rig.children:
            if any(x in obj.name for x in dynamic_objs_L):
                dynamic_obj_L_list.append(obj.name)
    

        #gives the meshes their attributes
        for obj in named_meshes_list:
            left_leg_parent = bpy.data.objects[obj]
            rig = isRigSelected(context)


            #Arm Deform
            modifier = left_leg_parent.modifiers.new(name="Leg Deform", type='LATTICE')
            modifier.object = bpy.data.objects[dynamic_obj_L_list[GetListIndex("Leg Deform LAT L", dynamic_obj_L_list)]]

            #Arm Bulge
            modifier = left_leg_parent.modifiers.new(name="Leg Bulge", type='LATTICE')
            modifier.object = bpy.data.objects[dynamic_obj_L_list[GetListIndex("Leg Bulge LAT L", dynamic_obj_L_list)]]

            #Simple Deform
            modifier = left_leg_parent.modifiers.new(name="Twist", type='SIMPLE_DEFORM')
            modifier.deform_method = 'TWIST'
            modifier.deform_axis = 'Z'
            modifier.origin = bpy.data.objects[dynamic_obj_L_list[GetListIndex("Leg Twist Empty L", dynamic_obj_L_list)]]

            spot = modifier.driver_add("angle")
            driver = spot.driver
            driver.type = 'AVERAGE'
            var = driver.variables.new()
            var.type = 'TRANSFORMS'
            var.name = "twist"
            target = var.targets[0]
            target.id = rig
            target.bone_target = "Leg Twist L"
            target.transform_type = 'ROT_Y'
            target.rotation_mode = 'AUTO'
            target.transform_space = 'LOCAL_SPACE'

            #Arm Squish
            modifier = left_leg_parent.modifiers.new(name="Leg Squish", type='LATTICE')
            modifier.object = bpy.data.objects[dynamic_obj_L_list[GetListIndex("Leg Squish LAT L", dynamic_obj_L_list)]]

            spot = modifier.driver_add("show_viewport")
            driver = spot.driver
            driver.type = 'SCRIPTED'
            var = driver.variables.new()
            var.type = 'SINGLE_PROP'
            var.name = "var"
            target = var.targets[0]
            target.id_type = 'OBJECT'
            target.id = rig
            target.data_path = "[\"antilag\"]"
            driver.expression = "+1 -var"

            #Smooth Bend
            modifier = left_leg_parent.modifiers.new(name="Smooth Bend", type='LATTICE')
            modifier.object = bpy.data.objects[dynamic_obj_L_list[GetListIndex("Lattice SMOOTH L", dynamic_obj_L_list)]]

            spot = modifier.driver_add("strength")
            driver = spot.driver
            driver.type = 'SCRIPTED'
            var = driver.variables.new()
            var.type = 'SINGLE_PROP'
            var.name = "var"
            target = var.targets[0]
            target.id_type = 'OBJECT'
            target.id = rig
            target.data_path = "[\"bendstyle\"]"
            driver.expression = "1 if (var==1) else 0"

            #Sharp Bend
            modifier = left_leg_parent.modifiers.new(name="Sharp Bend", type='LATTICE')
            modifier.object = bpy.data.objects[dynamic_obj_L_list[GetListIndex("Sharp LAT L", dynamic_obj_L_list)]]

            spot = modifier.driver_add("strength")
            driver = spot.driver
            driver.type = 'SCRIPTED'
            var = driver.variables.new()
            var.type = 'SINGLE_PROP'
            var.name = "var"
            target = var.targets[0]
            target.id_type = 'OBJECT'
            target.id = rig
            target.data_path = "[\"bendstyle\"]"
            driver.expression = "1 if (var==0) else 0"

            #Parent
            left_leg_parent.parent = rig

            
        
        for obj in ignore_bend_meshes_list:
            left_leg_parent = bpy.data.objects[obj]
            rig = isRigSelected(context)


            #Arm Deform
            modifier = left_leg_parent.modifiers.new(name="Leg Deform", type='LATTICE')
            modifier.object = bpy.data.objects[dynamic_obj_L_list[GetListIndex("Leg Deform LAT L", dynamic_obj_L_list)]]

            #Arm Bulge
            modifier = left_leg_parent.modifiers.new(name="Leg Bulge", type='LATTICE')
            modifier.object = bpy.data.objects[dynamic_obj_L_list[GetListIndex("Leg Bulge LAT L", dynamic_obj_L_list)]]

            #Simple Deform
            modifier = left_leg_parent.modifiers.new(name="Twist", type='SIMPLE_DEFORM')
            modifier.deform_method = 'TWIST'
            modifier.deform_axis = 'Z'
            modifier.origin = bpy.data.objects[dynamic_obj_L_list[GetListIndex("Leg Twist Empty L", dynamic_obj_L_list)]]

            spot = modifier.driver_add("angle")
            driver = spot.driver
            driver.type = 'AVERAGE'
            var = driver.variables.new()
            var.type = 'TRANSFORMS'
            var.name = "twist"
            target = var.targets[0]
            target.id = rig
            target.bone_target = "Leg Twist L"
            target.transform_type = 'ROT_Y'
            target.rotation_mode = 'AUTO'
            target.transform_space = 'LOCAL_SPACE'

            #Arm Squish
            modifier = left_leg_parent.modifiers.new(name="Leg Squish", type='LATTICE')
            modifier.object = bpy.data.objects[dynamic_obj_L_list[GetListIndex("Leg Squish LAT L", dynamic_obj_L_list)]]

            spot = modifier.driver_add("show_viewport")
            driver = spot.driver
            driver.type = 'SCRIPTED'
            var = driver.variables.new()
            var.type = 'SINGLE_PROP'
            var.name = "var"
            target = var.targets[0]
            target.id_type = 'OBJECT'
            target.id = rig
            target.data_path = "[\"antilag\"]"
            driver.expression = "+1 -var"

            #refresh
            bpy.context.view_layer.update()
            #Parenting Variable Setup
            objP = left_leg_parent
            rigP = rig
            if properties.global_parent_half == True:
                bone = rig.pose.bones["Leg Lower L"]
            else:
                bone = rig.pose.bones["Leg Upper L"]
            #save position data
            test_matrix = objP.matrix_world.copy()
            #parent objects
            objP.parent = rigP
            objP.parent_bone = bone.name
            objP.parent_type = 'BONE'
            objP.matrix_world = test_matrix

        #removes the key term from the name
        for obj in ignore_bend_meshes_list:
            clean_mesh_name = (obj.split(no_bend_term_to_str)[0])
            clean_mesh_name = (clean_mesh_name.split(key_term_to_str)[0])
            bpy.data.objects[obj].name = clean_mesh_name

        for obj in named_meshes_list:
            clean_mesh_name = (obj.split(key_term_to_str)[0])
            bpy.data.objects[obj].name = clean_mesh_name

        #error message
        if obj in named_meshes_list:
            pass
        elif obj in ignore_bend_meshes_list:
            pass
        else:
            CustomErrorBox("Nothing to parent!", "Parenting Exception", 'ERROR')
        
        return {'FINISHED'}

class parent_body(bpy.types.Operator):
    """Parents anything with the \"_BodyChild\" tag to the body"""
    bl_idname = "parent.body"
    bl_label = "parent body"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):


        named_meshes_list = []
        ignore_bend_meshes_list = []
        dynamic_obj_list = []
        no_bend_term = ["_IgnoreBend"]
        key_term = ["_BodyChild"]
        dynamic_objs = ["Chest Lattice", "Shape_2_Chest", "BodyStretch", "BodyDeforms", "RoundedBodyTopDeform", "BodyBulge"]
        bl_str = ""
        key_term_to_str = (bl_str.join(key_term))
        no_bend_term_to_str = (bl_str.join(no_bend_term))
        rig = isRigSelected(context)

        #checks if they have the proper name
        for obj in bpy.data.objects:
            if any(x in obj.name for x in key_term):
                if any(x in obj.name for x in no_bend_term):
                    ignore_bend_meshes_list.append(obj.name)
                else:
                    named_meshes_list.append(obj.name)
        for obj in rig.children:
            if any(x in obj.name for x in dynamic_objs):
                dynamic_obj_list.append(obj.name)
        


        #gives the meshes their attributes
        for obj in named_meshes_list:
            body_parent = bpy.data.objects[obj]
            rig = isRigSelected(context)

            #weight painting
            vg = body_parent.vertex_groups.new(name="Body_Bendy")
            verts = []
            for vert in body_parent.data.vertices:
                verts.append(vert.index)
            vg.add(verts, 1.0, 'ADD')

            #Chest Lattice
            modifier = body_parent.modifiers.new(name="Chest Lattice", type='LATTICE')
            modifier.object = bpy.data.objects[dynamic_obj_list[GetListIndex("Chest Lattice", dynamic_obj_list)]]
            
            spot = modifier.driver_add("strength")
            driver = spot.driver
            driver.type = 'SCRIPTED'
            var = driver.variables.new()
            var.type = 'SINGLE_PROP'
            var.name = "var"
            target = var.targets[0]
            target.id_type = 'OBJECT'
            target.id = rig
            target.data_path = "[\"breastshape\"]"
            driver.expression = "1 -var"

            #Chest Lattice 2
            modifier = body_parent.modifiers.new(name="Chest Lattice 2", type='LATTICE')
            modifier.object = bpy.data.objects[dynamic_obj_list[GetListIndex("Shape_2_Chest", dynamic_obj_list)]]

            spot = modifier.driver_add("strength")
            driver = spot.driver
            driver.type = 'SCRIPTED'
            var = driver.variables.new()
            var.type = 'SINGLE_PROP'
            var.name = "var"
            target = var.targets[0]
            target.id_type = 'OBJECT'
            target.id = rig
            target.data_path = "[\"breastshape\"]"
            driver.expression = "var"

            #Body Deform
            modifier = body_parent.modifiers.new(name="Body Deform", type='LATTICE')
            modifier.object = bpy.data.objects[dynamic_obj_list[GetListIndex("BodyDeforms", dynamic_obj_list)]]


            #Body Stretch
            modifier = body_parent.modifiers.new(name="Body Stretch", type='LATTICE')
            modifier.object = bpy.data.objects[dynamic_obj_list[GetListIndex("BodyStretch", dynamic_obj_list)]]

        

            spot = modifier.driver_add("show_viewport")
            driver = spot.driver
            driver.type = 'SCRIPTED'
            var = driver.variables.new()
            var.type = 'SINGLE_PROP'
            var.name = "var"
            target = var.targets[0]
            target.id_type = 'OBJECT'
            target.id = rig
            target.data_path = "[\"body_deforms\"]"
            driver.expression = "var"

            #Rounded Top
            modifier = body_parent.modifiers.new(name="Rounded Top Deform", type='LATTICE')
            modifier.object = bpy.data.objects[dynamic_obj_list[GetListIndex("RoundedBodyTopDeform", dynamic_obj_list)]]

            #Body Bulge
            modifier = body_parent.modifiers.new(name="Body Bulge", type='LATTICE')
            modifier.object = bpy.data.objects[dynamic_obj_list[GetListIndex("BodyBulge", dynamic_obj_list)]]

            #Armature
            modifier = body_parent.modifiers.new(name="Ice Cube", type='ARMATURE')
            modifier.object = rig

            #Parenting
            body_parent.parent = rig


        for obj in ignore_bend_meshes_list:
            body_parent = bpy.data.objects[obj]
            rig = isRigSelected(context)

            #vg = body_parent.vertex_groups.new(name="Body_Bendy")
            #verts = []
            #for vert in body_parent.data.vertices:
            #    verts.append(vert.index)
            #vg.add(verts, 1.0, 'ADD')

            #Chest Lattice
            modifier = body_parent.modifiers.new(name="Chest Lattice", type='LATTICE')
            modifier.object = bpy.data.objects[dynamic_obj_list[GetListIndex("Chest Lattice", dynamic_obj_list)]]
            
            spot = modifier.driver_add("strength")
            driver = spot.driver
            driver.type = 'SCRIPTED'
            var = driver.variables.new()
            var.type = 'SINGLE_PROP'
            var.name = "var"
            target = var.targets[0]
            target.id_type = 'OBJECT'
            target.id = rig
            target.data_path = "[\"breastshape\"]"
            driver.expression = "1 -var"

            #Chest Lattice 2
            modifier = body_parent.modifiers.new(name="Chest Lattice 2", type='LATTICE')
            modifier.object = bpy.data.objects[dynamic_obj_list[GetListIndex("Shape_2_Chest", dynamic_obj_list)]]

            spot = modifier.driver_add("strength")
            driver = spot.driver
            driver.type = 'SCRIPTED'
            var = driver.variables.new()
            var.type = 'SINGLE_PROP'
            var.name = "var"
            target = var.targets[0]
            target.id_type = 'OBJECT'
            target.id = rig
            target.data_path = "[\"breastshape\"]"
            driver.expression = "var"

            #Body Deform
            modifier = body_parent.modifiers.new(name="Body Deform", type='LATTICE')
            modifier.object = bpy.data.objects[dynamic_obj_list[GetListIndex("BodyDeforms", dynamic_obj_list)]]


            #Body Stretch
            modifier = body_parent.modifiers.new(name="Body Stretch", type='LATTICE')
            modifier.object = bpy.data.objects[dynamic_obj_list[GetListIndex("BodyStretch", dynamic_obj_list)]]

        

            spot = modifier.driver_add("show_viewport")
            driver = spot.driver
            driver.type = 'SCRIPTED'
            var = driver.variables.new()
            var.type = 'SINGLE_PROP'
            var.name = "var"
            target = var.targets[0]
            target.id_type = 'OBJECT'
            target.id = rig
            target.data_path = "[\"body_deforms\"]"
            driver.expression = "var"

            #Rounded Top
            modifier = body_parent.modifiers.new(name="Rounded Top Deform", type='LATTICE')
            modifier.object = bpy.data.objects[dynamic_obj_list[GetListIndex("RoundedBodyTopDeform", dynamic_obj_list)]]

            #Body Bulge
            modifier = body_parent.modifiers.new(name="Body Bulge", type='LATTICE')
            modifier.object = bpy.data.objects[dynamic_obj_list[GetListIndex("BodyBulge", dynamic_obj_list)]]

            #Armature
            modifier = body_parent.modifiers.new(name="Ice Cube", type='ARMATURE')
            modifier.object = rig

            #refresh
            bpy.context.view_layer.update()
            #Parenting Variable Setup
            objP = body_parent
            rigP = rig
            if properties.global_parent_half == True:
                bone = rig.pose.bones["Body_Bendy_Start"]
            else:
                bone = rig.pose.bones["Body_Bendy_End"]
            #save position data
            test_matrix = objP.matrix_world.copy()
            #parent objects
            objP.parent = rigP
            objP.parent_bone = bone.name
            objP.parent_type = 'BONE'
            objP.matrix_world = test_matrix



        #removes the key term from the name
        for obj in ignore_bend_meshes_list:
            clean_mesh_name = (obj.split(no_bend_term_to_str)[0])
            clean_mesh_name = (clean_mesh_name.split(key_term_to_str)[0])
            bpy.data.objects[obj].name = clean_mesh_name

        for obj in named_meshes_list:
            clean_mesh_name = (obj.split(key_term_to_str)[0])
            bpy.data.objects[obj].name = clean_mesh_name

        #error message
        if obj in named_meshes_list:
            pass
        elif obj in ignore_bend_meshes_list:
            pass
        else:
            CustomErrorBox("Nothing to parent!", "Parenting Exception", 'ERROR')
        
        return {'FINISHED'}

class parent_head(bpy.types.Operator):
    """Parents anything with the \"_HeadChild\" tag to the head"""
    bl_idname = "parent.head"
    bl_label = "parent head"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        

        named_meshes_list = []
        dynamic_obj_list = []
        key_term = ["_HeadChild"]
        dynamic_objs = ["Head Squish"]
        bl_str = ""
        key_term_to_str = (bl_str.join(key_term))
        rig = isRigSelected(context)


        #checks if they have the proper name
        for obj in bpy.data.objects:
            if any(x in obj.name for x in key_term):
                named_meshes_list.append(obj.name)
        
        for obj in rig.children:
            if any(x in obj.name for x in dynamic_objs):
                dynamic_obj_list.append(obj.name)
        
        #gives the meshes their attributes
        for obj in named_meshes_list:
            head_parent = bpy.data.objects[obj]
            rig = isRigSelected(context)

            #VERTEX

            vg = head_parent.vertex_groups.new(name="headsquish")
            verts = []
            for vert in head_parent.data.vertices:
                verts.append(vert.index)
            vg.add(verts, 1.0, 'ADD')

            #Head Squish
            modifier = head_parent.modifiers.new(name="Head Squish", type='LATTICE')
            modifier.object = bpy.data.objects[dynamic_obj_list[GetListIndex("Head Squish", dynamic_obj_list)]]

            spot = modifier.driver_add("show_viewport")
            driver = spot.driver
            driver.type = 'SCRIPTED'
            var = driver.variables.new()
            var.type = 'SINGLE_PROP'
            var.name = "var"
            target = var.targets[0]
            target.id_type = 'OBJECT'
            target.id = rig
            target.data_path = "[\"antilag\"]"
            driver.expression = "+1 -var"

            #Armature
            modifier = head_parent.modifiers.new(name="Ice Cube", type='ARMATURE')
            modifier.object = rig

            #Parenting
            head_parent.parent = rig


        #removes the key term from the name
        for obj in named_meshes_list:
            clean_mesh_name = (obj.split(key_term_to_str)[0])
            bpy.data.objects[obj].name = clean_mesh_name
        
        #error message
        if obj in named_meshes_list:
            pass
        else:
            CustomErrorBox("Nothing to parent!", "Parenting Exception", 'ERROR')
        
        return {'FINISHED'}
#
class lilocredits(bpy.types.Operator):
    """Opens a link to my credits page"""
    bl_idname = "lilocredits.link"
    bl_label = "About the Creator"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        
        CustomLink("https://darthlilo.carrd.co/")
        
        return {'FINISHED'}
        
class discord_link(bpy.types.Operator):
    """Opens a link to my Discord server"""
    bl_idname = "discordserver.link"
    bl_label = "Join the Discord!"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
    
        CustomLink("https://discord.gg/3G44QQM")
        
        return {'FINISHED'}

class download_template_1(bpy.types.Operator):
    """Downloads an asset template pack from my discord server"""
    bl_idname = "template1.download"
    bl_label = "Download Asset Pack Template"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
    
        CustomLink("https://cdn.discordapp.com/attachments/978737749995683851/978737884897107968/template_asset_pack.zip")
        
        return {'FINISHED'}

class download_template_2(bpy.types.Operator):
    """Downloads a rig template pack from my discord server"""
    bl_idname = "template2.download"
    bl_label = "Download Rig Pack Template"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
    
        CustomLink("https://cdn.discordapp.com/attachments/978737749995683851/978744989691555850/template_rig_pack.zip")
        
        return {'FINISHED'}

class open_wiki(bpy.types.Operator):
    """Opens the Ice Cube wiki"""
    bl_idname = "wiki.open"
    bl_label = "Ice Cube Wiki"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        
        CustomLink("https://darthlilo.gitbook.io/ice-cube/")
        
        return{'FINISHED'}

class open_custom_presets(bpy.types.Operator):
    """Opens the DLC folder"""
    bl_idname = "custom_presets.open"
    bl_label = "Open DLC Folder"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        #addon location
        script_file = os.path.realpath(__file__)
        #opens a popup if you're using windows
        if platform == "win32":
            asset_directory_win = os.path.dirname(script_file)+"\\internal_files\\user_packs"
            subprocess.Popen(fr'explorer "{asset_directory_win}"')
        #opens a popup if you're using mac os
        elif platform == "darwin":
            asset_directory_mac = os.path.dirname(script_file)+"/internal_files/user_packs/"
            subprocess.call(["open", "-R", asset_directory_mac])
        #opens a popup if you're using linux
        elif platform == "linux" or platform == "linux2":
            asset_directory_linux = os.path.dirname(script_file)+"/internal_files/user_packs/"
            subprocess.Popen(['xdg-open', asset_directory_linux])
        else:
            CustomErrorBox(message="Please contact \"DarthLilo#4103\" on discord for help.", title="Unknown Operating System", icon='ERROR')

        return{'FINISHED'}

class append_emotion_line(bpy.types.Operator):
    """Appends an emotion line to the rig"""
    bl_idname = "append.emotion"
    bl_label = "Append Emotion Line"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        script_file = os.path.realpath(__file__)
        script_file = os.path.normpath(script_file)
        emotion_line_dir = os.path.dirname(script_file)+"/rigs"
        emotion_line_dir = os.path.normpath(emotion_line_dir)

        blendfile = os.path.join(emotion_line_dir, "emotion_line.blend")
        section = "Collection"
        obj = "emotion_line"
        filepath = os.path.join(blendfile,section,obj)
        directory = os.path.join(blendfile,section)
        filename = obj
        #appends the mesh
        bpy.ops.wm.append(filepath=filepath,filename=filename,directory=directory,link=False,active_collection=True)

        obj1 = bpy.context.selected_objects[0]
        obj2 = bpy.context.selected_objects[1]
        rig = isRigSelected(context)

        #parent objects
        obj1.parent = rig

        
        obs = [bpy.data.objects[str(rig.name)], bpy.data.objects[str(obj2.name)]]

        c = {}
        c["object"] = bpy.data.objects[str(rig.name)]
        c["active_object"] = bpy.data.objects[str(rig.name)]
        c["selected_objects"] = obs
        c["selected_editable_objects"] = obs
        bpy.ops.object.join(c)

        root_bones_list = []
        mesh_line_list = []
        bend_bone_list = []
        dynamic_obj_list = []
        key_term = ["_ImANewEmotion"]
        key_term2 = ["_ImALineThing"]
        key_term3 = ["_ImAnInternalBend"]
        dynamic_objs = ["Head Squish"]
        bl_str = ""
        key_term_to_str = (bl_str.join(key_term))
        key_term2_to_str = (bl_str.join(key_term2))
        key_term3_to_str = (bl_str.join(key_term3))

        #checks if they have the proper name
        for bones in rig.pose.bones:
            if any(x in bones.name for x in key_term):
                root_bones_list.append(bones.name)

        for obj in bpy.data.objects:
            if any(x in obj.name for x in key_term2):
                mesh_line_list.append(obj.name)
        
        for bones in rig.pose.bones:
            if any(x in bones.name for x in key_term3):
                bend_bone_list.append(bones.name)
        
        for obj in rig.children:
            if any(x in obj.name for x in dynamic_objs):
                dynamic_obj_list.append(obj.name)

        
        #add constraints to root bone
        for bones in root_bones_list:
            cbone = rig.pose.bones[bones]
            constraint = cbone.constraints.new(type='CHILD_OF')
            constraint.name = 'Parenting DON\'T TOUCH'
            constraint.target = rig
            constraint.subtarget = "headsquish"
        #add modifiers to mesh line
        for obj in mesh_line_list:
            mesh_line = bpy.data.objects[obj]
            rig = isRigSelected(context)
            mat = bpy.data.materials.get("Emotion_Line")

            #Head Squish
            modifier = mesh_line.modifiers.new(name="Head Squish", type='LATTICE')
            modifier.object = bpy.data.objects[str(dynamic_obj_list[0])]

            modifier = mesh_line.modifiers.new(name="Ice Cube", type='ARMATURE')
            modifier.object = rig

            modifier = mesh_line.modifiers.new(name="Subsurf Mod", type='SUBSURF')
            modifier.levels = 1
            modifier.render_levels = 2

            spot = modifier.driver_add("show_viewport")
            driver = spot.driver
            driver.type = 'SCRIPTED'
            var = driver.variables.new()
            var.type = 'SINGLE_PROP'
            var.name = "var"
            target = var.targets[0]
            target.id_type = 'OBJECT'
            target.id = rig
            target.data_path = "[\"antilag\"]"
            driver.expression = "+1 - var"

            vg = mesh_line.vertex_groups.new(name=bend_bone_list[0])
            verts = []
            for vert in mesh_line.data.vertices:
                verts.append(vert.index)
            vg.add(verts, 1.0, 'ADD')

            if mesh_line.data.materials:
                mesh_line.data.materials[0] = mat
            else:
                mesh_line.data.materials.append(mat)
        
        #removes the key term from the name
        for bones in root_bones_list:
            cbone = rig.pose.bones[bones]
            clean_mesh_name = (cbone.name.split(key_term_to_str)[0])
            cbone.name = clean_mesh_name
        
        for obj in mesh_line_list:
            newobj = bpy.data.objects[obj]
            clean_mesh_name = (newobj.name.split(key_term2_to_str)[0])
            newobj.name = clean_mesh_name
        
        for bones in bend_bone_list:
            cbone = rig.pose.bones[bones]
            clean_mesh_name = (cbone.name.split(key_term3_to_str)[0])
            cbone.name = clean_mesh_name

        return{'FINISHED'}

class check_for_updates(bpy.types.Operator):
    """Checks the Ice Cube GitHub for updates"""
    bl_idname = "check.updates"
    bl_label = "Check for updates"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        #gets the current version of the addon
        current_version = bl_info['version']

        #Attempts to get the latest version and description of the addon from github, if not, returns NONE
        try:
            repo = json.loads(request.urlopen("https://api.github.com/repos/DarthLilo/ice-cube-beta/releases/latest").read().decode())
            github_latest_vers = repo['tag_name']
            github_changes = repo['body']
        except:
            github_latest_vers = "NONE"
        
        #Checks the current version of the rig, if none found returns "broken"
        try:
            version = IsVersionUpdated(current_version)
        except:
            version = "broken"

        #Prints the correct message based on the version
        if version == True:
            properties.update_available = False
            CustomErrorBox(f"You're running the latest version of Ice Cube. Version: {current_version}", title="Running Latest Version", icon='CHECKMARK')
        elif version == False:
            properties.update_available = True
            CustomErrorBox(f"Changes:\n{github_changes}", title=f"There is an update available! Version: {github_latest_vers}", icon='IMPORT')
        elif version == "broken":
            properties.update_available = False
            CustomErrorBox("Unable to connect to GitHub API, check your internet connection!",title="Connection Error", icon='CANCEL')
        else:
            CustomErrorBox("Unknown Error, contact \"DarthLilo#4103\" on Discord.", title="Unknown Error", icon='ERROR')
        

        return{'FINISHED'}

class install_update(bpy.types.Operator):
    """Installs the latest version from GitHub"""
    bl_idname = "install.update"
    bl_label = "Install the latest update"
    bl_options = {'REGISTER', 'UNDO'}



    def execute(self, context):
        #sets up variables
        script_file = os.path.realpath(__file__)
        script_file = os.path.normpath(script_file)
        install_loc = os.path.dirname(script_file)+""
        downloads_folder = os.path.dirname(script_file)+"/downloads"
        backups_folders = os.path.dirname(script_file)+"/backups"
        #checks if the downloads folder exists, if not, create one.
        if os.path.exists(downloads_folder):
            print("Path Found")
        else:
            os.mkdir(downloads_folder)
            print("Created Downloads Folder")

        download_folder = os.path.normpath(downloads_folder)
        backups_folders = os.path.normpath(backups_folders)

        #clear folder
        ClearDirectory(download_folder)

        download_file_loc = str(download_folder+"/latest_release.zip")

        github_repo = json.loads(request.urlopen("https://api.github.com/repos/DarthLilo/ice-cube-beta/releases/latest").read().decode())
        github_zip = github_repo['zipball_url']

        #download the zip
        try:
            request.urlretrieve(github_zip, download_file_loc)
            print("File Downloaded!")
        except Exception as e:
            CustomErrorBox(str(e), "Error while downloading update.", icon="CANCEL")
            print("Error while downloading file.")
        #unzips the file
        try:
            print(f"Unzipping File")
            with zipfile.ZipFile(download_file_loc, 'r') as zip_ref:
                zip_ref.extractall(download_folder)
            print("Successfully Unzipped File!")
            #removes the zip
            os.remove(download_file_loc)
            #if there's an old Ice Cube, remove it
            try:
                shutil.rmtree(download_folder+"/Ice Cube")
            except:
                pass
            print("Cleaned Folder")
        except Exception as e:
            CustomErrorBox(str(e), "Error unpacking update file.", icon="CANCEL")
            print("Unknown Error")
        #Rename the downloaded file to Ice Cube
        for file in getFiles(download_folder):
            filepath = str(f"{download_folder}/{file}")
            renamed_file = str(f"{download_folder}/Ice Cube")
            os.rename(filepath, renamed_file)
        
        #Install the downloaded addon
        try:
            distutils.dir_util.copy_tree(download_folder+"/Ice Cube", install_loc)
            print("Finished Install!")
            CustomErrorBox("Finished installing update! Restart Blender before continuing!","Updated Finished",'INFO')
        except Exception as e:
            print("Error Completing Install.")
            CustomErrorBox(str(e),"Error installing update file.",'ERROR')

        return{'FINISHED'}

class open_update_page(bpy.types.Operator):
    """Opens the Ice Cube website"""
    bl_idname = "open.update"
    bl_label = "Open Ice Cube Website"
    bl_options = {'REGISTER', 'UNDO'}



    def execute(self, context):
        CustomLink("https://ice-cube-beta.carrd.co/")
        properties.update_available = False
        return{'FINISHED'}

class create_backup(bpy.types.Operator):
    """Creates a backup of the currently installed version"""
    bl_idname = "create.backup"
    bl_label = "Load Backup"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        #sets up variables
        obj = context.object
        script_file = os.path.realpath(__file__)
        virtual_ice_cube = os.path.dirname(script_file)+""
        virtual_ice_cube = os.path.normpath(virtual_ice_cube)
        script_file = os.path.normpath(script_file)
        backups_folder = os.path.dirname(script_file)+"/backups"

        files = []
        files_nopath = []
        folders = []
        folders_nopath = []

        backup_name = obj.backup_name
        #check for a folder in the backups folder with the name entered, if none, create it.
        if obj.get("backup_name"):
            if obj.get("backup_name") == "":
                backups_folder = os.path.dirname(backups_folder)+"/backups/main"
                if os.path.exists(backups_folder):
                    pass
                else:
                    os.mkdir(backups_folder)
            else:
                backups_folder = os.path.dirname(backups_folder)+"/backups/"+backup_name
                if os.path.exists(backups_folder):
                    pass
                else:
                    os.mkdir(backups_folder)
        else:
            backups_folder = os.path.dirname(backups_folder)+"/backups/main"
            if os.path.exists(backups_folder):
                pass
            else:
                os.mkdir(backups_folder)
        
        #get a list of files in the addon folder
        for file in getFiles(virtual_ice_cube):
            newfile = str(f"{virtual_ice_cube}/{file}")
            if os.path.isfile(newfile):
                files.append(newfile)
                files_nopath.append(file)
        

        #create folders list
        folders.append("internal_files")
        folders.append("icons")
        folders.append("rigs")
        folders_nopath.append("internal_files")
        folders_nopath.append("icons")
        folders_nopath.append("rigs")



        #clean files list
        del files[0]
        del files_nopath[0]

        print(folders_nopath)

        #Actual Backing Up
        try:
            for file in files_nopath:
                file_nopy = file.split(".")[0]
                shutil.copy(f"{virtual_ice_cube}/{file}", f"{backups_folder}/{files_nopath[GetListIndex(file_nopy, files_nopath)]}")

            for folder in folders_nopath:
                try:
                    os.mkdir(f"{backups_folder}/{folders_nopath[GetListIndex(folder, folders_nopath)]}")
                except:
                    pass
                
            for folder in folders_nopath:
                distutils.dir_util.copy_tree(f"{virtual_ice_cube}/{folder}", f"{backups_folder}/{folder}")
            if obj.get("backup_name"):
                if obj.get("backup_name") == "":
                    backup_name = "main"
                else:
                    pass
            else:
                backup_name = "main"
            CustomErrorBox(f"Created Backup: [{backup_name}]", "Created Backup", 'INFO')
        except:
            CustomErrorBox(f"An Error Has Occured: [{backup_name}]", "Unknown Error", 'ERROR')
            

        return{'FINISHED'}

class load_backup(bpy.types.Operator):
    """Loads the selected backup from your backups folder"""
    bl_idname = "load.backup"
    bl_label = "Append Emotion Line"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        #set up the variables
        obj = context.object
        script_file = os.path.realpath(__file__)
        script_file = os.path.normpath(script_file)
        virtual_ice_cube = os.path.dirname(script_file)+""
        backup_name = obj.backup_name
        backups_folder = os.path.dirname(script_file)+"/backups/"+backup_name
        #check if you've entered a backup name, if not, give a prompt, if so, check if that folder exists and create one if it doesn't exist.
        if obj.get("backup_name"):
            if obj.get("backup_name") == "":
                CustomErrorBox("NO BACKUP FOUND","Selection Error",'ERROR')
            else:
                if os.path.exists(backups_folder):
                    distutils.dir_util.copy_tree(backups_folder, virtual_ice_cube)
                    CustomErrorBox(f"Loaded Backup: [{backup_name}], restart Blender for changes!", "Loaded Backup", 'INFO')
                else:
                    CustomErrorBox("INVALID BACKUP","Selection Error",'ERROR')
        else:
            CustomErrorBox("NO BACKUP FOUND","Selection Error",'ERROR')
            

        return{'FINISHED'}

class delete_backup(bpy.types.Operator):
    """Deletes the selected backup"""
    bl_idname = "delete.backup"
    bl_label = "Delete Backup"
    bl_options = {'REGISTER', 'UNDO'}



    def execute(self, context):
        #set up variables
        obj = context.object
        script_file = os.path.realpath(__file__)
        virtual_ice_cube = os.path.dirname(script_file)+""
        virtual_ice_cube = os.path.normpath(virtual_ice_cube)
        script_file = os.path.normpath(script_file)
        backups_folder = os.path.dirname(script_file)+"/backups"

        backup_name = obj.backup_name
        #check if you've entered a name, if not, give a prompt, if so, delete the entered name if a backup exists for it
        if obj.get("backup_name"):
            if obj.get("backup_name") == "":
                CustomErrorBox("Please enter the name of a backup!","Selection Error",'ERROR')
            else:
                backup_to_remove = os.path.dirname(backups_folder)+"/backups/"+backup_name
                if os.path.exists(backup_to_remove):
                    shutil.rmtree(backup_to_remove)
                    CustomErrorBox(f"Deleted Backup: [{backup_name}]", "Deleted Backup", 'INFO')
                else:
                    CustomErrorBox("Invalid Backup","Selection Error",'ERROR')
        else:
            CustomErrorBox("Please enter the name of a backup!","Selection Error",'ERROR')

        return{'FINISHED'}

dlc_id = []
dlc_type = []
dlc_author = []

def getIndexCustom(strV = "", indexlist = []):
        indexlist_new = []
        for item in indexlist:
            string_item = str(item)
            indexlist_new.append(string_item)
        index = indexlist_new.index(strV)

        return index

class refresh_dlc(bpy.types.Operator):
    """Checks the Ice Cube GitHub for new DLC"""
    bl_idname = "refresh.dlc"
    bl_label = "Delete Backup"
    bl_options = {'REGISTER', 'UNDO'}



    def execute(self, context):
        #checks github for the latest DLCs
        github_repo = json.loads(request.urlopen("https://raw.githubusercontent.com/DarthLilo/ice-cube-beta/master/dlc_list.json").read().decode())
        dlc_id.clear()
        dlc_type.clear()
        dlc_author.clear()
        for dlc in github_repo:
            dlc_number = getIndexCustom(str(dlc), github_repo)
            dlc_id.append(github_repo[dlc_number]['dlc_id'])
            dlc_type.append(github_repo[dlc_number]['dlc_type'])
            dlc_author.append(github_repo[dlc_number]['author'])

        return{'FINISHED'}

class download_dlc(bpy.types.Operator):
    """Downloads the selected DLC from GitHub"""
    bl_idname = "download.dlc"
    bl_label = "Download DLC"
    bl_options = {'REGISTER', 'UNDO'}



    def execute(self, context):
        obj = context.object
        dlc_textbox = obj.dlc_name_load
        #gets the latest data from the github "dlc_list.json" file
        github_repo = json.loads(request.urlopen("https://raw.githubusercontent.com/DarthLilo/ice-cube-beta/master/dlc_list.json").read().decode())
        #checks if you entered the name of a valid DLC
        if obj.get("dlc_name_load"):
            if obj.get("dlc_name_load") == "":
                #gives an error if you didn't enter the name of a valid DLC
                CustomErrorBox("Please enter the name of a DLC","Selection Error",'ERROR')
            else:
                try:
                    #sets up variables depending on what is entered in the textbox
                    for dlc in github_repo:
                        dlc_number = getIndexCustom(dlc_textbox,dlc_id)
                        dlc_type = github_repo[dlc_number]['dlc_type']
                        dlc_id_name = github_repo[dlc_number]['dlc_id']
                        dlc_download = github_repo[dlc_number]['download_link']
                        script_file = os.path.realpath(__file__)
                        script_file = os.path.normpath(script_file)
                        downloads_folder = os.path.dirname(script_file)+"/downloads"
                        dlc_folder = os.path.dirname(script_file)+"/internal_files/user_packs/"+dlc_type+"/"+dlc_id_name
                    #checks if a folder for the selected dlc exists, if not, create one.
                    if os.path.exists(dlc_folder):
                        print("Path Found")
                    else:
                        os.mkdir(dlc_folder)
                        print(f"Created {dlc_id_name} Folder")
                    download_folder = os.path.normpath(downloads_folder)
                    #clear folder
                    ClearDirectory(download_folder)
                    
                    download_file_loc = str(download_folder+"/dlc.zip")

                    #download the zip
                    try:
                        request.urlretrieve(dlc_download, download_file_loc)
                        print("File Downloaded!")
                    except:
                        CustomErrorBox("An unknown error has occured, canceled download.","Downloading Error","ERROR")
                    #unzips the file
                    try:
                        print(f"Unzipping File")
                        try:
                            shutil.rmtree(download_folder+"/"+dlc_id_name)
                        except:
                            pass
                        with zipfile.ZipFile(download_file_loc, 'r') as zip_ref:
                            zip_ref.extractall(download_folder)
                        print("Successfully Unzipped File!")
                        #remove the zip file when done
                        os.remove(download_file_loc)
                        print("Cleaned Folder")
                    except:
                        print("Unknown Error")
                    
                    try:
                        #install the new DLC
                        distutils.dir_util.copy_tree(download_folder+"/"+dlc_id_name, dlc_folder)
                        print("Finished Install!")
                        CustomErrorBox("Finished installing DLC! Restart Blender before continuing!","Updated Finished",'INFO')
                    except:
                        print("Error Completing Install.")
                        CustomErrorBox("Error Completing Install.","Updated Cancelled",'ERROR')

                except:
                    CustomErrorBox("Invalid DLC","Selection Error",'ERROR')
        else:
            CustomErrorBox("Please enter the name of a DLC","Selection Error",'ERROR')

        return{'FINISHED'}

try:
    bpy.types.Scene.selected_asset = EnumProperty(
        name = "Selected Pack",
        default = 'rig_1',
        items = final_list
    )
except:
    bpy.types.Scene.selected_asset = EnumProperty(
        name = "Selected Pack",
        default = 'rig_1',
        items = [('rig_1', "NO PACKS FOUND", 'Please install or create an asset pack!')]
    )


classes = [rig_baked_class,
           parent_struct_class,
           append_preset,
           append_defaultrig,
           parent_leftarm,
           parent_rightarm,
           parent_rightleg,
           parent_leftleg,
           parent_body,
           parent_head,
           lilocredits,
           discord_link,
           download_template_1,
           download_template_2,
           open_wiki,
           open_custom_presets,
           append_emotion_line,
           check_for_updates,
           install_update,
           open_update_page,
           create_backup,
           load_backup,
           delete_backup,
           refresh_dlc,
           download_dlc,
           ]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__=="__main__":
    register()