# Mistake tracking for The Studio, based on the mistake system from the Crime
# Scene Investigation level (Forensics-Pursuit/Game/ROP 2026/Sana).
#
# How it works:
#     - jsons/mistakes.json lists every mistake the player can make. Each one is a
#       normal inventory Item (name, image_name, description).
#     - During gameplay, call add_mistake("<name>", spot="<spot id>", where="<detail>")
#       when the player does something wrong.
#         - spot: which thumbnail on the Mistakes clipboard it belongs to (an "id"
#           from jsons/results.json, e.g. "canvas" or "knife").
#         - where: optional extra detail shown next to the mistake name, for spots
#           with more than one item (e.g. "Knife fingerprint 1").
#       The same mistake in the same place is only recorded once.
#     - When the player finishes the level or presses the Quit button, the game
#       jumps to label review_mistakes, which adds end-of-level mistakes (missing
#       evidence, etc.) and shows the results screens from results.rpy.

image mistake-laptop = Transform("images/objects/laptop.png", xysize=(200, 200), fit="contain")

# Holds the mistakes the player has made this playthrough. Using "default"
# means it starts empty for every new game and is included in save files.
default mistake_inventory = Inventory()

# True while the player is holding a swab they already ran a presumptive test on.
default tested_swab = False


init python:
    # Every gameplay screen that should be cleared away before the results.
    # (Hiding a screen that isn't showing does nothing, so it's safe to list them all.)
    GAMEPLAY_SCREENS = [
        "crimescene", "notebook", "notebook_screen", "progress_counter", "ui",
        "casefile", "casefile_physical", "casefile_photos", "back_button",
        "toolbox_print", "toolbox_blood", "toolbox_presumptive", "toolbox_packaging",
        "sample_to_tube", "tube_to_bag", "fingerprint_to_bag", "tape_to_bag",
        "folder_to_bag", "letters_to_bag", "bloody_swab", "dark_overlay_with_mouse",
        "inspect_laptop", "inspect_drawer", "inspect_folder", "show_document",
        "notify", "quit_button",
    ]

    # add_mistake() lives in results.rpy (shared with other levels).

    def current_sample():
        """(spot, where) for the blood sample the player is working on."""
        for key in ("stool", "canvas", "table"):
            if analyzing.get(key):
                return key, None
        if analyzing.get("knife"):
            return "knife", "Knife blood"
        return None, None

    def current_print():
        """(spot, where) for the fingerprint the player is working on."""
        if analyzing.get("knife fingerprint"):
            return "knife", "Knife fingerprint 1"
        elif analyzing.get("knife fingerprint alt"):
            return "knife", "Knife fingerprint 2"
        return "knife", None

    def add_sample_mistake(name):
        spot, where = current_sample()
        add_mistake(name, spot=spot, where=where)

    def add_print_mistake(name):
        spot, where = current_print()
        add_mistake(name, spot=spot, where=where)

    PRESUMPTIVE_KEYS = {
        "stool": "splatter presumptive",
        "canvas": "canvas presumptive",
        "table": "table presumptive",
        "knife": "knife presumptive",
    }

    def check_presumptive_done():
        """Called when a blood sample is about to be packaged. Records a mistake if
        the player skipped the presumptive (Kastle-Meyer) test for it.
        """
        for key, analyzed_key in PRESUMPTIVE_KEYS.items():
            if analyzing.get(key):
                if not analyzed.get(analyzed_key):
                    add_sample_mistake("No Presumptive Test")
                return

    def check_kastle_meyer_order():
        """Called after each drop in the presumptive test. Records a mistake as soon
        as the drops can no longer turn into a valid Kastle-Meyer order.
        """
        order = store.player_kastle_meyer_order
        if not any(valid[:len(order)] == order for valid in valid_kastle_meyer_orders):
            add_sample_mistake("Wrong Blood Test Order")

    def add_end_of_level_mistakes():
        """Mistakes that can only be checked once the player is done."""
        add_missing_evidence_mistakes()

        if not tasks["Inspect the computer"]:
            add_mistake("Computer Not Inspected", spot="laptop")


# QUIT BUTTON -----------------------------------------------------------------

screen quit_button():
    # Small red text in the bottom-right corner that ends the investigation early.
    zorder 150

    textbutton "Quit":
        xalign 1.0
        yalign 1.0
        xoffset -10
        yoffset -6
        padding (4, 2, 4, 2)
        background None
        hover_background None
        text_size 22
        text_bold True
        text_color "#d32f2f"
        text_hover_color "#ff6659"
        action Confirm("Are you sure you want to leave and conclude the crime scene investigation?", Jump("review_mistakes"))


# END OF LEVEL ----------------------------------------------------------------

label review_mistakes:
    python:
        hide_all_inventory()
        for screen_name in GAMEPLAY_SCREENS:
            renpy.hide_screen(screen_name)
        default_mouse = "default"
        add_end_of_level_mistakes()

    # Placeholder background until the final end-of-level scene is ready.
    scene black
    show nina normal at right
    s "All finished, investigator?"
    s "Let's see how you did!"

    # Performance Results rubric, then the Mistakes clipboard.
    call show_results

    # Done was pressed: the clipboard is gone, Nina signs off, back to the main menu.
    show nina normal at right
    s "Great work today!"

    # (Level Select test) Save the stars shown on the level selector.
    $ record_level_stars("studio", studio_stars_earned())
    $ MainMenu(confirm=False)()
