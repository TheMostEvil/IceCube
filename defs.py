#Libraries
import bpy
import os
import webbrowser
import json
from urllib import request
import shutil
import imghdr
import struct



#Rig Selectors

##Checks if the targed object is part of the rig
def partOfRig(obj):
    try:
        #obj.parent.data.get("rig_id") == rig_id
        return False
    except (AttributeError, KeyError, TypeError):
        return False

##Checks if the currently selected object is the rig
def isRigSelected(context):
    return bpy.context.active_object.parent if partOfRig(bpy.context.active_object) else bpy.context.active_object

#Looks for the mesh with the materials tag set to 1
def main_face(rig):
    try:
        for obj in rig.children:
            try:
                if obj.data['materials'] == 1:
                    return obj
            except:
                pass
    except (AttributeError, KeyError, TypeError):
        return False





#UI Tools

#Draws a Custom Error Box Popup, use "\n" to draw a new line.
def CustomErrorBox(message = "", title = "Custom Error Box", icon = 'INFO'):

    def draw(self, context):
        lines = message.split("\n")

        for l in lines:
            self.layout.label(text=l)
    
    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)



#Filepath Tools

##Prints a list of filenames in a specific directory.
def getFiles(path):
    dir = os.path.realpath(path);
    
    if os.path.exists(dir):
        dirs = [];

        for i in os.listdir(dir):
            dirs.append(i);

        return dirs;

##Unpacks an image
def unpack_img(img):
    if img.packed_files:
        if bpy.data.is_saved:
            return img.unpack()
        else:
            return img.unpack(method='USE_ORIGINAL')


##Clears every folder inside of a specified directory
def ClearDirectory(dir = ""):
    for folder in os.listdir(dir):
        filepath = os.path.join(dir, folder)
        filepath = os.path.normpath(filepath)
        shutil.rmtree(filepath)

##
def isOldSkin(skin):

    with open(skin, 'rb') as fhandle:
        head = fhandle.read(24)
        if len(head) != 24:
            return
        if imghdr.what(skin) == 'png':
            check = struct.unpack('>i', head[4:8])[0]
            if check != 0x0d0a1a0a:
                return
            width, height = struct.unpack('>ii', head[16:24])
    if height == 64:
        return False
    else:
        return True




#Web Browser Tools

##Opens a custom url in the default browser
def CustomLink(url = ""):
    http = ["http://"]
    https = ["https://"]

    http_str = "http://"
    https_str = "https://"

    blnk_str = ""
    fixed_url = (blnk_str.join(url))
    if any(x in url for x in http):
        url = (fixed_url.split(http_str)[1])

    elif any(x in url for x in https):
        url = (fixed_url.split(https_str)[1])

    elif():
        url = url
    
    
    webbrowser.open_new(http_str + url)




#Code Tools

##Gets the index value of specified text in a list
def GetListIndex(strV = "", indexlist = []):
    indexlist_new = []
    for item in indexlist:
        string_item = str(item)
        string_item = (string_item.split(".")[0])
        indexlist_new.append(string_item)
    index = indexlist_new.index(strV)

    return index


##Checks if the addon is up to date
def IsVersionUpdated(current):
    cv = str(current)
    repo = json.loads(request.urlopen("https://api.github.com/repos/DarthLilo/ice-cube-beta/releases/latest").read().decode())
    github_latest_vers = repo['tag_name']
    current_vers = str(cv.replace("(", ""))
    current_vers = str(current_vers.replace(")", ""))
    current_vers = str(current_vers.replace(",", ""))
    current_vers = int(current_vers.replace(" ", ""))
    latest_vers = int(github_latest_vers.replace(".", ""))
    if current_vers >= latest_vers:
        return True
    else:
        return False