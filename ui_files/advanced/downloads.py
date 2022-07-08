#Libraries
import datetime
import bpy
import os
from sys import platform
import pathlib

def downloads_UI(self, context, layout, obj, script, update, getFilesPath, getIndex, dlc_id, dlc_type, dlc_author):
    box = layout.box()
    if platform == "darwin":
        b = box.row(align=True)
        b.label(text= "DOWNLOAD PANEL NOT SUPPORTED ON MAC OS!", icon='ERROR')
    else:
        script_file = script
        virtual_ice_cube = os.path.dirname(script_file)+""
        virtual_ice_cube = os.path.normpath(virtual_ice_cube)
        script_file = os.path.normpath(script_file)
        backups_folder = os.path.dirname(script_file)+"/backups"
        dlc_folder_preset = os.path.dirname(script_file)+"/internal_files/user_packs/rigs"
        dlc_folder_asset = os.path.dirname(script_file)+"/internal_files/user_packs/inventory"
        if os.path.exists(backups_folder):
            pass
        else:
            os.mkdir(backups_folder)
            print("Created Backups Folder")

        b = box.row(align=True)
        b.label(text= "Update Manager", icon='FILE_REFRESH')
        b = box.row(align=True)
        b.label(text="Do NOT close Blender while installing")
        b = box.row(align=True)
        if update == True:
            b.operator("install.update", text="Install Update", icon='MOD_WAVE')
        else:
            b.operator("check.updates", text="Check for Updates", icon='IMPORT')
        box = layout.box()
        b = box.row(align=True)
        b.label(text = "Backup Manager")
        b = box.row(align=True)
        b.prop(obj, "backup_name", text="Backup Name", icon='FILE_BACKUP')
        b = box.row(align=True)
        bcreate = b.row(align=True)
        bload = b.row(align=True)
        bdelete = b.row(align=True)
        bcreate.operator("create.backup", text="Create Backup")
        bload.operator("load.backup", text="Load Backup")
        bdelete.operator("delete.backup", text="Delete Backup")
        if obj.get("backup_name"):
            if obj.get("backup_name") == "":
                bload.enabled = False
                bdelete.enabled = False
            else:
                pass
        else:
            bload.enabled = False
            bdelete.enabled = False
        b = box.row(align=True)

        box = b.box()
        b1 = box.row(align=True)
        b1.label(text = "Created Backups:")
        backup_folder_scan = os.listdir(backups_folder)
        if len(backup_folder_scan) == 0:
            b1 = box.row(align=True)
            b1.label(text = "NO BACKUPS FOUND", icon = 'FILE_BACKUP')
            b1.label(text = f"Created:  [N/A]")
        else:
            for backup in getFilesPath(backups_folder):
                creation_date = pathlib.Path(f"{backups_folder}/{backup}").stat().st_mtime
                creation_date = str(datetime.datetime.fromtimestamp(creation_date)).split(" ")[0]
                b1 = box.row(align=True)
                b1.label(text = backup, icon = 'FILE_BACKUP')
                b1.label(text = f"Created:  [{creation_date}]")
        box = layout.box()
        b = box.row(align=True)
        b.label(text = "DLC Manager")
        b = box.row(align=True)
        b.prop(obj, "dlc_name_load", text="DLC Name", icon='FILE_FOLDER')
        b.operator("download.dlc", text="", icon= 'IMPORT')
        b.operator("refresh.dlc", text="", icon= 'FILE_REFRESH')
        b = box.row(align=True)
        b.label(text = "Available DLC:")
        b = box.row(align=True)
        #start of box
        box2 = b.box()
        b1 = box2.row(align=True)

        b1.label(text="ID:", icon ='FILE_BACKUP')
        b1.label(text="Type:")
        b1.label(text="Author:")
        b1 = box2.row(align=True)
        for dlc in dlc_id:
            try:
                dlc_number = getIndex(str(dlc), dlc_id)
                b1.label(text=f"{dlc_id[dlc_number]}",icon ='FILE_BACKUP')
                b1.label(text=f"{dlc_type[dlc_number]}")
                b1.label(text=f"{dlc_author[dlc_number]}")
            except:
                b1.label(text="REFRESH")
            b1 = box2.row(align=True)




        b1 = box2.row(align=True)
        #end of box
        b = box.row(align=True)
        b.label(text = "Installed DLC:")
        b = box.row(align=True)
        #start of box
        box2 = b.box()
        b1 = box2.row(align=True)
        dlc_preset_scan = os.listdir(dlc_folder_preset)
        dlc_asset_scan = os.listdir(dlc_folder_asset)
        if len(dlc_preset_scan) + len(dlc_asset_scan) == 0:
            b1 = box2.row(align=True)
            b1.label(text = "NO DLC FOUND", icon = 'FILE_BACKUP')
        else:
            for dlc in getFilesPath(dlc_folder_asset):
                b1 = box2.row(align=True)
                b1.label(text = dlc, icon = 'FILE_BACKUP')
            for dlc in getFilesPath(dlc_folder_preset):
                b1 = box2.row(align=True)
                b1.label(text = dlc, icon = 'FILE_BACKUP')