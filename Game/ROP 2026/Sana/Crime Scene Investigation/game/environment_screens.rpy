init python: 
    class Scene:
        def __init__(self, name: str, background: str = None, states: dict = {}):
            self.name = name
            self.background = background
            self.states = {"scene_photographed": False}
            self.states.update(states)

        def set_state(self, key, value=True):
            if key not in self.states:
                return

            self.states[key] = value

        def get_state(self, key, default=False):
            return self.states.get(key, default)

    

default scenes = {
    "bedroom_main": 
        Scene(
            "bedroom_main", 
            background="bg bedroom", 
            states={
                "swabbed": False,
                "right_swab": False,
                "presumptive_test_attempt": False,
                "correct_presumptive_test": False,
                "false_positive": False,
                "test_swab_current": False
            }
            ),

    "angel_statues": 
        Scene(
            "angel_statues", 
            background="bg angel_statues", 
            states={ 
                "dusted": False, 
                "right_dust": False,
                "dusted_photographed": False, 
                "scale_bar": False, 
                "scale_bar_photographed": False,
                "lifted": False,
                }
            ),

    "angel_head": 
        Scene(
            "angel_head", 
            background="bg angel_head",
            states={
                "examined": False,
                "enhanced": False,
                "enhanced_photographed": False,
                "swabbed": False
            }
            )
    }

# swabbing and testing are explicit flags because the mouse cursor changes while hovering,
# so it can't tell us whether a swab is equipped. Background in notes.md.
default swabbing = False
default testing = False

# The scene the player is looking at. Saved with the game, so loading returns to the same view.
default current_scene = "bedroom_main"


screen main():
    # Top-level screen: draws the current scene and picks the top-right button. Design notes in notes.md.
    #The nice thing about this single line is that I never need to explicitly show or hid an environment scene again. 
    #All that is required is a change to current_scene!
    use expression current_scene

    vbox:
        at topright

        if testing:
            use presumptive_testing
        elif swabbing:
            use discard_swab_button
        elif current_scene == "bedroom_main":
            use leave_button
        elif current_scene != "bedroom_main":
            use back_button
        

screen bedroom_main():
    imagemap:
        idle scenes["bedroom_main"].background
        hover "bg bedroom_hover"

        hotspot (1080, 241, 79, 78) action SetVariable("current_scene", "angel_statues")
        hotspot (382, 655, 282, 180) action If(swabbing, Function(swab_something), Notify("A dried blood pool"))
        hotspot (1335, 874, 20, 16) action [SetVariable("current_scene", "angel_head"), Function(scenes["angel_head"].set_state, "examined")]

screen angel_statues():
    imagemap:
        idle scenes["angel_statues"].background
        hover "bg bedroom_hover"
    
screen angel_head():
    imagemap:
        idle scenes["angel_head"].background
        hover "bg bedroom_hover"
    

screen back_button():
    imagebutton:
        idle "back_button"
        hover "back_button_hover"
        #Horrendous hardcode for the scene name but we do not have to worry about scalability :)
        action SetVariable("current_scene", "bedroom_main")

screen discard_swab_button():
    imagebutton:
        idle "images/Environment Items/garbage_idle.png"
        hover "images/Environment Items/garbage_hover.png"
        action Confirm("Are you sure you want to throw away the swab you are currently holding?", Function(discard_swab))

screen presumptive_test_button():
    frame:
        textbutton "Test Swab":
            action Confirm("Run presumptive test on this swab?", Function(discard_swab))

screen collect_swab_button():
    frame:
        textbutton "Collect Swab":
            action Confirm("Place swab in collection tube and add to evidence?", Function(discard_swab))


screen leave_button():
    frame:
        textbutton "Leave the Scene?":
            action Confirm("Are you sure you want to leave and conclude the crime scene investigation?", Jump("review_mistakes"))


# The old mistake_screen / restart_game screens were replaced by the results
# screens in results.rpy (results_1 and results_2).


screen presumptive_testing():
    # Kastle-Meyer reagent buttons plus a close button. Design notes in notes.md.
    default curr_attempt = []

    vbox:
        imagebutton: 
            idle "images/Environment Items/x_idle.png" 
            hover "images/Environment Items/x_hover.png"
            action Function(stop_test)
        imagebutton:
            idle "images/Environment Items/ethanol_idle.png" 
            hover "images/Environment Items/ethanol_hover.png"
            action [Function(add_reagent, curr_attempt, 'e'), SetLocalVariable("sensitive", False)]
        text "Ethanol"
        imagebutton: 
            idle  "images/Environment Items/reagent_idle.png" 
            hover "images/Environment Items/reagent_hover.png"
            action [Function(add_reagent, curr_attempt, 'p'), SetLocalVariable("sensitive", False)]
        text "Phenolphthalin"
        imagebutton: 
            idle "images/Environment Items/hydrogen_peroxide_idle.png" 
            hover "images/Environment Items/hydrogen_peroxide_hover.png"
            action [Function(add_reagent, curr_attempt, 'h'), SetLocalVariable("sensitive", False)]
        text "Hydrogen Peroxide"
        

screen environment_tester():
    zorder 100
    
    # Debug keys, only active when running from the Ren'Py SDK (config.developer).
    if config.developer:
        key "d" action Function(lambda: renpy.notify(f"{scenes[current_scene].get_state('dusted')}"))
        key "s" action Function(lambda: renpy.notify(f"{scenes[current_scene].states}"))
        key "m" action Function(lambda: renpy.notify(f"{mistake_inventory._inventory}"))
        key "b" action Function(lambda: renpy.notify(f"{swabbing}"))
        key "t" action Function(lambda: renpy.notify(f"{testing}"))







