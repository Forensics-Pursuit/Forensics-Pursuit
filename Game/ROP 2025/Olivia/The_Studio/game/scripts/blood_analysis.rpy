"""
This file contains all labels and functions related to the blood analysis
"""
init python:
    def add_toolbox_blood_items():
        """Adds necessary blood collection items to inventory.
        """
        tools["swab"] = True
        tools["gloves"] = True
        add_tools_to_toolbox(["Swab Pack"])
        # add_tools_to_toolbox(["Gloves"])

    # def add_toolbox_print_items():
    #     """Adds necessary fingerprint collection items to inventory.
    #     """

label click_canvas:
    $ default_mouse = "default"
    hide screen casefile_physical
    hide screen casefile_photos
    hide screen notebook_screen
    scene inspect_canvas
    show screen back_button

    if analyzed["canvas presumptive"]:
        $ analyzing["canvas"] = False
        s "You've already inspected the canvas."
        call crimescene from _call_crimescene
    
    $ analyzing["canvas"] = True

    if encountered["canvas"] == False:
        $ encountered["canvas"] = True
        "New photo added to evidence."

    $ remove_toolbox_items()
    $ add_toolbox_blood_items()
    $ show_toolbox()
    call screen inventory
    hide screen notebook_screen

label click_stool:
    $ default_mouse = "default"
    hide screen casefile_physical
    hide screen casefile_photos
    hide screen notebook_screen
    scene inspect_stool
    show screen back_button

    if analyzed["splatter presumptive"]:
        $ analyzing["stool"] = False
        s normal3 "You've finished analyzing the splatter."
        call crimescene from _call_crimescene_1

    $ analyzing["stool"] = True

    if encountered["stool"] == False:
        $ encountered["stool"] = True
        "New photo added to evidence."    

    $ remove_toolbox_items()
    $ add_toolbox_blood_items()
    $ show_toolbox()
    call screen inventory
    hide screen notebook_screen

label click_knife:
    $ default_mouse = "default"
    hide screen casefile_physical
    hide screen casefile_photos
    hide screen notebook_screen
    scene inspect_knife
    show screen back_button

    if analyzed["knife presumptive"] and analyzed["knife fingerprint"] and analyzed["knife fingerprint alt"] :
        $ analyzing["knife"] = False
        s "You've already inspected the knife"
        call crimescene from _call_crimescene_2

    $ analyzing["knife"] = True
    $ tools["uv light"] = True

    if encountered["knife"] == False:
        $ encountered["knife"] = True
        "New photo added to evidence."

    $ add_tools_to_toolbox(["Swab Pack"])
    if not analyzed["knife presumptive"]:
        $ add_toolbox_blood_items()
    if not (analyzed["knife fingerprint"] and analyzed["knife fingerprint alt"]):
        $ remove_toolbox_items()
        $ add_tools_to_toolbox(["UV Light", "Magnetic Powder", "Silver Granular Powder", "Scalebar", "Tape", "Backing Card", "Gel Lifter"])
    $ show_toolbox()
    call screen inventory
    hide screen notebook_screen

label click_table:
    $ remove_toolbox_items()
    $ default_mouse = "default"
    hide screen casefile_physical
    hide screen casefile_photos
    hide screen notebook_screen
    scene inspect_table
    show screen back_button

    if analyzed["table presumptive"]:
        $ analyzing["table"] = False
        s normal2 "You've already inspected the table"
        call crimescene from _call_crimescene_3

    $ analyzing["table"] = True

    if encountered["table"] == False:
        $ encountered["table"] = True
        "New photo added to evidence."

    $ remove_toolbox_items()
    $ add_toolbox_blood_items()
    $ show_toolbox()
    call screen inventory
    hide screen notebook_screen

label canvas_swab:
    $ remove_toolbox_items()
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
            $ add_sample_mistake("Dry Swab on Dried Stain")
            $ asked["canvas_swab"] = True
            hide clean swab
            show red swab at Transform(xpos=0.4, ypos=0.3)
            "Sample successfully collected."
            jump sample

label knife_swab:
    $ remove_toolbox_items()
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
            $ add_sample_mistake("Dry Swab on Dried Stain")
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
            $ add_sample_mistake("Wet Swab on Wet Stain")
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
            $ add_sample_mistake("Wet Swab on Wet Stain")
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
    $ remove_toolbox_items()
    menu:
        "How would you like to proceed?"
        "Package the sample":
            jump splatter_alt
        "Run a presumptive test":
            hide red swab
            show screen bloody_swab
            $ remove_toolbox_items()
            $ add_tools_to_toolbox(["Ethanol", "Reagent", "Hydrogen Peroxide"])
            $ show_toolbox()
            call screen inventory

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
            $ show_toolbox()
            call screen inventory

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

    $ check_kastle_meyer_order()

    if len(player_kastle_meyer_order) > 5:
        $ default_mouse = "default"
        s think "I think you put in too many drops... you should try again."
        hide screen bloody_swab
        hide red swab
        $ player_kastle_meyer_order = []
        
        $ remove_toolbox_items()

        hide screen toolbox_presumptive

    if player_kastle_meyer_order in valid_kastle_meyer_orders:
        hide screen toolbox_presumptive
        hide screen bloody_swab
        hide red swab
        
        if not analyzing["table"]:
            show pink swab at Transform(xpos=0.4, ypos=0.3)
            "The results of this test show that this substance appears to be blood."
        else:
            "The results of this test show that this substance does not appear to be blood."

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
        $ remove_toolbox_items()
        $ tested_swab = True

        # The tested swab has chemicals on it, so it shouldn't be packaged.
        menu:
            "What would you like to do with the tested swab?"
            "Package this swab":
                hide pink swab
                jump splatter_alt
            "Throw it out and collect a fresh sample":
                hide pink swab
                $ tested_swab = False
                if analyzing["stool"]:
                    jump stool_swab
                elif analyzing["canvas"]:
                    jump canvas_swab
                elif analyzing["knife"]:
                    jump knife_swab
                else:
                    jump table_swab

    else:
        show screen bloody_swab
        $ show_toolbox()
        call screen inventory

# Splatter packaging
label splatter_alt:
    $ check_presumptive_done()
    if tested_swab:
        $ add_sample_mistake("Test Swab Collected")
        $ tested_swab = False
    $ remove_toolbox_items()
    $ add_tools_to_toolbox(["Evidence Bag", "Tube", "Tamper Evident Tape"])
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
    $ show_toolbox()
    call screen inventory

label splatter_packaging_0:
    hide red swab
    call screen sample_to_tube
    show sample test tube at Transform(xpos=0.4, ypos=0.2)
    "Sample successfully placed in tube."
    $ show_toolbox()
    call screen inventory

label splatter_packaging_1:
    hide sample test tube
    call screen tube_to_bag
    show evidence bag large at Transform(xpos=0.4, ypos=0.15)
    "Sample successfully placed in bag."
    $ show_toolbox()
    call screen inventory

label splatter_packaging_2:
    hide evidence bag large
    call screen tape_to_bag

label splatter_packaging_3:
    $ remove_toolbox_items()

    show casefile_evidence_idle at Transform(xpos=0.3, ypos=0.24)
    "The blood sample has been added to your evidence."
    if analyzing["stool"]:
        $ analyzing["stool"] = False
        $ analyzed["splatter presumptive"] = True
        $ tasks["Analyze the splatter by the stool"] = True
        $ custom_notify("Analyzed stool splatter!", True)
        $ add_to_evidence(["Stool Splatter Sample"])
        hide casefile_evidence_idle
    elif analyzing["canvas"]:
        $ analyzing["canvas"] = False
        $ analyzed["canvas presumptive"] = True
        $ tasks["Analyze the canvas"] = True
        $ custom_notify("Analyzed canvas!", True)
        $ add_to_evidence(["Canvas Blood Sample"])
        hide casefile_evidence_idle
    elif analyzing["knife"]:
        $ analyzing["knife"] = False
        $ analyzed["knife presumptive"] = True
        $ tasks["Analyze the blood on the knife"] = True
        $ custom_notify("Analyzed the bloody knife!", True)
        $ add_to_evidence(["Knife Blood Sample"])
        hide casefile_evidence_idle
    elif analyzing["table"]:
        $ analyzing["table"] = False
        $ analyzed["table presumptive"] = True
        $ tasks["Analyze the table"] = True
        $ custom_notify("Analyzed the table!", True)
        $ add_to_evidence(["Table Stain Sample"])
        hide casefile_evidence_idle
    $ update_progress()
    call crimescene from _call_crimescene_4