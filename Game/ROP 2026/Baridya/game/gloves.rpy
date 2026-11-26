init -1 python:
    ################################################################################
    ## Gloves
    ################################################################################
    ## Adapted from the source project's _glove_animation (bare hands rise,
    ## swap to gloved hands, slide back down) -- but triggered by clicking
    ## the hands directly instead of the source's drag-a-box-onto-hands
    ## system, which we don't have. Worn twice per playthrough: once before
    ## the door handle, once before anything in the lab -- gloves_worn gets
    ## reset to False at the start of each of those two gates, so both
    ## require a fresh glove-up.
    ##
    ## Runs at init -1 so use_gloves exists before script.rpy's
    ## init python fills the toolbox and assigns the Gloves action.

    gloves_worn = False
    _glove_return_label = None

    def get_toolbox_item(name):
        for item in toolbox._inventory:
            if item.name == name:
                return item
        return None

    def use_gloves():
        """The Gloves toolbox item's action. Safe to call from inside the
        inventory screen's own interaction -- see the magnetic powder quiz
        for why call_in_new_context is required here."""
        global gloves_worn
        if renpy.call_in_new_context("glove_up_sequence"):
            gloves_worn = True
            renpy.hide_screen("inventory")
            renpy.notify("Gloves on.")
            ## Disable so it can't be clicked again until the next gate
            ## explicitly re-enables it -- otherwise it stays clickable
            ## through the rest of evidence collection, which is what was
            ## causing the repeated glove-up bugs.
            _gloves_item = get_toolbox_item("Gloves")
            if _gloves_item:
                _gloves_item.usable = False
            if _glove_return_label:
                renpy.jump(_glove_return_label)

    def has_gloves_item():
        """False until 'Gloves' is actually added to toolbox.json -- lets
        the two gates below skip themselves gracefully instead of soft-
        locking on an item that can't exist yet."""
        return any(item.name == "Gloves" for item in toolbox._inventory)


transform glove_rise:
    xalign 0.5
    yanchor 1.0
    ypos 1.3
    linear 0.6 ypos 1.0

transform glove_settle:
    xalign 0.5
    yanchor 1.0
    ypos 1.0
    linear 0.4 ypos 1.3

screen glove_click_prompt():
    modal True
    add Solid("#000000aa")
    imagebutton:
        idle "hands"
        hover "hands"
        at glove_rise
        action Return()

label glove_up_sequence:
    show nina talk
    n "Click your hands to put your gloves on."
    call screen glove_click_prompt
    show gloved_hands at glove_rise
    pause 0.8
    show gloved_hands at glove_settle
    pause 0.4
    hide gloved_hands
    hide nina with dissolve
    return True
