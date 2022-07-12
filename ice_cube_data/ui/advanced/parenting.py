#Libraries
import bpy

def parenting_UI(self, context, layout, rig_baked):
    box = layout.box()
                
    b = box.row(align=True)
    b.operator("parent.head", text="Parent Head")
    b = box.row(align=True)
    b.operator("parent.rightarm", text="Parent Right Arm")
    b.operator("parent.body", text="Parent Body")
    b.operator("parent.leftarm", text="Parent Left Arm")
    b = box.row(align=True)
    b.operator("parent.rightleg", text="Parent Right Leg")
    b.operator("parent.leftleg", text="Parent Left Leg")
    b = box.row(align=True)
    if rig_baked == True:
        global_parent_text = "Parent half: Lower"
        icon = 'LAYER_ACTIVE'
    else:
        global_parent_text = "Parent half: Upper"
        icon = 'LAYER_USED'
    b.operator("rig.parentstruct", text=global_parent_text, icon=icon)

    
    box = layout.box()
    box.label(text= "IMPORTANT", icon= 'HELP')
    b = box.row(align=True)
    b = box.row(align=True)
    b.label(text= "To parent something to the rig with all features")
    b = box.row(align=True)
    b.label(text= "inherited, add the correct suffix to the end")
    b = box.row(align=True)
    b.label(text= "of their name then click the corresponding button.")
    b = box.row(align=True)
    b = box.row(align=True)
    b.label(text= "Head Suffix: \"_HeadChild\"", icon= 'OUTLINER_OB_ARMATURE')
    b = box.row(align=True)
    b.label(text= "Body Suffix: \"_BodyChild\"", icon= 'OUTLINER_OB_ARMATURE')
    b = box.row(align=True)
    b.label(text= "Right Arm Suffix: \"_RightArmChild\"", icon= 'OUTLINER_OB_ARMATURE')
    b = box.row(align=True)
    b.label(text= "Left Arm Suffix: \"_LeftArmChild\"", icon= 'OUTLINER_OB_ARMATURE')
    b = box.row(align=True)
    b.label(text= "Right Leg Suffix: \"_RightLegChild\"", icon= 'OUTLINER_OB_ARMATURE')
    b = box.row(align=True)
    b.label(text= "Left Leg Suffix: \"_LeftLegChild\"", icon= 'OUTLINER_OB_ARMATURE')
    b = box.row(align=True)
    b = box.row(align=True)
    b.label(text= "If you want to have a certain part ignore bends,")
    b = box.row(align=True)
    b.label(text="just add the \"_IgnoreBend\" after the previous")
    b = box.row(align=True)
    b.label(text="suffix and make sure to chose an upper or lower parent.")

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