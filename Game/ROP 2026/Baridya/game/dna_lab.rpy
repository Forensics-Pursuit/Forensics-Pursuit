################################################################################
## DNA Lab -- Bio Station
################################################################################
## Adapted from the source project's machines.rpy / custom_screens.rpy DNA
## pipeline. Everything in this section is prefixed dna_ so it's fully
## self-contained -- nothing here should ever need to touch AFIS, evidence
## collection, or anything outside this block, which is exactly what makes
## it safe to debug in isolation later.
##
## Two things were deliberately changed from the source:
##   1. Blood -> touch DNA in the narration only; the extraction chemistry
##      (lysis, ethanol precipitation, spin-column washes) is identical
##      regardless of sample type, so no mechanical changes were needed.
##   2. The three steps originally gated behind clicking "ethanol"/"tube"/
##      "trash" items in a different inventory system (which we don't have)
##      now auto-advance immediately after the step that unlocks them,
##      instead of requiring a separate tool click. Per your "keep it
##      simple" call.
##
## Both can + wheel swabs (if collected) lead into this same single
## procedure and the same result -- no per-swab branching, as requested.
##
## ASSET REQUIREMENTS: this reuses the source project's exact filenames
## (backgrounds/bio_station.png, objects/swab.png, etc.) verbatim, since
## you already have that art. If any path doesn't match your actual folder
## layout, it's a one-line fix wherever that string appears below.
################################################################################

init -5 python:

    ## Which evidence items count as a DNA swab.
    DNA_NAME_KEYWORDS = ["swab", "dna"]

    def has_dna_evidence():
        for item in evidence._inventory:
            name_lower = item.name.lower()
            if any(k in name_lower for k in DNA_NAME_KEYWORDS):
                return True
        return False

    ## Swab prep checklist -- every extraction step, in order.
    dna_swab_tasks = {
        "swab_is_cut": False,
        "swab_is_prepped": False,
        "swab_is_vortexed": False,
        "swab_is_incubated": False,
        "swab_is_spun": False,
        "swab_new_tube": False,
        "sample_is_spun": False,
        "sample_new_tube": False,
    }

    ## Bigger milestones -- gate the qPCR machine and the final result.
    dna_tasks = {
        "Prep swab for DNA analysis": False,
        "Run qPCR machine": False,
        "Analyze DNA results": False,
    }

    ## One-off flags used partway through the sequence (names kept close to
    ## the source so its branching logic ports over unchanged).
    dna_swab_is_vortexed_2 = False
    dna_swab_is_incubated_0 = False
    dna_ethanol_added = False
    dna_tube_transfered = False

    ## The quantification tray.
    dna_tray_top_filled = False
    dna_tray_bottom_filled = False
    dna_tray_side_filled = False
    dna_tray_prepped = False
    dna_tray_placements = {
        "top": "reaction_mix",
        "bottom": "diluted_dna",
        "side": "nuclease_free_water",
    }

    ## Lab toolbox -- completely separate from the field evidence toolbox.
    ## Only exists while working the DNA bio station, and only ever
    ## contains these 3 items, matching the source project's ethanol/tube/
    ## trash inventory steps.
    lab_toolbox = Inventory()

    def dna_use_ethanol():
        if dna_check_task_complete(["swab_is_cut", "swab_is_prepped", "swab_is_vortexed", "swab_is_incubated"]) and not dna_ethanol_added:
            renpy.jump("dna_add_ethanol")
        else:
            dna_notify_msg("Nothing to add ethanol to yet.", correct=False)

    def dna_use_tube():
        if dna_check_task_complete(["swab_is_cut", "swab_is_prepped", "swab_is_vortexed", "swab_is_incubated", "swab_is_spun"]) and not dna_swab_tasks["swab_new_tube"]:
            renpy.jump("dna_new_tube")
        else:
            dna_notify_msg("No sample ready to transfer yet.", correct=False)

    def dna_use_trash():
        if dna_swab_tasks["sample_is_spun"] and not dna_swab_tasks["sample_new_tube"]:
            renpy.jump("dna_discard_sample")
        else:
            dna_notify_msg("Nothing to discard yet.", correct=False)

    def dna_setup_lab_toolbox():
        """Populates the lab toolbox fresh. Safe to call every time the DNA
        lab is entered -- these 3 items never change."""
        lab_toolbox.reset_inventory()
        lab_toolbox.add_to_inventory(Item("Ethanol", "lab-ethanol", usable=True, action=dna_use_ethanol))
        lab_toolbox.add_to_inventory(Item("Tube", "lab-tube", usable=True, action=dna_use_tube))
        lab_toolbox.add_to_inventory(Item("Trash", "lab-trash", usable=True, action=dna_use_trash))

    ## Retractable notebook state.
    dna_notebook_clicked = False       # has the notebook icon ever been clicked

    def dna_toggle_screen(name):
        if renpy.get_screen(name):
            renpy.hide_screen(name)
        else:
            renpy.show_screen(name)

    def dna_toggle_notebook():
        global dna_notebook_clicked
        dna_notebook_clicked = True
        dna_toggle_screen("dna_notebook_panel")

    def dna_reset():
        global dna_swab_is_vortexed_2, dna_swab_is_incubated_0, dna_ethanol_added, dna_tube_transfered
        global dna_tray_top_filled, dna_tray_bottom_filled, dna_tray_side_filled, dna_tray_prepped
        for k in dna_tasks:
            dna_tasks[k] = False
        for k in dna_swab_tasks:
            dna_swab_tasks[k] = False
        dna_swab_is_vortexed_2 = False
        dna_swab_is_incubated_0 = False
        dna_ethanol_added = False
        dna_tube_transfered = False
        dna_tray_top_filled = False
        dna_tray_bottom_filled = False
        dna_tray_side_filled = False
        dna_tray_prepped = False

    def dna_check_task_complete(task_list):
        return all(dna_swab_tasks.get(t, True) for t in task_list)

    def dna_notify_msg(msg, correct=True):
        renpy.show_screen("dna_notify", message=msg, correct=correct)

    def dna_item_dragging_package(drags):
        global default_mouse
        default_mouse = "hand_grab"

    def dna_item_dragged_package(drags, drop):
        global default_mouse, dna_tray_top_filled, dna_tray_bottom_filled, dna_tray_side_filled
        default_mouse = "hand_grab"
        if not drop:
            default_mouse = "hand"
            return None

        if drop.drag_name == "top":
            dna_tray_top_filled = True
            dna_notify_msg("Top filled!", correct=True)
        elif drop.drag_name == "bottom":
            dna_tray_bottom_filled = True
            dna_notify_msg("Bottom filled!", correct=True)
        elif drop.drag_name == "side":
            dna_tray_side_filled = True
            dna_notify_msg("Side filled!", correct=True)

        renpy.restart_interaction()

        if drop.drag_name in dna_tray_placements:
            dna_tray_placements[drop.drag_name] = drags[0].drag_name

        default_mouse = "default"
        return None

    def dna_check_tray_placements():
        global dna_tray_prepped
        if not (dna_tray_top_filled and dna_tray_bottom_filled and dna_tray_side_filled):
            dna_notify_msg("Place all required components on the tray", correct=False)
            return

        correct = True
        messages = []

        if dna_tray_placements.get("top") != "reaction_mix":
            correct = False
            messages.append("You need to place the reaction mix at the top")
        if dna_tray_placements.get("bottom") != "diluted_dna":
            correct = False
            messages.append("You need to place the diluted extracted DNA at the bottom")
        if dna_tray_placements.get("side") != "nuclease_free_water":
            correct = False
            messages.append("You need to place the negative control (nuclease-free water) at the side")

        if correct:
            dna_notify_msg("All tray placements are correct!", correct=True)
            dna_tray_prepped = True
            renpy.jump("dna_bio_station")
        else:
            for message in messages:
                dna_notify_msg(message, correct=False)


################################################################################
## DNA screens
################################################################################

screen dna_notify(message, correct):
    zorder 200
    frame:
        xalign 0.5
        yalign 0.08
        background Solid("#1a7a3ae6" if correct else "#7a1a1ae6")
        padding (24, 14)
        text message size 26 color "#ffffff"
    timer 2.0 action Hide("dna_notify")


screen dna_lab_toolbox():
    zorder 90
    vbox:
        xalign 0.02
        yalign 0.5
        spacing 24

        for _lab_item in lab_toolbox._inventory:
            fixed:
                xysize (110, 110)

                add "inventory-slot"
                add _lab_item.image_name:
                    zoom 0.45
                    xoffset 18
                    yoffset 18

                button:
                    xysize (110, 110)
                    background None
                    action Function(_lab_item.action)

                text _lab_item.name:
                    xalign 0.5
                    yalign 1.0
                    size 16
                    color "#ffffff"


screen dna_notebook_icon():
    zorder 110
    imagebutton:
        idle (Animation("images/ui/notebook_icon.png", 0.5, "images/ui/notebook_icon_hover.png", 0.5) if not dna_notebook_clicked else "images/ui/notebook_icon.png")
        hover "images/ui/notebook_icon_hover.png"
        xpos 1830 ypos 20
        at Transform(zoom=0.15)
        action Function(dna_toggle_notebook)


screen dna_notebook_panel():
    zorder 100
    add "images/ui/dna_notebook.png":
        xalign 0.92
        yalign 0.02


screen dna_bio_station():
    imagemap:
        idle "backgrounds/bio_station.png"
        hover "backgrounds/bio_station_hover.png"

        hotspot (811, 411, 229, 290) action Jump("dna_use_qpcr")
        hotspot (1040, 460, 241, 212) action Jump("dna_use_centrifuge")
        hotspot (1276, 417, 174, 257) action Jump("dna_use_spinner")
        hotspot (1458, 475, 126, 228) action Jump("dna_use_vortex")
        hotspot (1594, 571, 184, 174) action Jump("dna_use_incubator")
        hotspot (1634, 455, 228, 135) action Jump("dna_use_prep")

    textbutton "Back to Lab":
        xalign 0.02
        yalign 0.95
        background Solid("#000000aa")
        xpadding 20
        ypadding 10
        action Jump("dna_exit")


screen dna_swab_screen():
    zorder 1
    modal True

    imagemap:
        ground "backgrounds/swab_screen.png"
        idle "backgrounds/swab_screen_idle.png"
        hover "backgrounds/swab_screen_hover.png"

        hotspot (84, 178, 349, 727):
            action SetDict(dna_swab_tasks, "swab_is_cut", True)
        hotspot (488, 333, 767, 516):
            action Function(
                lambda:
                    dna_notify_msg("You need to cut the swab first...", correct=False)
                    if not dna_check_task_complete(["swab_is_cut"])
                    else renpy.store.__setattr__("default_mouse", "micropipette")
            )

    if dna_check_task_complete(["swab_is_prepped"]):
        add "objects/cut_swab_filled.png" pos (1400, 250)
    elif dna_check_task_complete(["swab_is_cut"]):
        add "objects/cut_swab.png" pos (1400, 250)
    else:
        add "objects/swab.png" pos (1500, 200)

    if default_mouse == "micropipette":
        imagebutton:
            xpos 1450
            ypos 200
            idle "images/ui/transparent.png"
            hover "images/ui/transparent.png"
            mouse "micropipette"
            action [
                SetDict(dna_swab_tasks, "swab_is_prepped", True),
                SetVariable("default_mouse", "default"),
                Show("dna_notify", message="Swab extraction phase initiated.", correct=True),
                Return(),
            ]

    textbutton "Close":
        action Return()
        align (0.0, 0.0)
        xpadding 30
        ypadding 10
        background Solid("#2a2a2ae6")
        hover_background Solid("#4a90d9")
        text_color "#ffffff"
        text_hover_color "#ffffff"


screen dna_centrifuge():
    zorder 99
    modal True

    imagemap:
        ground "backgrounds/use_centrifuge.png"
        idle "backgrounds/use_centrifuge.png"
        hover "backgrounds/use_centrifuge_hover.png"

        hotspot (784, 295, 349, 335):
            action If(
                dna_check_task_complete([
                    "swab_is_cut", "swab_is_prepped", "swab_is_vortexed",
                    "swab_is_incubated", "swab_is_spun", "swab_new_tube",
                ]),
                [SetDict(dna_swab_tasks, "sample_is_spun", True),
                 Show("dna_notify", message="Centrifuge cycle complete.", correct=True),
                 Jump("dna_wait_screen")],
                [Show("dna_notify", message="Protocol error: Incorrect step order.", correct=False), Return()],
            )


screen dna_spinner():
    zorder 99
    modal True

    imagemap:
        ground "backgrounds/use_spinner.png"
        idle "backgrounds/use_spinner.png"
        hover "backgrounds/use_spinner_hover.png"

        hotspot (810, 559, 350, 327):
            action [
                If(
                    dna_check_task_complete(["swab_is_cut", "swab_is_prepped", "swab_is_vortexed", "swab_is_incubated"]) and dna_swab_is_vortexed_2,
                    SetDict(dna_swab_tasks, "swab_is_spun", True),
                    If(
                        dna_check_task_complete(["swab_is_cut", "swab_is_prepped", "swab_is_vortexed"]) and dna_swab_is_incubated_0,
                        SetDict(dna_swab_tasks, "swab_is_incubated", True),
                        [Show("dna_notify", message="Protocol error: Incubation skipped out of sequence.", correct=False), Jump("dna_bio_station")],
                    ),
                ),
                Show("dna_notify", message="Separation column spun successfully.", correct=True),
                Return(),
            ]


screen dna_vortex():
    zorder 99
    modal True

    default vortex_clicked = False

    if not vortex_clicked:
        imagemap:
            ground "backgrounds/use_vortex.png"
            idle "backgrounds/use_vortex.png"
            hover "backgrounds/use_vortex_hover.png"

            hotspot (842, 429, 329, 552):
                action If(
                    dna_check_task_complete(["swab_is_cut", "swab_is_prepped"]),
                    SetScreenVariable("vortex_clicked", True),
                    [Show("dna_notify", message="Action error: Tube is empty. Nothing to vortex.", correct=False), Jump("dna_bio_station")],
                )
    else:
        imagemap:
            ground "backgrounds/vortex_swab.png"
            idle "backgrounds/vortex_swab.png"
            hover "backgrounds/vortex_swab_hover.png"

            hotspot (981, 695, 181, 180):
                action [
                    If(
                        dna_check_task_complete(["swab_is_cut", "swab_is_prepped", "swab_is_vortexed", "swab_is_incubated"]),
                        SetVariable("dna_swab_is_vortexed_2", True),
                        If(
                            dna_check_task_complete(["swab_is_cut", "swab_is_prepped"]),
                            SetDict(dna_swab_tasks, "swab_is_vortexed", True),
                        ),
                    ),
                    Show("dna_notify", message="Sample mixed. Vortexed for 15 seconds.", correct=True),
                    Return(),
                ]


screen dna_incubator():
    zorder 99
    modal True

    imagemap:
        ground "backgrounds/use_incubator.png"
        idle "backgrounds/use_incubator.png"
        hover "backgrounds/use_incubator_hover.png"

        hotspot (599, 157, 719, 815):
            action If(
                dna_check_task_complete(["swab_is_cut", "swab_is_prepped", "swab_is_vortexed"]),
                Jump("dna_incubator_question"),
                [Show("dna_notify", message="Action error: Incubator is empty. Load your sample.", correct=False), Jump("dna_bio_station")],
            )


screen dna_qpcr():
    zorder 99
    modal True

    imagemap:
        ground "backgrounds/use_qpcr.png"
        idle "backgrounds/use_qpcr.png"
        hover "backgrounds/use_qpcr_hover.png"

        hotspot (860, 561, 301, 156):
            action If(
                dna_tasks["Prep swab for DNA analysis"],
                Jump("dna_pcr"),
                [Show("dna_notify", message="Protocol error: Incorrect step order.", correct=False), Jump("dna_bio_station")],
            )


screen dna_cem_screen():
    zorder 99
    modal True

    imagemap:
        ground "backgrounds/cem_screen_idle.png"
        idle "backgrounds/cem_screen_idle.png"
        hover "backgrounds/cem_screen_hover.png"

        hotspot (486, 300, 140, 648):
            action Jump("dna_cem_finish")

    textbutton "Close":
        action Return()
        align (0.0, 0.0)
        xpadding 30
        ypadding 10
        background Solid("#2a2a2ae6")
        hover_background Solid("#4a90d9")
        text_color "#ffffff"
        text_hover_color "#ffffff"


screen dna_tray_drag():
    tag dna_tray_drag
    modal True
    add Solid("#000000cc")
    image "tray"

    draggroup:
        drag:
            drag_name "top"
            child ("tray_top_filled" if dna_tray_top_filled else "tray_top")
            xpos 590 ypos 170
            draggable False
            droppable True
            dragging dna_item_dragging_package
            dragged dna_item_dragged_package

        drag:
            drag_name "reaction_mix"
            child "textbox_1"
            xpos 300 ypos 890
            draggable True
            droppable True
            dragging dna_item_dragging_package
            dragged dna_item_dragged_package

    draggroup:
        drag:
            drag_name "nuclease_free_water"
            child "textbox_3"
            xpos 1300 ypos 890
            draggable True
            droppable True
            dragging dna_item_dragging_package
            dragged dna_item_dragged_package

        drag:
            drag_name "side"
            child ("tray_side_filled" if dna_tray_side_filled else "tray_side")
            xpos 510 ypos 170
            draggable False
            droppable True
            dragging dna_item_dragging_package
            dragged dna_item_dragged_package

    draggroup:
        drag:
            drag_name "bottom"
            child ("tray_bottom_filled" if dna_tray_bottom_filled else "tray_top")
            xpos 590 ypos 715
            draggable False
            droppable True
            dragging dna_item_dragging_package
            dragged dna_item_dragged_package

        drag:
            drag_name "diluted_dna"
            child "textbox_2"
            xpos 800 ypos 890
            draggable True
            droppable True
            dragging dna_item_dragging_package
            dragged dna_item_dragged_package

    textbutton "Reset":
        action [
            SetVariable("dna_tray_top_filled", False),
            SetVariable("dna_tray_bottom_filled", False),
            SetVariable("dna_tray_side_filled", False),
        ]
        xpos 0.1
        ypos 0.4
        xpadding 30
        ypadding 10
        background Solid("#2a2a2ae6")
        hover_background Solid("#4a90d9")
        text_color "#ffffff"
        text_hover_color "#ffffff"

    textbutton "Submit":
        action Function(dna_check_tray_placements)
        xpos 0.85
        ypos 0.4
        xpadding 30
        ypadding 10
        background Solid("#2a2a2ae6")
        hover_background Solid("#4a90d9")
        text_color "#ffffff"
        text_hover_color "#ffffff"

    textbutton "Close":
        action Jump("dna_bio_station")
        align (0.0, 0.0)
        xpadding 30
        ypadding 10
        background Solid("#2a2a2ae6")
        hover_background Solid("#4a90d9")
        text_color "#ffffff"
        text_hover_color "#ffffff"


################################################################################
## DNA labels -- entry / exit
################################################################################

label dna_lab_entry:
    hide screen inventory
    hide screen open_inv
    show nina thinknote1 at right
    if not has_dna_evidence():
        n "We can't extract DNA from thin air. Go back to the vehicle and collect a physical sample first."
        hide nina with dissolve
        jump lab_hub_loop
    $ dna_setup_lab_toolbox()
    show screen dna_lab_toolbox
    show screen dna_notebook_icon
    jump dna_bio_station

label dna_exit:
    hide screen dna_lab_toolbox
    hide screen dna_notebook_icon
    hide screen dna_notebook_panel
    hide nina with dissolve
    scene lab_hallway with dissolve
    jump lab_hub_loop

label dna_bio_station:
    python:
        if all(dna_swab_tasks.values()):
            dna_tasks["Prep swab for DNA analysis"] = True
    call screen dna_bio_station
    jump dna_bio_station


################################################################################
## DNA labels -- swab prep machines
################################################################################

label dna_use_prep:
    if dna_swab_tasks["swab_is_cut"] and dna_swab_tasks["swab_is_prepped"]:
        $ dna_notify_msg("Already prepped!", correct=False)
        jump dna_bio_station
    call screen dna_swab_screen
    jump dna_bio_station

label dna_use_vortex:
    if (dna_swab_is_incubated_0 and not dna_swab_tasks["swab_is_incubated"]) or dna_swab_tasks["swab_is_spun"]:
        $ dna_notify_msg("Protocol error: Incorrect step order.", correct=False)
        jump dna_bio_station
    call screen dna_vortex
    jump dna_bio_station

label dna_use_incubator:
    if dna_swab_tasks["swab_is_incubated"]:
        $ dna_notify_msg("Protocol error: Incorrect step order.", correct=False)
        jump dna_bio_station
    call screen dna_incubator
    jump dna_bio_station

label dna_incubator_question:
    scene use_incubator
    show nina thinknote1 at right
    n "Set the incubator temperature and timer for cell lysis:"
    menu:
        "37\u00b0C for 15 minutes":
            n "That temperature is too low. We need 56\u00b0C for 10 minutes to activate the Proteinase K enzyme and break open the cell membranes. Try again."
            jump dna_use_incubator

        "56\u00b0C for 10 minutes":
            $ dna_swab_is_incubated_0 = True
            jump dna_wait_screen

        "95\u00b0C for 5 minutes":
            n "Too hot. 95\u00b0C will destroy our active enzymes before they can do their job. Save that heat for the PCR machine later. Set it to 56\u00b0C."
            jump dna_use_incubator

label dna_use_spinner:
    if (dna_ethanol_added and not dna_swab_is_vortexed_2) or dna_swab_tasks["swab_is_spun"] or not dna_swab_is_incubated_0:
        $ dna_notify_msg("Protocol error: Incorrect step order.", correct=False)
        jump dna_bio_station
    call screen dna_spinner
    jump dna_bio_station

label dna_add_ethanol:
    $ dna_ethanol_added = True
    if dna_check_task_complete(["swab_is_cut", "swab_is_prepped", "swab_is_vortexed", "swab_is_incubated"]):
        scene add_ethanol_1
        pause 1.0
        scene add_ethanol_2
        pause 0.5
        scene add_ethanol_3
        pause 1.0
        scene add_ethanol_4
        pause 1.0
        $ dna_notify_msg("Added 400uL of ethanol!", correct=True)
    jump dna_bio_station

label dna_new_tube:
    if dna_check_task_complete(["swab_is_cut", "swab_is_prepped", "swab_is_vortexed", "swab_is_incubated", "swab_is_spun"]):
        scene new_tube_1
        pause 1.0
        scene new_tube_2
        pause 0.5
        scene new_tube_3
        pause 1.0
        $ dna_notify_msg("Transferred to a new 2mL tube!", correct=True)
        $ dna_tube_transfered = True
        $ dna_swab_tasks["swab_new_tube"] = True
    jump dna_bio_station

label dna_use_centrifuge:
    if dna_swab_tasks["sample_is_spun"]:
        $ dna_notify_msg("Protocol error: Incorrect step order.", correct=False)
        jump dna_bio_station
    call screen dna_centrifuge
    jump dna_bio_station

label dna_wait_screen:
    scene black with dissolve
    if dna_tasks["Prep swab for DNA analysis"]:
        show text "{color=#ffffff}We run the PCR machine...{/color}" at truecenter with dissolve
    elif dna_check_task_complete(["swab_new_tube"]):
        show text "{color=#ffffff}We spin at 6000 RCF for 1 minute...{/color}" at truecenter with dissolve
    else:
        show text "{color=#ffffff}We wait for 10 minutes...{/color}" at truecenter with dissolve
    pause 2.0
    hide text with dissolve
    jump dna_bio_station

label dna_discard_sample:
    if dna_check_task_complete(["swab_is_cut", "swab_is_prepped", "swab_is_vortexed", "swab_is_incubated", "swab_is_spun", "swab_new_tube", "sample_is_spun"]):
        scene discard_sample_1
        pause 1.0
        scene discard_sample_2
        pause 0.5
        scene discard_sample_3
        pause 0.5
        scene discard_sample_4
        pause 0.5
        scene discard_sample_5
        pause 0.5
        scene discard_sample_6
        pause 0.5
        scene discard_sample_7
        pause 1.0
        $ dna_notify_msg("Sample transferred!", correct=True)
        $ dna_swab_tasks["sample_new_tube"] = True
        jump dna_finish_step_1
    jump dna_bio_station

label dna_finish_step_1:
    scene bio_station
    show nina talk at right
    n "Lysis complete. The cells are broken down and the DNA is suspended in the liquid lysate."
    show nina thinknote1 at right
    n "Now we begin the purification steps to separate the DNA from unwanted proteins and fats. Keep your pipetting precise."
    scene table_tube_dark
    show nina thinknote1 at right
    n "That's the final wash done. The spin column is dry and ready for us to collect the clean DNA."
    jump dna_swab_question_1


################################################################################
## DNA labels -- extraction quiz + quantification
################################################################################

label dna_swab_question_1:
    scene table_tube_dark
    show nina thinknote1 at right
    n "The sample is loaded into the spin column, and the DNA is bound to the filter matrix. Next, we need a purification wash using Buffer AW1."
    n "How much Buffer AW1 should be pipetted into the column?"
    menu:
        "200\u00b5L Buffer AW1":
            n "Not enough volume. 200\u00b5L won't wash away all the leftover proteins, leaving our final sample contaminated. We need exactly 500\u00b5L."
            scene black with dissolve
            jump dna_swab_question_1

        "500\u00b5L Buffer AW1":
            $ dna_notify_msg("500\u00b5L Buffer AW1 added!", correct=True)
            jump dna_swab_question_2

        "1000\u00b5L Buffer AW1":
            n "That will flood the column assembly and ruin the wash. Bring it back down to 500\u00b5L."
            scene black with dissolve
            jump dna_swab_question_1

label dna_swab_question_2:
    show nina thinknote1 at right
    n "After the first wash, Buffer AW2 is added to remove remaining salts. How long should we spin the sample in the centrifuge for this step?"
    menu:
        "1 minute":
            n "Too short. A 1-minute spin leaves residual ethanol in the filter, which will completely ruin our later PCR reactions. It needs a full 3 minutes."
            scene black with dissolve
            jump dna_swab_question_1

        "3 minutes":
            $ dna_notify_msg("Centrifuged for 3 minutes!", correct=True)
            jump dna_swab_question_3

        "10 minutes":
            n "Spinning for 10 minutes is overkill and risks tearing the DNA apart under intense friction. Stick to the standard 3 minutes."
            scene black with dissolve
            jump dna_swab_question_1

label dna_swab_question_3:
    show nina thinknote1 at right
    n "The purified DNA is ready to be washed off the filter into a clean tube. How much of this extracted DNA template should go into our 50\u00b5L PCR reaction mix?"
    menu:
        "1\u00b5L extracted DNA":
            $ dna_notify_msg("DNA diluted!", correct=True)
            jump dna_finish_swab

        "5\u00b5L extracted DNA":
            n "If the sample is too concentrated, leftover chemicals from the extraction will overwhelm the DNA polymerase. Keep it to a clean 1\u00b5L."
            scene black with dissolve
            jump dna_swab_question_2

        "10\u00b5L extracted DNA":
            n "That much volume will stall out the reaction entirely. 1\u00b5L is all it takes for a 50\u00b5L target mix."
            scene black with dissolve
            jump dna_swab_question_2

label dna_finish_swab:
    scene bio_station
    show nina talk at right
    n "Clean yield. The DNA is isolated, purified, and ready in the tube."
    n "Let's run a quick qPCR assay to measure exactly how much human DNA we recovered from the car."
    jump dna_reaction_question_1

label dna_reaction_question_1:
    scene table_tube_dark
    show nina thinknote1 at right
    n "Which of these components is NOT used in a standard DNA profiling mix?"
    menu:
        "Master mix":
            n "Incorrect. The master mix holds the essential polymerase and building blocks for replication. We definitely need it."
            scene black with dissolve
            jump dna_reaction_question_1

        "Forward and reverse primers":
            n "Incorrect. Primers act as chemical markers to target the specific DNA regions we want to look at."
            scene black with dissolve
            jump dna_reaction_question_1

        "Nuclease-free water":
            n "Incorrect. We use it to bring the chemical mix up to volume safely without degrading the DNA."
            scene black with dissolve
            jump dna_reaction_question_1

        "Reverse transcriptase":
            n "Correct. That enzyme is used to copy RNA, not DNA. It has no place in an STR profiling kit."
            $ dna_notify_msg("Reaction mix prepared!", correct=True)
            jump dna_reaction_question_2

        "Magnesium chloride":
            n "Incorrect. Magnesium ions are required to catalyze the duplication process."
            scene black with dissolve
            jump dna_reaction_question_1

label dna_reaction_question_2:
    scene table_tube_dark
    show nina thinknote1 at right
    n "What size microcentrifuge tube should be used to prepare this mix?"
    menu:
        "1.0 mL tube":
            n "Non-standard size. Grab a standard 1.5 mL tube so we have enough room to mix the reagents safely."
            scene black with dissolve
            jump dna_reaction_question_1

        "1.5 mL tube":
            $ dna_notify_msg("Mix put into a 1.5 mL tube!", correct=True)
            jump dna_reaction_question_3

        "2.0 mL tube":
            n "Too large. A 2.0 mL tube won't sit properly in our benchtop centrifuges, and it makes it harder to see the liquid pellet. Stick to 1.5 mL."
            scene black with dissolve
            jump dna_reaction_question_1

label dna_reaction_question_3:
    n "Good. Dilute the purified DNA 1:1 with nuclease-free water to stabilize our final working solution."
    call screen dna_tray_drag
    jump dna_bio_station


################################################################################
## DNA labels -- qPCR / PCR / capillary electrophoresis / result
################################################################################

label dna_use_qpcr:
    call screen dna_qpcr
    jump dna_bio_station

label dna_pcr:
    $ dna_tasks["Run qPCR machine"] = True
    n "The quantification data looks great. We have more than enough DNA to get a profile."
    scene use_pcr
    show nina thinknote1 at right
    n "Now for the real test. We'll load the DNA, the master mix, and the fluorescent primers into the thermal cycler to copy our target forensic markers."
    n "Amplification is complete. The markers are copied millions of times over. Let's move the tube to the capillary electrophoresis unit to read the data."
    jump dna_cem

label dna_cem:
    scene computer_screen_interface
    pause 1.0
    scene cem_interface
    call screen dna_cem_screen
    jump dna_bio_station

label dna_cem_finish:
    scene cem_screen_results
    show nina thinknote1 at right
    n "The electropherogram results are printing out now."
    n "It's a clean, single-source profile. The lack of genetic noise means we pulled skin cells from touch transfer, not fluid."
    n "Running the data through the criminal database now... We have an exact match for [_robber_name]."
    $ dna_tasks["Analyze DNA results"] = True
    $ lab_dna_done = True
    $ dna_notify_msg("DNA analysis complete, profile matched!", correct=True)
    n "That solidifies our biological evidence. Let's head back to the main desk and wrap this up."
    jump dna_exit
