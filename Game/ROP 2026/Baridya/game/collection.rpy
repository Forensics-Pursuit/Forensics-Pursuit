init python:
    def item_dragged_package(drags, drop):
        global default_mouse
        default_mouse = "hand_grab"

        if not drop:
            default_mouse = "hand"
            return

        store.dragged = drags[0].drag_name
        store.dropped = drop.drag_name
        default_mouse = "default"

        if store.dropped != "bag" and store.dragged != "bag":
            return True

        if renpy.get_screen("drag_to_bag"):
            renpy.hide_screen("drag_to_bag")
            renpy.hide_screen("inventory")
            if store.active_process is not None:
                store.active_process.advance()
                renpy.notify("Now seal the bag with tape.")
                renpy.invoke_in_new_context(renpy.call_screen, "drag_tape_to_bag")

        elif renpy.get_screen("drag_tape_to_bag"):
            renpy.hide_screen("drag_tape_to_bag")
            if store.active_process is not None:
                store.active_process.advance()  # triggers on_complete internally

        return True


label scene_parking:
    scene bg_parking_lot with fade
    show nina talk
    show nina thinknote1 at right
    n "Click the licence plate on the vehicle to run the plates first."
    hide nina with dissolve
    call screen parking_screen

screen parking_screen():
    imagemap:
        ground "images/backgrounds/bg_parking_lot.png"
        hover  "images/backgrounds/bg_parking_lot_hover.png"
        hotspot (620, 670, 90, 60) action Jump("ran_plates")

label ran_plates:
    show nina talk at right
    n "Plate verified. This is the victim's vehicle."
    n "This vehicle is now an active crime scene tied to a violent felony. Secure the perimeter and proceed with methodical documentation."
    $ gloves_worn = False
    jump glove_gate_field

label glove_gate_field:
    if gloves_worn or not has_gloves_item():
        jump scence_exterior
    $ _glove_return_label = "glove_gate_field"
    $ _gloves_item = get_toolbox_item("Gloves")
    if _gloves_item:
        $ _gloves_item.usable = True
    n "Let's get gloved up before we touch anything at this scene."
    call screen inventory
    jump glove_gate_field

label scence_exterior:
    scene bg_car_exterior with fade
    show screen field_notebook_icon
    show nina normal1 at right with moveinright
    n "Visual inspection of the exterior indicates the driver-side door handle remains untouched by emergency responders."
    n "This is a primary contact point for the suspect. We will attempt a latent print lift here. Click the door handle to isolate the area."
    hide nina with dissolve
    call screen car_exterior_screen


screen car_exterior_screen():
    imagemap:
        ground "images/backgrounds/bg_car_exterior.png"
        hover  "images/backgrounds/bg_car_exterior_hover.png"
        hotspot (1100, 660, 450, 150) action Jump("hotspot_door_handle")


label magnetic_powder_quiz:
    ## Run via renpy.call_in_new_context() from use_tool() in
    ## inventory_functions.rpy -- that's what lets a menu/dialogue pop up
    ## safely from inside a toolbox item's click action, without clashing
    ## with the inventory screen's already-running interaction. Returns
    ## True/False for whether the right answer was picked; use_tool()
    ## handles actually advancing the process based on that.
    ##
    ## Re-showing evidence_closeup_view here is deliberate: nested contexts
    ## via call_in_new_context don't reliably inherit persistent screens
    ## shown in the parent, which is why the background was flashing back
    ## to the real scene during this quiz before.
    ##
    ## show/hide nina here fixes a separate issue: Nina gets explicitly
    ## hidden right before the inventory loop starts, so without this,
    ## there's no character sprite currently shown for the dialogue box's
    ## side portrait to source from during this quiz.
    show screen evidence_closeup_view
    show nina talk
    n "What color powder should we use here?"
    menu:
        "White powder":
            n "White powder against a dark surface, that'll show up clearly."
            hide nina
            return True

        "Black powder":
            n "Black powder won't show up well against this surface. Let's try again."
            hide nina
            return False


label hotspot_door_handle:
    show nina talk at right
    if fingerprint_process.step_index == 0:
        call flash_camera
        n "Photo taken of the door handle."
        n "Access your field kit to begin processing the latent friction ridges on the surface."
    $ active_process = fingerprint_process
    show screen evidence_closeup_view
    hide nina with dissolve
    call screen inventory
    if fingerprint_process.complete:
        hide screen evidence_closeup_view
        jump fingerprint_complete
    jump hotspot_door_handle


label fingerprint_complete:
    show nina thinknote1 at right
    n "The latent print is successfully lifted, mounted on a backing card, and sealed."
    n "Let's take a look at the interior now."
    jump scene_interior

label scene_interior:
    if did_can:
        scene bg_car_interior_no_soda with fade
    else:
        scene bg_car_interior with fade
    if not visited_interior:
        $ visited_interior = True
        show nina normal1 at right with moveinright
        n "The interior environment is preserved. We need to locate and isolate high-contact surfaces where biological or friction ridge evidence could transfer."
        n "Methodically scan the cabin. Photograph all evidence in situ before executing collection protocols."
        n "Click on any evidence to take a photo and examine it."
    call screen car_interior_screen

label hotspot_soda_can:
    show nina talk at right
    if not visited_can:
        $ visited_can = True
        call flash_camera
        n "Photo taken of the soda can."
        n "This object represents a dual-matrix evidence source: latent prints on the body and potential salivary DNA on the rim."

label can_menu:
    menu:
        "Select the forensic processing protocol you want for the beverage container:"

        "Dust for fingerprints" if not can_print_process.complete and not can_whole_process.complete:
            $ active_process = can_print_process
            show screen evidence_closeup_view
            call screen inventory
            if can_print_process.complete:
                hide screen evidence_closeup_view
            jump can_menu

        "Swab for DNA" if not can_dna_process.complete and not can_whole_process.complete:
            $ active_process = can_dna_process
            show screen evidence_closeup_view
            call screen inventory
            if can_dna_process.complete:
                hide screen evidence_closeup_view
            jump can_menu

        "Collect the whole can" if not can_whole_process.complete:
            $ active_process = can_whole_process
            call screen inventory
            jump can_menu

        "Move on" if (can_print_process.complete or can_dna_process.complete or can_whole_process.complete):
            $ can_done = True
            if can_done and wheel_done:
                jump scene_wrap_up
            jump scene_interior

label hotspot_steering_wheel:
    show nina talk at right
    if not visited_wheel:
        $ visited_wheel = True
        call flash_camera
        n "Photo taken of the steering wheel. Plenty of trace evidence here."
        n "The steering wheel substrate is highly conducive to trapping epithelial cells via friction, though it often yields complex, overlapping mixtures."

label wheel_menu:
    menu:
        "Select the appropriate forensic processing protocol for the steering wheel:"

        "Dust for fingerprints" if not wheel_print_process.complete:
            $ active_process = wheel_print_process
            show screen evidence_closeup_view
            call screen inventory
            if wheel_print_process.complete:
                hide screen evidence_closeup_view
            jump wheel_menu

        "Swab for DNA" if not wheel_dna_process.complete:
            $ active_process = wheel_dna_process
            show screen evidence_closeup_view
            call screen inventory
            if wheel_dna_process.complete:
                hide screen evidence_closeup_view
            jump wheel_menu

        "Move on" if (wheel_print_process.complete or wheel_dna_process.complete):
            $ wheel_done = True
            if can_done and wheel_done:
                jump scene_wrap_up
            jump scene_interior

screen car_interior_screen():
    imagemap:
        ground ("images/backgrounds/bg_car_interior_no_soda.png" if did_can else "images/backgrounds/bg_car_interior.png")
        hover  ("images/backgrounds/bg_car_interior_hover_wheel_no_soda.png" if did_can else "images/backgrounds/bg_car_interior_hover_wheel.png")
        hotspot (20, 180, 610, 670) action Jump("hotspot_steering_wheel") sensitive (not wheel_done)

    imagemap:
        ground Null()
        hover  "images/backgrounds/bg_car_interior_hover_can.png"
        hotspot (1070, 795, 100, 180) action Jump("hotspot_soda_can") sensitive (not can_done)

label scene_wrap_up:
    scene bg_parking_lot with fade
    hide screen field_notebook_icon
    hide screen field_notebook_panel
    show nina normal1 at right with dissolve
    n "Let us review the field documentation and collection sequence before transport:"
    show nina thinknote1 at right
    n "Scene Documentation: Photographic evidence of each item was captured in situ with an appropriate scale bar prior to handling."
    n "Latent Fingerprints: Developed using physical developer, documented with a scale bar, lifted with tape, and secured on a high-contrast backing card."
    n "Biological Materials: Swabbed high-contact areas, focusing on the can rim for salivary epithelial cells to generate an STR profile."
    n "Chain of Custody: Chronological tracking log has been signed, ensuring a continuous, unbroken chain. The integrity of the physical evidence is intact."
    show nina normal1 at right
    n "These are the core steps of physical evidence collection from a vehicle scene."
    n "Transport all sealed packets to the lab for diagnostic analysis."
    hide nina with dissolve
    jump scene_lab


screen drag_to_bag(item_image, item_drag_name):
    modal True
    add Solid("#0008")
    
    draggroup:
        drag:
            drag_name item_drag_name
            child item_image
            xpos 0.25 ypos 0.3
            draggable True
            droppable True
            dragged item_dragged_package

        drag:
            drag_name "bag"
            child "evidence bag large"
            xpos 0.55 ypos 0.25
            draggable True
            droppable True
            dragged item_dragged_package

screen drag_tape_to_bag():
    modal True
    add Solid("#0008")

    draggroup:
        drag:
            drag_name "tape"
            child "tamper evident tape"
            xpos 0.25 ypos 0.3
            draggable True
            droppable True
            dragged item_dragged_package

        drag:
            drag_name "bag"
            child "evidence bag large"
            xpos 0.55 ypos 0.25
            draggable True
            droppable True
            dragged item_dragged_package

## Camera flash effect #########################################################
## A quick white flash + shutter sound, used to indicate a photo was taken.

transform camera_flash_transform:
    alpha 0.0
    linear 0.05 alpha 1.0
    linear 0.25 alpha 0.0

screen camera_flash():
    zorder 300
    add Solid("#fff") at camera_flash_transform

label flash_camera:
    show screen camera_flash
    play sound "audio/camera_shutter.ogg"
    pause 0.6
    hide screen camera_flash
    return


screen evidence_closeup_view():
    ## A real full-screen close-up, shown/hidden explicitly at specific
    ## story points (see hotspot_door_handle, can_menu, wheel_menu) rather
    ## than tied to a one-shot scene statement. Being a screen means it's
    ## reactive -- it automatically redraws with whatever
    ## active_process.current_image() returns right now, every single time
    ## anything changes, so it just naturally holds steady through all 6
    ## steps with zero extra sync calls needed anywhere.
    ## acts as a background, so it needs to render BEHIND the inventory
    ## panel, dialogue box, and everything else -- not on top of them.
    zorder -10
    if active_process:
        $ _img = active_process.current_image()
        if _img and renpy.image_exists(_img):
            add _img:
                xalign 0.5
                yalign 0.5
                xsize 1920
                ysize 1080
                fit "cover"


################################################################################
## Field notebook -- same idea as the DNA lab one, for the evidence
## collection phase (door handle / can / wheel).
################################################################################

init python:
    field_notebook_clicked = False

    def field_toggle_notebook():
        global field_notebook_clicked
        field_notebook_clicked = True
        dna_toggle_screen("field_notebook_panel")

screen field_notebook_icon():
    zorder 110
    imagebutton:
        idle (Animation("images/ui/notebook_icon.png", 0.5, "images/ui/notebook_icon_hover.png", 0.5) if not field_notebook_clicked else "images/ui/notebook_icon.png")
        hover "images/ui/notebook_icon_hover.png"
        xpos 1830 ypos 20
        at Transform(zoom=0.15)
        action Function(field_toggle_notebook)

screen field_notebook_panel():
    zorder 100
    add "images/ui/field_notebook.png":
        xalign 0.92
        yalign 0.02
