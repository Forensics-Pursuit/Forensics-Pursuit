# # 
# #This file contains all custom screens used in the game.
# # 

screen notebook():
    zorder 100
    imagebutton:
        idle (Animation("images/ui/notebook_icon.png", 0.5, "images/ui/notebook_icon_hover.png", 0.5) if not notebook_clicked else "images/ui/notebook_icon.png")
        hover "images/ui/notebook_icon_hover.png"
        xpos 1830 ypos 20
        at Transform(zoom=0.15)
        action [Function(toggle_notebook), SetVariable("notebook_clicked", True)]

screen notebook_screen():
    zorder 100
    frame:
        xalign 1.02
        yalign 0.02
        xsize 590
        ysize 300
        xpadding 10
        ypadding 20
        background "images/ui/notebook_paper.png"

        vbox:
            spacing 10
            label " " style "heading_text"

            for i, task in enumerate(tasks, 1):
                if tasks[task]:
                    text f"{i}. {task}" style "strikethrough_text"
                else:
                    text f"{i}. {task}" style "instructions_text"


screen ui():
    # This is the case file displayed on the top left corner of the screen when the player is in the corridor.
    zorder 2

    hbox:
        xpos 0.02 ypos 0.12
        imagebutton:
            auto "case_file_%s.png" at Transform(zoom=2.5) mouse "pointer"
            hovered Notify("evidence")
            action Function(close_menu)

# Contents of casefile ---------------------------------------------------------------------------------------
screen casefile():
    # This is screen displayed after the player clicks on the case file.
    # It allows the player to choose between the physical evidence and the photos.
    zorder 1
    modal True
    add "casefile_inventory.png"

    text "Evidence Collected" xpos 0.42 ypos 0.15
    text "Physical Evidence" xpos 0.27 ypos 0.7
    text "Photo Evidence" xpos 0.565 ypos 0.7

    hbox:
        xpos 0.17 ypos 0.1
        imagebutton:
            auto "back_button_%s.png" at Transform(zoom=0.2)
            action Function(close_menu)

    hbox:
        xpos 0.2 ypos 0.23
        imagebutton:
            auto "casefile_evidence_%s.png" at Transform(zoom=0.7) mouse "pointer"
            hovered Notify("collected evidence")
            action [ToggleScreen("casefile"), ToggleScreen("casefile_physical")]
    
    hbox:
        xpos 0.5 ypos 0.27
        imagebutton:
            auto "casefile_photos_%s.png" at Transform(zoom=1.5)
            hovered Notify("photos")
            action [ToggleScreen("casefile"), ToggleScreen("casefile_photos")]
    
# Contents of toolbox --------------------------------------------------------------------------------------
screen toolbox_print():
    # This is the toolbox used for the fingerprint.
    zorder 1
    python:
        tool_positions = [
            ("uv light", 0.89, 0.084, "uv_light_%s.png", "flashlight", "dark_overlay_with_mouse"),
            ("magnetic powder", 0.88, 0.27, "magnetic_powder_%s.png", "magnetic powder", "fingerprint_dusted"),
            ("silver granular powder", 0.885, 0.5, "silver_granular_powder_%s.png", "silver granular powder", "fingerprint_1_dusted"),
            ("scalebar", 0.88, 0.65, "scalebar_%s.png", "scalebar", "fingerprint_scalebar"),
            ("tape", 0.885, 0.8, "tape_%s.png", "tape", "fingerprint_taped"),
            ("backing", 0, 0.13, "backing_card_%s.png", "backing card", "fingerprint_backing"),
            ("packaging", 0, 0.34, "casefile_evidence_%s.png", "packaging", "packaging"),
            ("gel lifter", 0, 0.45, "gel_lifter_%s.png", "gel lifter", None)
        ]
    for tool, x, y, img, tip, jump in tool_positions:
        hbox:
            xpos x ypos y
            imagebutton:
                sensitive tools[tool]
                auto img at Transform(zoom=0.06 if "powder" in tool else 0.35)
                hovered Notify(tip)
                action [SetDict(tools, tool, False)] + ([Jump(jump)] if jump else [])

screen toolbox_blood():
    # This is the toolbox used for the bloody footprint and the splatter.
    # It contains the swab and the hungarian red reagent.
    zorder 1
    hbox:
        xpos 0.13 ypos 0.03
        imagebutton:
            auto "back_button_%s.png" at Transform(zoom=0.2)
            action [If(analyzing["splatter"], SetDict(analyzing, "splatter", False)), Jump("crimescene")]
    hbox:
        xpos 0.77 ypos 0.11
        imagebutton:
            sensitive tools["swab"]
            hovered Notify("swab")
            auto "swab_pack_%s.png" at Transform(zoom=0.8)
            action [
                SetDict(tools, "swab", False),
                If(analyzing["table"], Jump("table_swab")),
                If(analyzing["splatter"], Jump("splatter_swab")),
                If(analyzing["knife"] and not (analyzing["knife fingerprint"] or analyzing["knife fingerprint alt"]), Jump("knife_swab")),
                If(analyzing["canvas"], Jump("canvas_swab"))]

screen toolbox_presumptive():
    # This is the toolbox used for the presumptive test.
    zorder 1
    python:
        drops = [
            ("ethanol", 0.88, 0.02),
            ("reagent", 0.885, 0.26),
            ("hydrogen", 0.885, 0.5)
        ]
    for chem, x, y in drops:
        hbox:
            xpos x ypos y
            imagebutton:
                auto f"{chem}_%s.png"
                hovered Notify(chem)
                action [SetVariable("default_mouse", chem), ToggleScreen("toolbox_presumptive")]
                mouse "dropper"
    
    hbox:
        xpos 0.898 ypos 0.75
        imagebutton:
            auto "trash_%s"
            hovered Notify("trash")

            action Jump("trash")

screen toolbox_packaging():
    # This is the toolbox used for packaging the evidence.
    zorder 1
    hbox:
        xpos 0.89 ypos 0.13
        imagebutton:
            sensitive tools["tube"]
            hovered Notify("tube")
            auto "tube_%s" at Transform(zoom=0.8)
            action [SetDict(tools, "tube", False), SetDict(tools, "bag", True), If(analyzing["stool"] or analyzing["knife"], Jump("splatter_packaging_0"))]
    hbox:
        xpos 0.885 ypos 0.32
        imagebutton:
            sensitive tools["bag"]
            auto "evidence_bag_%s" at Transform(zoom=0.9)
            hovered Notify("evidence bag")
            action [SetDict(tools, "tube", False), SetDict(tools, "bag", False), SetDict(tools, "tamper evident tape", True), If(analyzing["knife"], Jump("packaging_1")), If((analyzing["knife"] or analyzing["canvas"] or analyzing["stool"] or analyzing["table"]), Jump("splatter_packaging_1"))]
    
    hbox:
        xpos 0.885 ypos 0.51
        imagebutton:
            sensitive tools["tamper evident tape"]
            hovered Notify("tamper evident tape")
            auto "tamper_evident_tape_%s.png" at Transform(zoom=0.9)
            action [SetDict(tools, "tamper evident tape", False), If((analyzing["knife fingerprint"] or analyzing["knife fingerprint alt"]), Jump("packaging_2")), If((analyzing["knife"] or analyzing["canvas"] or analyzing["stool"] or analyzing["table"]), Jump("splatter_packaging_2"))]

# Drag and drop screens -------------------------------------------------------------------------------

screen sample_to_tube():
    draggroup:
        drag:
            drag_name "sample"
            child "red swab cropped"
            xpos 0.28 ypos 0.3
            draggable True
            droppable True
            dragging item_dragging_package
            dragged item_dragged_package

        drag:
            drag_name "tube"
            child "tube"
            xpos 0.59 ypos 0.29
            draggable True
            droppable True
            dragging item_dragging_package
            dragged item_dragged_package


screen tube_to_bag():
    draggroup:
        drag:
            drag_name "sample test tube"
            child "sample test tube"
            xpos 0.23 ypos 0.2
            draggable True
            droppable True
            dragging item_dragging_package
            dragged item_dragged_package

        drag:
            drag_name "bag"
            child "evidence bag large"
            xpos 0.54 ypos 0.19
            draggable True
            droppable True
            dragging item_dragging_package
            dragged item_dragged_package

screen fingerprint_to_bag():
    draggroup:
        drag:
            drag_name "fingerprint"
            child "backing fingerprint"
            xpos 0.25 ypos 0.3
            draggable True
            droppable True
            dragging item_dragging_package
            dragged item_dragged_package

        drag:
            drag_name "bag"
            child "evidence bag large"
            xpos 0.55 ypos 0.2
            draggable True
            droppable True
            dragging item_dragging_package
            dragged item_dragged_package

screen tape_to_bag():
    draggroup:
        drag:
            drag_name "tape"
            child "tamper evident tape"
            xpos 0.25 ypos 0.3
            draggable True
            droppable True
            dragging item_dragging_package
            dragged item_dragged_package
        
        drag:
            drag_name "bag"
            child "evidence bag large"
            xpos 0.55 ypos 0.2
            draggable True
            droppable True
            dragging item_dragging_package
            dragged item_dragged_package

screen folder_to_bag():
    draggroup:
        drag:
            drag_name "folder"
            child "folder"
            xpos 0.25 ypos 0.3
            draggable True
            droppable True
            dragging item_dragging_package
            dragged item_dragged_package

        drag:
            drag_name "bag"
            child "evidence bag large"
            xpos 0.55 ypos 0.2
            draggable True
            droppable True
            dragging item_dragging_package
            dragged item_dragged_package

screen letters_to_bag():
    draggroup:
        drag:
            drag_name "letters"
            child "letters"
            xpos 0.20 ypos 0.22
            draggable True
            droppable True
            dragging item_dragging_package
            dragged item_dragged_package

        drag:
            drag_name "bag"
            child "evidence bag large"
            xpos 0.55 ypos 0.2
            draggable True
            droppable True
            dragging item_dragging_package
            dragged item_dragged_package

# Backgrounds -------------------------------------------------------------------------------------------
screen crimescene():
    zorder 0
    default bg_toggle = True
    timer 0.5 repeat True action ToggleScreenVariable("bg_toggle")

    if bg_toggle:
        add "backgrounds/room_1.png"
    else:
        add "backgrounds/room_2.png"

    use full_inventory()

    default remaining_count = get_progress()

    showif True:
        use progress_counter

    python:
        objects = [
            ("knife", 200, 950),
            ("canvas", 200, 200),
            ("letters", 1050, 250),
            ("stool", 300, 750),
            ("table", 1130, 575),
            ("laptop", 1215, 390),
            ("drawer", 915, 415)
        ]
    for name, x, y in objects:
        imagebutton:
            idle f"images/objects/{name}.png"
            hover f"images/objects/hover/{name}.png"
            xpos x ypos y
            action Jump(f"click_{name}")

    showif encountered["canvas"]:
        add "marker 1" at Transform(xpos=0.06, ypos=0.76, zoom= 0.32)
    
    showif encountered["knife"]:
        add "marker 2" at Transform(xpos=0.16, ypos=0.87, zoom=0.3)
    
    showif encountered["stool"]:
        add "marker 3" at Transform(xpos=0.55, ypos=0.83, zoom=0.33)

    showif encountered["table"]:
        add "marker 4" at Transform(xpos=0.81, ypos=0.88, zoom=0.33)

screen bloody_swab():
    # This is the screen used to allow the player to add drops of chemicals
    # to the swab during the presumptive test.
    imagebutton:
        idle "red swab" at Transform(xpos=0.4, ypos=0.3)
        action Jump("presumptive")

screen dark_overlay_with_mouse():
    # This is the screen used after pressing the flashlight when analyzing
    # the door.
    modal True

    default mouse = (0, 0)

    # Timer to repeatedly update the mouse position
    timer 0.02 repeat True action SetScreenVariable("mouse", renpy.get_mouse_pos())

    imagemap:
        idle "images/backgrounds/inspect_knife_fingerprint.png"
        # fingerprint 1
        hotspot (1091, 627, 87, 84) action [SetDict(tools, "uv light", False), SetDict(tools, "silver granular powder", True), SetDict(analyzing, "knife fingerprint", True), ToggleScreen("dark_overlay_with_mouse"), Jump("knife_fingerprint_1")]
        
        # fingerprint 2
        hotspot (1268, 650, 69, 77) action [SetDict(tools, "uv light", False), SetDict(tools, "silver granular powder", True), SetDict(analyzing, "knife fingerprint alt", True), ToggleScreen("dark_overlay_with_mouse"), Jump("knife_fingerprint_2")]

    # Adding the darkness overlay with the current mouse position
    add "darkness" pos mouse anchor (0.5, 0.5)

screen outside_room():
    zorder 0

    imagebutton:
        idle "images/objects/door.png"
        hover "images/objects/hover/door.png"
        xpos 750
        ypos 125
        action [Hide("outside_room"), Jump("go_to_scene")]

screen back_button():
    zorder 100
    textbutton "Back" xpos 1800 ypos 1000 action Jump("crimescene")

# screen inspect_canvas():
#     add "images/backgrounds/inspect_canvas.png" xpos 700 ypos 50
#     textbutton "Back" xpos 1800 ypos 1000 action Jump("crimescene")

# screen inspect_knife():
#     add "images/backgrounds/inspect_knife.png" xpos 600 ypos 200
#     textbutton "Back" xpos 1800 ypos 1000 action Jump("crimescene")

# screen inspect_table():
#     add "images/backgrounds/inspect_table.png" xpos 600 ypos 200
#     textbutton "Back" xpos 1800 ypos 1000 action Jump("crimescene")

# screen inspect_letters():
#     add "images/backgrounds/inspect_letters.png" xpos 10 ypos 10
#     textbutton "Back" xpos 1800 ypos 1000 action Jump("crimescene")

# screen inspect_stool():
#     add "images/backgrounds/inspect_stool.png" xpos 600 ypos 500
#     textbutton "Back" xpos 1800 ypos 1000 action Jump("crimescene")

# Interactibles  -------------------------------------------------------------------------------------------

default current_tab = "emily"

screen inspect_laptop():
    $ tasks["Inspect the computer"] = True
    $ default_mouse = "cursor"
    add "images/backgrounds/inspect_laptop.png" 

    if current_tab == "emily":
        add "images/backgrounds/laptop_emily.png"
    elif current_tab == "fred":
        add "images/backgrounds/laptop_fred.png"
    elif current_tab == "mom":
        add "images/backgrounds/laptop_mom.png"

    for i, tab in enumerate(["emily", "fred", "mom"]):
        imagebutton:
            idle Solid("#a0a0a010")
            hover Solid("#ffffff1e")
            xpos 336 ypos 247 + i * 140 xsize 230 ysize 130
            action SetVariable("current_tab", tab)

    textbutton "Back" xpos 1800 ypos 1000 action Jump("crimescene")

default drawer_open = False

screen inspect_drawer():
    $ default_mouse = "cursor"

    if drawer_open:
        add "images/backgrounds/inspect_drawer_open.png"
        imagebutton:
            idle "images/objects/cropped_folder.png"
            hover "images/objects/hover/cropped_folder.png"
            xpos 770
            ypos 385
            action Jump("click_folder")
        textbutton "Back" xpos 1800 ypos 1000 action [SetVariable("drawer_open", False)]
    else:
        add "images/backgrounds/inspect_drawer.png"
        imagebutton:
            idle Solid("#352f2d1c")
            hover Solid("#ffffff1e")
            xpos 790 ypos 603 xsize 335 ysize 134
            action SetVariable("drawer_open", True)
        textbutton "Back" xpos 1800 ypos 1000 action Jump("crimescene")

screen show_document():
    add "images/backgrounds/inspect_document.png"
    key "mouseup_1" action Return()

screen inspect_folder():
    $ default_mouse = "cursor"
    add "images/backgrounds/inspect_folder.png"

# UI

screen progress_counter():
    frame:
        xalign 0.0
        yalign 0.02
        padding (10, 5)
        background "#0008"
        text "Remaining tasks: [remaining_count]" size 30 color "#fff"
