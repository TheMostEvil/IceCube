bl_info ={
    "name": "Ice Cube",
    "author": "DarhtLilo",
    "version": (1, 2, 9),
    "blender": (3, 0, 0),
    "location": "View3D > Tool",
    "description": "A custom python script for Ice Cube! Credit to \"@KJMineImator\" and \"@RealMineAPI\" on twitter for helping me with the code!",
    "tracker_url": "https://discord.gg/3G44QQM",
    "category": "Lilo's Rigs",
}

import importlib

from . import load_modules
from . import operators

def register():
    load_modules.register(bl_info)
    operators.cur_version = bl_info['version']

def unregister():
    load_modules.unregister(bl_info)

    
if __name__ == "__main__":
    register()
