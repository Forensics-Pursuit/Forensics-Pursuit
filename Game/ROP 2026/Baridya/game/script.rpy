default default_mouse = "default"

################################################################################
## Custom cursors
################################################################################
## Full set matching the source lab project's own config.mouse. Registers
## a state only if its file actually exists yet, so this can never crash
## at startup regardless of which cursor art has been added so far --
## Ren'Py preloads config.mouse["default"] during its own startup GL test,
## before any of our game code runs, so a missing file there is otherwise
## a hard crash at launch.
init python:
    if config.mouse is None:
        config.mouse = {}

    _cursor_files = {
        "default": ("images/ui/cursors/cursor.png", 0, 0),
        "pointer": ("images/ui/cursors/cursor.png", 0, 0),
        "magnifying": ("images/ui/cursors/default_cursor.png", 0, 0),
        "hover": ("images/ui/cursors/hover_cursor.png", 0, 0),
        "dropper": ("images/ui/cursors/dropper.png", 0, 49),
        "ethanol": ("images/ui/cursors/dropper_filled.png", 0, 49),
        "hand": ("images/ui/cursors/default_hand.png", 0, 0),
        "hand_grab": ("images/ui/cursors/grab_hand.png", 0, 0),
        "micropipette": ("images/ui/cursors/micropipette.png", 10, 10),
    }
    for _cursor_name, (_cursor_path, _hot_x, _hot_y) in _cursor_files.items():
        if renpy.loadable(_cursor_path):
            config.mouse[_cursor_name] = [(_cursor_path, _hot_x, _hot_y)]


define n = Character(name=("Nina"), image="nina")


init python:
    ## Starting field toolbox. use_gloves comes from gloves.rpy (init -1),
    ## so it already exists when the Gloves action is set below.
    tools = load_items("jsons/toolbox.json")
    toolbox.add_to_inventory(tools["Evidence Bag"])
    toolbox.add_to_inventory(tools["Tamper Evident Tape"])
    toolbox.add_to_inventory(tools["Tube"])
    toolbox.add_to_inventory(tools["Swab Pack"])
    toolbox.add_to_inventory(tools["Backing Card"])
    toolbox.add_to_inventory(tools["Magnetic Powder"])
    toolbox.add_to_inventory(tools["Tape"])
    toolbox.add_to_inventory(tools["Scalebar"])
    if "Gloves" in tools:
        toolbox.add_to_inventory(tools["Gloves"])
        ## Force these directly rather than trusting the JSON's "usable"/
        ## "action" fields resolved correctly -- guarantees this works
        ## regardless of what's actually in toolbox.json right now.
        tools["Gloves"].usable = True
        tools["Gloves"].action = use_gloves


label start:
    $ evidence.reset_inventory()
    $ fingerprint_process.reset()
    $ can_print_process.reset()
    $ can_dna_process.reset()
    $ can_whole_process.reset()
    $ wheel_print_process.reset()
    $ wheel_dna_process.reset()
    $ active_process = None
    $ did_can = False
    $ can_done = False
    $ wheel_done = False
    $ visited_can = False
    $ visited_wheel = False
    $ visited_interior = False
    scene bg_dispatch with fade
    show nina normal1 at center with moveinright
    n "We have a critical situation. Dispatch logged a forced carjacking; the vehicle owner was hospitalized with severe injuries, and the perpetrator fled the scene."
    show nina talk
    n "The vehicle was located abandoned in a commercial parking lot."
    show nina thinknote1
    n "The MO aligns closely with an active serial carjacking investigation targeting high-end vehicles."
    n "We need to process this scene immediately to establish if the perpetrator is indeed our primary suspect, known as the \"Pontiac Bandit.\""
    hide nina with dissolve
    jump scene_parking
