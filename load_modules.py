import importlib


if "bpy" in locals():
    importlib.reload(main)
    #importlib.reload(ui)
    importlib.reload(operators)
    importlib.reload(skin_downloader)
    importlib.reload(inventory_system)
else:
    import bpy
    from . import (
        main,
        #ui,
        operators,
        skin_downloader,
        inventory_system,
    )

module_list = (
    main,
    #ui,
    skin_downloader,
    inventory_system,
)

def register(bl_info):
    for mod in module_list:
        mod.register()

def unregister(bl_info):
    for mod in reversed(module_list):
        mod.unregister()