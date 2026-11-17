"""
This file has all labels and functions related to fingerprints.
"""

label knife_fingerprint_1:
    if analyzed["knife fingerprint"]:
        $ tools["silver granular powder"] = False
        scene inspect_knife
        s "You've already analyzed this print."
        jump crimescene
    $ analyzing["knife fingerprint"] = True
    scene inspect_knife
    $ show_toolbox()
    call screen inventory

label knife_fingerprint_2:
    if analyzed["knife fingerprint alt"]:
        $ tools["silver granular powder"] = False
        scene inspect_knife
        s "You've already analyzed this print."
        jump crimescene
    $ analyzing["knife fingerprint alt"] = True
    scene inspect_knife
    $ show_toolbox()
    call screen inventory

#---------------------
# Processing
#---------------------

label fingerprint_dusted:
    $ encountered["knife"] = True
    if analyzing["knife fingerprint"]:
        scene fingerprint dusted
    else:
        scene fingerprint dusted alt
    "New photo added to evidence."
    $ show_toolbox()
    call screen inventory

label fingerprint_scalebar:
    if analyzing["knife fingerprint"]:
        scene fingerprint scalebar
    else:
        scene fingerprint scalebar alt
    $ show_toolbox()
    call screen inventory
    
label fingerprint_taped:
    if analyzing["knife fingerprint"]:
        scene fingerprint taped
    else:
        scene fingerprint taped alt
    $ show_toolbox()
    call screen inventory

label fingerprint_backing:
    if analyzing["knife fingerprint"]:
        scene fingerprint backing
    else:
        scene fingerprint backing alt
    $ remove_tools_from_toolbox(["UV Light", "Magnetic Powder", "Silver Granular Powder", "Scalebar", "Tape", "Backing Card", "Gel Lifter"])
    $ add_tools_to_toolbox(["Evidence Bag", "Tube", "Tamper Evident Tape"])
    $ show_toolbox()
    call screen inventory

#---------------------
# Packaging
#---------------------

label packaging:
    if analyzing["knife fingerprint"]:
        scene fingerprint dusted
    elif analyzing["knife fingerprint alt"]:
        scene fingerprint dusted alt
    $ tools["bag"] = True
    if analyzing["knife"]:
        show backing fingerprint at Transform(xpos=0.3, ypos=0.2, zoom=1.6)
    
    $ remove_toolbox_items()
    $ show_toolbox()
    call screen inventory

label packaging_1:
    show inspect_knife
    if analyzing["knife"]:
        call screen fingerprint_to_bag
    $ tools["bag"] = False
    show evidence bag large at Transform(xpos=0.4, ypos=0.15)
    "Sample successfully placed in bag."
    $ show_toolbox()
    call screen inventory

label packaging_2:
    hide evidence bag large
    call screen tape_to_bag

label packaging_3:
    show casefile_evidence_idle at Transform(xpos=0.3, ypos=0.24)
    "The fingerprint has been added to your evidence."

    if analyzing["knife fingerprint"]:
        $ add_to_evidence(["Knife Fingerprint 1"])
        $ analyzed["knife fingerprint"] = True
        $ analyzing["knife fingerprint"] = False
        if not analyzed["knife fingerprint alt"]:
            $ custom_notify("Analyzed first fingerprint!", True)
        else:
            $ custom_notify("Analyzed second fingerprint!", True)

    elif analyzing["knife fingerprint alt"]:
        $ add_to_evidence(["Knife Fingerprint 2"])
        $ analyzed["knife fingerprint alt"] = True
        $ analyzing["knife fingerprint alt"] = False
        if not analyzed["knife fingerprint"]:
            $ custom_notify("Analyzed first fingerprint!", True)
        else:
            $ custom_notify("Analyzed second fingerprint!", True)
    if analyzed["knife fingerprint"] and analyzed["knife fingerprint alt"]:
        $ tasks["Analyze the fingerprints (2) on the knife"] = True
    $ analyzing["knife"] = False
    $ update_progress()

    hide casefile_evidence_idle

    $ remove_toolbox_items()
    jump crimescene
