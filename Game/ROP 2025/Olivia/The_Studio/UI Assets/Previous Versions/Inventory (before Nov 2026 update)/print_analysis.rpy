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
    call screen toolbox

label knife_fingerprint_2:
    if analyzed["knife fingerprint alt"]:
        $ tools["silver granular powder"] = False
        scene inspect_knife
        s "You've already analyzed this print."
        jump crimescene
    $ analyzing["knife fingerprint alt"] = True
    scene inspect_knife
    call screen toolbox

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
    call screen toolbox

label fingerprint_scalebar:
    if analyzing["knife fingerprint"]:
        scene fingerprint scalebar
    else:
        scene fingerprint scalebar alt
    call screen toolbox
    
label fingerprint_taped:
    if analyzing["knife fingerprint"]:
        scene fingerprint taped
    else:
        scene fingerprint taped alt
    call screen toolbox

label fingerprint_backing:
    if analyzing["knife fingerprint"]:
        scene fingerprint backing
    else:
        scene fingerprint backing alt
    python:
        removal_list = ["swab_back", "uv_light", "magnetic_powder", "silver_granular_powder", "scalebar", "tape", "backing_card", "gel_lifter"]
        for item in removal_list:
            if item in toolbox_items:
                removeToolboxItem(toolbox_sprites[toolbox_items.index(item)])
    $ addToToolbox(["evidence_bag", "tube", "tamper_evident_tape"])
    call screen toolbox

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
    call screen toolbox

label packaging_1:
    show inspect_knife
    if analyzing["knife"]:
        call screen fingerprint_to_bag
    $ tools["bag"] = False
    show evidence bag large at Transform(xpos=0.4, ypos=0.15)
    "Sample successfully placed in bag."
    call screen toolbox

label packaging_2:
    hide evidence bag large
    call screen tape_to_bag

label packaging_3:
    show casefile_evidence_idle at Transform(xpos=0.3, ypos=0.24)
    "The fingerprint has been added to your evidence."

    if analyzing["knife fingerprint"]:
        $ analyzed["knife fingerprint"] = True
        $ analyzing["knife fingerprint"] = False
        if not analyzed["knife fingerprint alt"]:
            $ custom_notify("Analyzed first fingerprint!", True)
        else:
            $ custom_notify("Analyzed second fingerprint!", True)

    elif analyzing["knife fingerprint alt"]:
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
    $ addToInventory(["fingerprint"])

    hide casefile_evidence_idle

    $ remove_toolbox_items()
    jump crimescene
