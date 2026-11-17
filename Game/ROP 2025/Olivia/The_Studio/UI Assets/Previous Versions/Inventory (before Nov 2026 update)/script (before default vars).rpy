define s = Character(name=("Nina"), image="nina")
default notebook_clicked = False

init python:
    tasks = {
        "Analyze the canvas": False,
        "Analyze the splatter by the stool": False,
        "Analyze the blood on the knife": False,
        "Analyze the fingerprints (2) on the knife": False,
        "Analyze the table": False,
        "Inspect the computer": False,
        "Package the folder": False,
        "Package the letters": False
    }

    # Defines all mouse cursors used in the game
    config.mouse = {
        "default": [("images/ui/cursors/cursor.png", 0, 0)],
        "pointer": [("images/ui/cursors/cursor.png", 0, 0)],
        "magnifying": [("images/ui/cursors/default_cursor.png", 0, 0)],
        "hover": [("images/ui/cursors/hover_cursor.png", 0, 0)],
        "dropper": [("images/ui/cursors/dropper.png", 0, 49)],
        "ethanol": [("images/ui/cursors/dropper_filled.png", 0, 49)],
        "reagent": [("images/ui/cursors/dropper_filled.png", 0, 49)],
        "hydrogen": [("images/ui/cursors/dropper_filled.png", 0, 49)],
        "hand": [("images/ui/cursors/default_hand.png", 0, 0)],
        "hand_grab": [("images/ui/cursors/grab_hand.png", 0, 0)]
    }
    
    # Used for tool sensitivity in the toolbox screens defined in custom_screens.rpy
    tools = {
        "uv light": False,
        "magnetic powder": False,
        "silver granular powder": False,
        "scalebar": False,
        "gel lifter": False,
        "tape": False,
        "backing": False,
        "packaging": False,
        "tube": False,
        "bag": False,
        "tamper evident tape": False,
        "swab": True,
        "folder": True,
        "letters": True,
        "gloves": False,
    }

    # Used to keep track of player's progress in the game
    analyzing = {
        "knife": False,
        "knife fingerprint": False,
        "knife fingerprint alt": False,
        "canvas": False,
        "stool": False,
        "table": False,
        "folder": False,
        "letters": False,
    }

    # Used to keep track of what evidence has been analyzed
    analyzed = {
        "canvas presumptive": False,
        "splatter presumptive": False,
        "knife fingerprint": False,
        "knife fingerprint alt": False,
        "knife presumptive": False,
        "table presumptive": False,
        "folder": False,
        "letters": False
    }

    # Used to keep track of what evidence has been encountered
    # This is used to display the evidence markers and enable respective photos
    encountered = {
        "knife": False, 
        "canvas": False,
        "letters": False,
        "stool": False,
        "table": False,
        "laptop": False,
        "drawer": False
    }

    # Used to ensure that the player is not asked the "How would you like to collect the sample?" question multiple times
    asked = {
        "stool_swab": False,
        "canvas_swab": False,
        "table_swab": False,
        "knife_swab": False,
    }

    # Used to compare against the player's Kastle-Meyer order in the presumptive test scene
    valid_kastle_meyer_orders = [
        ["e", "r", "h"],
        ["e", "r", "r", "h"],
        ["e", "r", "h", "h"],
        ["e", "r", "r", "h", "h"],
        ["e", "e", "r", "h"],
        ["e", "e", "r", "r", "h"],
        ["e", "e", "r", "h", "h"],
        ["e", "e", "r", "r", "h", "h"]
    ]

    player_kastle_meyer_order = []

    # Used to display the evidence description in the casefile
    evidence_desc = ""

    def item_dragging_package(drags):
        """Used to set the mouse cursor to the hand_grab cursor when dragging an item.
        """
        global default_mouse
        default_mouse = "hand_grab"
        return

    def item_dragged_package(drags, drop):
        """Used to set the mouse cursor to the hand_grab cursor when grabbing an item.
        """
        global default_mouse
        default_mouse = "hand_grab"
        
        if not drop:
            default_mouse = "hand"
            return

        store.dragged = drags[0].drag_name
        store.dropped = drop.drag_name

        # Hide all draggable screens
        renpy.hide_screen("sample_to_tube")
        renpy.hide_screen("fingerprint_to_bag")
        renpy.hide_screen("tape_to_bag")
        renpy.hide_screen("folder_to_bag")
        renpy.hide_screen("letters_to_bag")
        default_mouse = "default"
        return True
    
    def close_menu():
        """Used to close the casefile menu.
        """
        if renpy.get_screen("casefile_physical"):
            evidence_desc = ""
            renpy.hide_screen("casefile_physical")
        elif renpy.get_screen("casefile_photos"):
            renpy.hide_screen("casefile_photos")
        elif renpy.get_screen("casefile"):
            renpy.hide_screen("casefile")
        else:
            renpy.show_screen("casefile")

    def get_progress():
        remaining = sum(1 for e in tasks.values() if not e)
        return remaining

    def update_progress():
        store.remaining_count = get_progress()
        renpy.hide_screen("progress_counter")
        renpy.show_screen("progress_counter")

    def toggle_screen(name):
        if renpy.get_screen(name):
            renpy.hide_screen(name)
        else:
            renpy.show_screen(name)

    def toggle_notebook():
        toggle_screen("notebook_screen")

    def custom_notify(msg, correct=True):
        renpy.show_screen("notify", message=msg, correct=correct)

label start:
    $ default_mouse = "magnifying"

    $config.rollback_enabled = False # disables rollback
    $quick_menu = False # removes quick menu (at bottom of screen)

    show screen open_inv
    jump begin

label begin:
    scene news
    with Dissolve(2.5)
    scene outside_room
    show nina normal at right
    voice "line1.mp3"
    s "Good evening, investigator."
    show nina talk at right
    voice "line2.mp3"
    s "We received a call earlier regarding the famous painter, {color=#ffff00}Peter Painter{/color}, who was found {color=#ffff00}dead{/color} in his studio apartment."
    show nina write at right
    voice "line3.mp3"
    s "His neighbours claim to have heard a heated argument at around 6pm with a woman, {color=#ffff00}Emily Exgirlfriend{/color}, and went to check up on him later at 10pm, only to find him dead."
    voice "line4.mp3"
    s "There was a {color=#ffff00}knife{/color} found in his chest, and his body appeared to have {color=#ffff00}several cuts on the arms{/color}, he bled quite a bit."
    show nina think at right
    voice "line5.mp3"
    s "We’re not sure of the motive behind this death, so we need you to be thorough. I’ll give you a fair warning, investigator, there is quite a bit of blood on this scene."
    show nina normal at right
    voice "line6.mp3"
    s "You may enter whenever you’re ready."

    call screen outside_room

label crimescene:
    scene room
    if all(tasks.values()):
        jump finish_investigation
    $ default_mouse = "magnifying"
    $ show_inventory_button()
    $ remaining_count = get_progress()
    show screen progress_counter
    show screen notebook
    show screen quit_button
    call screen crimescene
    $ remove_toolbox_items()

label go_to_scene():
    play music "background_music.mp3" volume 0.8
    jump crimescene

label finish_investigation:
    $ hide_all_inventory()
    scene room
    show nina talk at right
    s "Good work, investigator!\nYou've collected all the evidence."
    s "Now, let's head to the lab!"
    jump review_mistakes

transform half_size:
    zoom 0.5