"""
This file contains all labels and functions related to the blood analysis
"""
init python:
    def add_toolbox_blood_items():
        """Adds necessary blood collection items to inventory.
        """
        tools["swab"] = True
        tools["gloves"] = True
        if "swab_pack" not in toolbox_items:
            addToToolbox(["swab_pack"])
        addToToolbox(["gloves"])

    # def add_toolbox_print_items():
    #     """Adds necessary fingerprint collection items to inventory.
    #     """

label click_canvas:
    $ default_mouse = "default"
    hide screen casefile_physical
    hide screen casefile_photos

    scene inspect_canvas

    if analyzed["canvas"] and analyzed["canvas presumptive"]:
        $ analyzing["canvas"] = False
        s normal "You've already inspected the canvas."
        call crimescene
    
    $ analyzing["canvas"] = True

    if encountered["canvas"] == False:
        $ encountered["canvas"] = True
        "New photo added to evidence."

    $ add_toolbox_blood_items()
    call screen toolbox

label click_stool:
    $ default_mouse = "default"
    hide screen casefile_physical
    hide screen casefile_photos
    scene inspect_stool

    if analyzed["splatter"] and analyzed["splatter presumptive"] and analyzed["splatter packaged"]:
        $ analyzing["stool"] = False
        s normal3 "You've finished analyzing the splatter."
        call crimescene

    $ analyzing["stool"] = True

    if encountered["stool"] == False:
        $ encountered["stool"] = True
        "New photo added to evidence."    

    $ add_toolbox_blood_items()
    call screen toolbox

label click_knife:
    $ default_mouse = "default"
    hide screen casefile_physical
    hide screen casefile_photos
    scene inspect_knife

    if analyzed["knife presumptive"] and analyzed["knife packaged"] and analyzed["knife fingerprint"]:
        $ analyzing["knife"] = False
        s "You've already inspected the knife"
        call crimescene

    $ analyzing["knife"] = True
    $ tools["uv light"] = True

    if encountered["knife"] == False:
        $ encountered["knife"] = True
        "New photo added to evidence."

    if not (analyzed["knife presumptive"] and analyzed["knife packaged"]):
        $ add_toolbox_blood_items()
    if not (analyzed["knife fingerprint"] and analyzed["knife fingerprint alt"] and analyzed["knife fingerprint packaged"]):
        $ addToToolbox(["uv_light", "magnetic_powder", "silver_granular_powder", "scalebar", "tape", "backing_card", "gel_lifter"])
        $ addToToolbox(["gloves"])
    call screen toolbox

label click_table:
    $ default_mouse = "default"
    hide screen casefile_physical
    hide screen casefile_photos
    scene inspect_table

    if analyzed["table presumptive"] and analyzed["table packaged"]:
        $ analyzing["table"] = False
        s normal2 "You've already inspected the table"
        call crimescene

    $ analyzing["table"] = True

    if encountered["table"] == False:
        $ encountered["table"] = True
        "New photo added to evidence."

    $ add_toolbox_blood_items()
    call screen toolbox

label canvas_swab:
    scene inspect_canvas
    if asked["canvas_swab"]:
        show red swab at Transform(xpos=0.4, ypos=0.3)
        "Sample successfully collected."
        jump sample
    
    show clean swab at Transform(xpos=0.4, ypos=0.3)
    menu:
        "How would you like to collect the sample?"
        "Using a wet swab":
            $ asked["canvas_swab"] = True
            hide clean swab
            show red swab at Transform(xpos=0.4, ypos=0.3)
            "Sample successfully collected."
            jump sample
        "Using a dry swab":
            $ asked["canvas_swab"] = True
            hide clean swab
            show red swab at Transform(xpos=0.4, ypos=0.3)
            "Sample successfully collected."
            jump sample

label knife_swab:
    scene inspect_knife
    if asked["knife_swab"]:
        show red swab at Transform(xpos=0.4, ypos=0.3)
        "Sample successfully collected."
        jump sample
    
    show clean swab at Transform(xpos=0.4, ypos=0.3)
    menu:
        "How would you like to collect the sample?"
        "Using a wet swab":
            $ asked["knife_swab"] = True
            hide clean swab
            show red swab at Transform(xpos=0.4, ypos=0.3)
            "Sample successfully collected."
            jump sample
        "Using a dry swab":
            $ asked["knife_swab"] = True
            hide clean swab
            show red swab at Transform(xpos=0.4, ypos=0.3)
            "Sample successfully collected."
            jump sample

label table_swab:
    scene inspect_table
    if asked["table_swab"]:
        show red swab at Transform(xpos=0.4, ypos=0.3)
        "Sample successfully collected."
        jump sample
    
    show clean swab at Transform(xpos=0.4, ypos=0.3)
    menu:
        "How would you like to collect the sample?"
        "Using a wet swab":
            $ asked["table_swab"] = True
            hide clean swab
            show red swab at Transform(xpos=0.4, ypos=0.3)
            "Sample successfully collected."
            jump sample
        "Using a dry swab":
            $ asked["table_swab"] = True
            hide clean swab
            show red swab at Transform(xpos=0.4, ypos=0.3)
            "Sample successfully collected."
            jump sample

label stool_swab:
    scene inspect_stool
    if asked["stool_swab"]:
        show red swab at Transform(xpos=0.4, ypos=0.3)
        "Sample successfully collected."
        jump sample
    
    show clean swab at Transform(xpos=0.4, ypos=0.3)
    menu:
        "How would you like to collect the sample?"
        "Using a wet swab":
            $ asked["stool_swab"] = True
            hide clean swab
            show red swab at Transform(xpos=0.4, ypos=0.3)
            "Sample successfully collected."
            jump sample
        "Using a dry swab":
            $ asked["stool_swab"] = True
            hide clean swab
            show red swab at Transform(xpos=0.4, ypos=0.3)
            "Sample successfully collected."
            jump sample

label sample:
    menu:
        "How would you like to proceed?"
        "Package the sample":
            jump splatter_alt
        "Run a presumptive test":
            hide red swab
            show screen bloody_swab
            $ remove_tools_from_toolbox(["swab_pack", "uv_light", "magnetic_powder", "silver_granular_powder", "scalebar", "tape", "backing_card", "gel_lifter", "gloves"])
            $ addToToolbox(["ethanol", "reagent", "hydrogen_peroxide"])
            call screen toolbox

label trash:
    $ default_mouse = "default"
    hide screen toolbox_presumptive
    menu:
        "Should I get rid of this swab?"
        "Yes":
            hide screen bloody_swab
            hide red swab
            $ player_kastle_meyer_order = []
            hide screen toolbox_presumptive
            if analyzing["stool"]:
                jump splatter
        "No":
            show screen bloody_swab
            call screen toolbox

label presumptive:
    if default_mouse == "ethanol":
        $ player_kastle_meyer_order.append("e")
        $ default_mouse = "default"
        "A drop of ethanol has been added to the sample."
    elif default_mouse == "reagent":
        $ player_kastle_meyer_order.append("r")
        $ default_mouse = "default"
        "A drop of phenolpthalin has been added to the sample."
    elif default_mouse == "hydrogen":
        $ player_kastle_meyer_order.append("h")
        $ default_mouse = "default"
        "A drop of hydrogen peroxide has been added to the sample."

    if len(player_kastle_meyer_order) > 5:
        $ default_mouse = "default"
        s think "I think you put in too many drops... you should try again."
        hide screen bloody_swab
        hide red swab
        $ player_kastle_meyer_order = []
        
        $ remove_tools_from_toolbox(["ethanol", "reagent", "hydrogen_peroxide", "gloves"])

        hide screen toolbox_presumptive

    if player_kastle_meyer_order in valid_kastle_meyer_orders:
        hide screen toolbox_presumptive
        hide screen bloody_swab
        hide red swab
        show pink swab at Transform(xpos=0.4, ypos=0.3)
        "The results of this test show that this substance is indeed blood."

        if analyzing["stool"]:
            $ analyzed["splatter presumptive"] = True
        elif analyzing["canvas"]:
            $ analyzed["canvas presumptive"] = True
        elif analyzing["knife"]:
            $ analyzed["knife presumptive"] = True
        elif analyzing["table"]:
            $ analyzed["table presumptive"] = True
        $ update_progress()

        $ player_kastle_meyer_order = []
        $ remove_tools_from_toolbox(["ethanol", "reagent", "hydrogen_peroxide", "gloves"])
        
    else:
        show screen bloody_swab
        call screen toolbox

# Splatter packaging
label splatter_alt:
    $ remove_tools_from_toolbox(["swab_pack", "uv_light", "magnetic_powder", "silver_granular_powder", "scalebar", "tape", "backing_card", "gel_lifter", "gloves"])   
    $ addToToolbox(["evidence_bag", "tube", "tamper_evident_tape"])
    if analyzing["stool"]:
        scene inspect_stool
    elif analyzing["canvas"]:
        scene inspect_canvas
    elif analyzing["knife"]:
        scene inspect_knife
    elif analyzing["table"]:
        scene inspect_table
    show red swab at Transform(xpos=0.4, ypos=0.3)
    $ tools["tube"] = True
    call screen toolbox

label splatter_packaging_0:
    hide red swab
    call screen sample_to_tube
    show sample test tube at Transform(xpos=0.4, ypos=0.2)
    "Sample successfully placed in tube."
    call screen toolbox

label splatter_packaging_1:
    hide sample test tube
    call screen tube_to_bag
    show evidence bag large at Transform(xpos=0.4, ypos=0.15)
    "Sample successfully placed in bag."
    call screen toolbox

label splatter_packaging_2:
    hide evidence bag large
    call screen tape_to_bag

label splatter_packaging_3:
    $ remove_tools_from_toolbox(["evidence_bag", "tube", "tamper_evident_tape", "gloves"])

    show casefile_evidence_idle at Transform(xpos=0.3, ypos=0.24)
    "The blood sample has been added to your evidence."
    if analyzing["stool"]:
        $ analyzing["stool"] = False
        $ analyzed["splatter packaged"] = True
        $ addToInventory(["splatter"])
        hide casefile_evidence_idle
    elif analyzing["canvas"]:
        $ analyzing["canvas"] = False
        $ analyzed["canvas packaged"] = True
        $ addToInventory(["splatter"])
        hide casefile_evidence_idle
    elif analyzing["knife"]:
        $ analyzing["knife"] = False
        $ analyzed["knife packaged"] = True
        $ addToInventory(["splatter"])
        hide casefile_evidence_idle
    elif analyzing["table"]:
        $ analyzing["table"] = False
        $ analyzed["table packaged"] = True
        $ addToInventory(["splatter"])
        hide casefile_evidence_idle
    $ update_progress()
    call crimescene