# Level-specific inventory code for The Studio.
#
# The generic inventory system (Item / Inventory classes, the inventory screens and
# load_items) lives in inventory.rpy and should be kept identical to the shared
# template so future updates can be dropped in. Everything specific to this level
# goes here instead:
#
#     - The action functions that tools run when the player clicks "Use". These are
#       linked to items through the "action" field in jsons/toolbox.json.
#     - Helpers for adding/removing tools and evidence by name.
#     - Helpers for showing/hiding the inventory during gameplay.
#     - Loading the items from jsons/toolbox.json and jsons/evidence.json.

# Evidence images that don't have dedicated inventory art, scaled to inventory size.
image inventory-folder = Transform("images/folder.png", xysize=(200, 200), fit="contain")
image inventory-letters = Transform("images/objects/letters.png", xysize=(200, 200), fit="contain")


init -5 python:
    # SHOWING / HIDING THE INVENTORY -----------------------------------------

    def show_toolbox():
        """Switches the inventory to the toolbox tab and hides the open button.
        Use right before "call screen inventory" so the open button and the
        inventory panel are never visible at the same time.
        """
        store.selected_inventory = toolbox
        renpy.hide_screen("open_inv")

    def close_inventory():
        """Closes the inventory panel (and any item info pop-up) and leaves the
        open button on screen so the player can reopen it.
        """
        renpy.hide_screen("inventory")
        renpy.hide_screen("inventory_info")
        renpy.show_screen("open_inv")

    def show_inventory_button():
        """Shows the open button unless the inventory panel is already open."""
        if not renpy.get_screen("inventory"):
            renpy.show_screen("open_inv")

    def hide_all_inventory():
        """Hides everything inventory-related, including the open button."""
        renpy.hide_screen("inventory")
        renpy.hide_screen("inventory_info")
        renpy.hide_screen("open_inv")

    # ADDING / REMOVING ITEMS ------------------------------------------------
    # Names are the "name" values in jsons/toolbox.json and jsons/evidence.json.

    def add_tools_to_toolbox(names):
        for name in names:
            item = tool_items[name]
            if item not in toolbox._inventory: # don't add the same tool twice
                toolbox.add_to_inventory(item)

    def remove_tools_from_toolbox(names):
        for name in names:
            if name in tool_items:
                toolbox.delete_from_inventory(tool_items[name])

    def remove_toolbox_items():
        toolbox.reset_inventory()

    def add_to_evidence(names):
        for name in names:
            item = evidence_items[name]
            if item not in evidence._inventory:
                evidence.add_to_inventory(item)

    # TOOL ACTIONS -----------------------------------------------------------

    def jump_if_analyzing(options, label):
        for key in options:
            if analyzing.get(key):
                renpy.jump(label)
                break

    def toolbox_actions(item: str) -> None:
        """Runs the gameplay logic for a tool. The tools dict (script.rpy) decides
        whether a tool does anything at the current step.
        """
        global tools, analyzing, default_mouse

        # --- FINGERPRINT & HANDPRINT TOOLS ---
        if item == "uv_light" and tools["uv light"]:
            tools["uv light"] = False
            hide_all_inventory()
            renpy.show_screen("dark_overlay_with_mouse")

        elif item == "magnetic_powder":
            custom_notify("Wrong type of powder!", False)
            add_print_mistake("Wrong Powder")

        elif item == "silver_granular_powder" and tools["silver granular powder"]:
            tools["silver granular powder"] = False
            tools["scalebar"] = True
            close_inventory()
            renpy.jump("fingerprint_dusted")

        elif item == "scalebar" and tools["scalebar"]:
            tools["scalebar"] = False
            tools["tape"] = True
            close_inventory()
            renpy.jump("fingerprint_scalebar")

        elif item == "tape" and tools["tape"]:
            tools["tape"] = False
            tools["backing"] = True
            close_inventory()
            renpy.jump("fingerprint_taped")

        elif item == "backing_card" and tools["backing"]:
            tools["backing"] = False
            tools["packaging"] = True
            close_inventory()
            renpy.jump("fingerprint_backing")

        # --- BLOOD / SWAB TOOLS ---
        elif item == "swab_pack" and tools["swab"]:
            tools["swab"] = False
            close_inventory()
            if analyzing.get("canvas"):
                renpy.jump("canvas_swab")
            elif analyzing.get("knife"):
                renpy.jump("knife_swab")
            elif analyzing.get("table"):
                renpy.jump("table_swab")
            elif analyzing.get("stool"):
                renpy.jump("stool_swab")

        # --- PRESUMPTIVE TEST DROPPERS ---
        elif item == "ethanol":
            default_mouse = "ethanol"
            close_inventory()

        elif item == "reagent":
            default_mouse = "reagent"
            close_inventory()

        elif item == "hydrogen_peroxide":
            default_mouse = "hydrogen"
            close_inventory()

        # --- PACKAGING TOOLS ---
        elif item == "evidence_bag":
            if tools["packaging"]:
                tools["packaging"] = False
                tools["tamper evident tape"] = True
                tools["bag"] = True
                close_inventory()
                if analyzing.get("folder") or analyzing.get("letters"):
                    renpy.jump("psych_packaging_1")
                else:
                    renpy.jump("packaging_1")
            elif tools["bag"]:
                tools["tube"] = False
                tools["bag"] = False
                tools["tamper evident tape"] = True
                close_inventory()
                if analyzing.get("knife fingerprint") or analyzing.get("knife fingerprint alt"):
                    renpy.jump("packaging_1")
                elif analyzing.get("folder") or analyzing.get("letters"):
                    renpy.jump("psych_packaging_1")
                else:
                    jump_if_analyzing(["stool", "canvas", "knife", "table"], "splatter_packaging_1")

        elif item == "tube" and tools["tube"]:
            tools["tube"] = False
            tools["bag"] = True
            close_inventory()
            jump_if_analyzing(["stool", "canvas", "knife", "table"], "splatter_packaging_0")

        elif item == "tamper_evident_tape" and tools["tamper evident tape"]:
            tools["tamper evident tape"] = False
            close_inventory()
            if analyzing.get("knife fingerprint") or analyzing.get("knife fingerprint alt"):
                renpy.jump("packaging_2")
            elif analyzing.get("folder") or analyzing.get("letters"):
                renpy.jump("psych_packaging_2")
            else:
                jump_if_analyzing(["stool", "canvas", "knife", "table"], "splatter_packaging_2")

        elif item == "gloves":
            tools["gloves"] = True
            renpy.call_in_new_context("_glove_animation")

    # One function per usable tool; these names are referenced by the
    # "action" field in jsons/toolbox.json.
    def use_uv_light(): toolbox_actions("uv_light")
    def use_magnetic_powder(): toolbox_actions("magnetic_powder")
    def use_silver_granular_powder(): toolbox_actions("silver_granular_powder")
    def use_scalebar(): toolbox_actions("scalebar")
    def use_tape(): toolbox_actions("tape")
    def use_backing_card(): toolbox_actions("backing_card")
    def use_swab_pack(): toolbox_actions("swab_pack")
    def use_ethanol(): toolbox_actions("ethanol")
    def use_reagent(): toolbox_actions("reagent")
    def use_hydrogen_peroxide(): toolbox_actions("hydrogen_peroxide")
    def use_evidence_bag(): toolbox_actions("evidence_bag")
    def use_tube(): toolbox_actions("tube")
    def use_tamper_evident_tape(): toolbox_actions("tamper_evident_tape")
    def use_gloves(): toolbox_actions("gloves")


init python:
    # Loaded after the action functions above exist so load_items can link them.
    tool_items = load_items("jsons/toolbox.json")
    evidence_items = load_items("jsons/evidence.json")


# GLOVE ANIMATION ------------------------------------------------------------

transform slide_up:
    # start off-screen below
    xalign 0.5
    yalign 1.8
    zoom 1.0
    linear 0.5 xalign 0.5 yalign 1.1

transform slide_down:
    xalign 0.5
    yalign 1.1
    zoom 1.0
    # slide off-screen below
    linear 1.0 xalign 0.5 yalign 1.8

label _glove_animation:
    show hands at slide_up
    with None
    pause 0.5

    hide hands with None

    show gloved_hands at slide_down
    with None
    pause 0.5

    hide gloved_hands
    return
