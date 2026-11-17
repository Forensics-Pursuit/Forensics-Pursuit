"""
This file has all labels and functions related to psychology-related evidence.
"""
label click_folder:
    $ remove_toolbox_items()
    $ default_mouse = "default"
    hide screen casefile_physical
    hide screen casefile_photos
    hide screen notebook_screen
    call screen show_document
    scene inspect_folder

    if analyzed["folder"]:
        $ analyzing["folder"] = False
        s normal "You've already inspected the folder."
        jump crimescene

    $ analyzing["folder"] = True
    $ tools["bag"] = True
    $ add_tools_to_toolbox(["Evidence Bag", "Tube", "Tamper Evident Tape"])
    $ show_toolbox()
    call screen inventory

label click_laptop:
    $ default_mouse = "default"
    hide screen casefile_physical
    hide screen casefile_photos
    hide screen notebook_screen
    $ tasks["Inspect the computer"] = True
    call screen inspect_laptop

label click_letters:
    $ remove_toolbox_items()
    $ default_mouse = "default"
    hide screen casefile_physical
    hide screen casefile_photos
    hide screen notebook_screen

    if analyzed["letters"]:
        scene no_letters
        $ analyzing["letters"] = False
        s normal "You've already inspected the letters."
        jump crimescene

    scene inspect_letters

    $ analyzing["letters"] = True
    $ tools["bag"] = True
    $ add_tools_to_toolbox(["Evidence Bag", "Tube", "Tamper Evident Tape"])
    $ show_toolbox()
    call screen inventory

label click_drawer:
    $ remove_toolbox_items()
    $ default_mouse = "default"
    hide screen casefile_physical
    hide screen casefile_photos
    hide screen notebook_screen
    call screen inspect_drawer

label psych_packaging_1:
    show inspect_drawer_open
    $ tools["bag"] = True
    if analyzing["folder"]:
        scene inspect_drawer
        call screen folder_to_bag
    elif analyzing["letters"]:
        scene no_letters
        call screen letters_to_bag
    show evidence bag large at Transform(xpos=0.4, ypos=0.15)
    "Evidence successfully placed in bag."
    $ show_toolbox()
    call screen inventory

label psych_packaging_2:
    hide evidence bag large
    call screen tape_to_bag

label psych_packaging_3:
    show casefile_evidence_idle at Transform(xpos=0.3, ypos=0.24)
    "The documents have been added to your evidence."

    if analyzing["folder"]:
        $ analyzing["folder"] = False
        $ analyzed["folder"] = True
        $ tasks["Package the folder"] = True
        $ add_to_evidence(["Folder"])
    elif analyzing["letters"]:
        $ analyzing["letters"] = False
        $ analyzed["letters"] = True
        $ tasks["Package the letters"] = True
        $ add_to_evidence(["Letters"])
    $ update_progress()

    hide casefile_evidence_idle

    $ remove_toolbox_items()
    jump crimescene
