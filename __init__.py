bl_info ={
    "name": "Ice Cube",
    "author": "DarhtLilo",
    "version": (1, 3, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Tool",
    "description": "A custom python script for Ice Cube! Credit to \"@KJMineImator\" and \"@RealMineAPI\" on twitter for helping me with the code!",
    "tracker_url": "https://discord.gg/3G44QQM",
    "category": "Lilo's Rigs",
}

import bpy
import importlib
import sys
from os import path

root_folder = path.dirname(path.abspath(__file__))
github_url = "https://api.github.com/repos/TheMostEvil/IceCube/releases/latest"

sys.path.append(path.dirname(path.abspath(__file__)))

#Import Files
from . import main
from . import ice_cube_data

#Reload
importlib.reload(main)
importlib.reload(ice_cube_data)


def register():
    main.register()
    ice_cube_data.register()

def unregister():
    main.unregister()
    ice_cube_data.unregister()
