import os
import subprocess
import bpy
from sys import platform
import json
from urllib import request
import zipfile
import shutil
import distutils.dir_util
import datetime
import pathlib

from ice_cube import root_folder, latest_dlc, github_url

from ice_cube_data.utils.ui_tools import CustomErrorBox
from ice_cube_data.utils.file_manage import ClearDirectory, getFiles
from ice_cube_data.utils.general_func import GetListIndex, getIndexCustom


def open_user_packs(self, context):
    #addon location
    #opens a popup if you're using windows
    if platform == "win32":
        asset_directory_win = root_folder+"\\ice_cube_data\\internal_files\\user_packs"
        subprocess.Popen(fr'explorer "{asset_directory_win}"')
    #opens a popup if you're using mac os
    elif platform == "darwin":
        asset_directory_mac = root_folder+"/ice_cube_data/internal_files/user_packs/"
        subprocess.call(["open", "-R", asset_directory_mac])
    #opens a popup if you're using linux
    elif platform == "linux" or platform == "linux2":
        asset_directory_linux = root_folder+"/ice_cube_data/internal_files/user_packs/"
        subprocess.Popen(['xdg-open', asset_directory_linux])
    else:
        CustomErrorBox(message="Please contact \"DarthLilo#4103\" on discord for help.", title="Unknown Operating System", icon='ERROR')

    return{'FINISHED'}

def install_update_func(self, context):
    #sets up variables
    install_loc = root_folder+""
    downloads_folder = root_folder+"/downloads"
    backups_folders = root_folder+"/backups"
    can_backup = False
    #checks if the downloads folder exists, if not, create one.
    if os.path.exists(downloads_folder):
        print("Path Found")
    else:
        os.mkdir(downloads_folder)
        print("Created Downloads Folder")

    download_folder = os.path.normpath(downloads_folder)
    backups_folders = os.path.normpath(backups_folders)

    #checking if there's an up to date backup
    backups_list = {}
    for file in getFiles(backups_folders):
        creation_date = pathlib.Path(f"{backups_folders}/{file}").stat().st_mtime
        creation_date = "".join(str(datetime.datetime.fromtimestamp(creation_date)).split(" ")[0].split("-"))
        backups_list[file] = creation_date
    
    cur_time = "".join(str(datetime.datetime.now()).split(" ")[0].split("-"))
    
    for entry in backups_list:
        if backups_list[entry] == cur_time:
            can_backup = True
            break
    
    if can_backup == False:
        CustomErrorBox("Please create an up-to-date backup before updating!","No updated backup found!","ERROR")
        return{'FINISHED'}
    

    #clear folder
    ClearDirectory(download_folder)

    download_file_loc = str(download_folder+"/latest_release.zip")

    github_repo = json.loads(request.urlopen(github_url).read().decode())
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

def create_backup_func(self, context):
    #sets up variables
    obj = context.object
    virtual_ice_cube = root_folder+""
    virtual_ice_cube = os.path.normpath(virtual_ice_cube)
    backups_folder = root_folder+"/backups"

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
    
    #list of files to backup
    files_to_backup = ["__init__.py","main.py"]
    for file in files_to_backup:
        file_w_path = os.path.normpath(f"{root_folder}/{file}")
        files.append(file_w_path)
        files_nopath.append(file)
    

    #list of folders to backup
    folders_to_backup = ["ice_cube_data"]
    for folder in folders_to_backup:
        folder_w_path = os.path.normpath(f"{root_folder}/{folder}")
        folders.append(folder_w_path)
        folders_nopath.append(folder)




    print(files_nopath)
    print(folders_nopath)

    print(files)
    print(folders)

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

def load_backup_func(self, context):
    #set up the variables
    obj = context.object
    virtual_ice_cube = root_folder+""
    backup_name = obj.backup_name
    backups_folder = root_folder+"/backups/"+backup_name
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

def delete_backup_func(self, context):
        #set up variables
        obj = context.object
        virtual_ice_cube = root_folder+""
        virtual_ice_cube = os.path.normpath(virtual_ice_cube)
        backups_folder = root_folder+"/backups"

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

def download_dlc_func(self, context, dlc_id):
        obj = context.object
        dlc_textbox = obj.dlc_name_load
        #gets the latest data from the github "dlc_list.json" file
        github_repo = json.loads(request.urlopen(latest_dlc).read().decode())
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
                        downloads_folder = root_folder+"/downloads"
                        dlc_folder = root_folder+"/ice_cube_data/internal_files/user_packs/"+dlc_type+"/"+dlc_id_name
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

classes = [
           ]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__=="__main__":
    register()