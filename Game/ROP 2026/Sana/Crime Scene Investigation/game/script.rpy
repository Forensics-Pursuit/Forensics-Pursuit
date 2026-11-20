# The script of the game goes in this file.

# Declare characters used by this game. The color argument colorizes the
# name of the character.

#The current screen var is referred to within the inventory function which has init of -5
init python:
    import json

    tools = load_items("jsons/toolbox.json") #Gets dictionary representing all tools contained in toolbox.json
    # Tape and Backing Card are left out of the starting toolbox (the combined "Backing Card and Tape" is used instead).
    STARTING_TOOLS = [name for name in tools if name not in ("Tape", "Backing Card")]
    
    evies = load_items("jsons/evidence.json")

    mistakes = load_items("jsons/mistakes.json")

    #Line below is for testing
    #for mistake in mistakes: mistake_inventory.add_to_inventory(mistakes[mistake])


# Holds mistakes as the player makes them (used by results.rpy). A default, so it is saved and fresh each new game.
default mistake_inventory = Inventory()


define config.mouse_displayable = MouseDisplayable(
    "images/default_cursor.png", 15, 15
    ).add(
        "clean swab","images/Toolbox Items/clean_swab.png", 150, 138
        ).add(
            "red swab","images/Toolbox Items/red_swab.png", 150, 138
            ).add(
                "pink swab","images/Toolbox Items/pink_swab.png", 150, 138
                )


#-1 contaminated gloves, 0 no gloves, 1 clean gloves
define s = Character(name=("Nina"), image="nina")


label start:
    # evidence and mistake_inventory start empty because they are defaults; the toolbox is filled here.
    $ toolbox.set_inventory([tools[name] for name in STARTING_TOOLS])

    scene outside_crime_scene
    "May 16, 2026 12:17 PM. 13 Reaper's End."
    
    show nina smile
    s "Officer, glad you could make it"
    s normal1 "Behind me is the Peaceful Rest Senior Retirement Community."
    s thinknote1 "From what I've heard it's the best place in the city for people looking to boot their parents out of the house."
    s "At least..."
    s normal1 "...Under normal circumstances."

    s normal1 "Police received a call around 10 this morning reporting the sudden death of a patient, Mary Sullivan, aged 75."
    s "Staff claim she was in good health during her morning checkup and had no underlying health conditions."

    s write "Mary was paid a visit by her daughter, Jane Sullivan, at around 9."
    s "Typically such a visit would be supervised."
    s "However, a facility emergency led to an hour long gap from the time Jane entered the facility, left the premises, and when Mary was found deceased."

    s normal1 "The deceased has been transferred to the morgue and the initial state of the room has been preserved."
    s "That's about all the details I have for you right now, Officer."
    s "I'm sure you don't need me to tell you what to do with the scene."

    s normal1 "Good luck, Officer. We're counting on you to help us solve this case."
    
    scene bg bedroom 

    show screen open_inv

    show screen environment_tester

    call screen main

label review_mistakes:
    python:
        # Mistakes that can only be checked once the player is done. They're filed
        # under the angel head, which is where they happen (see jsons/results.json).
        if scenes["angel_head"].get_state("examined"):
            if not scenes["angel_head"].get_state("scene_photographed"): add_mistake("No Photo Scene", spot="angel_head")
            if scenes["angel_head"].get_state("enhanced"):
                if not scenes["angel_head"].get_state("enhanced_photographed"): add_mistake("No Developed Fingerprint Photograph", spot="angel_head")
            else: add_mistake("Incomplete Fingerprint Development", spot="angel_head")

        # One "Missing Evidence" per uncollected item, on that item's spot.
        add_missing_evidence_mistakes()

    hide screen inventory
    hide screen main
    hide screen open_inv

    scene outside_crime_scene
    show nina normal1 at right
    s "All finished, Officer?"
    
    s write "Let's see how you did!"

    if len(mistake_inventory._inventory) == 0:
        s normal1 "Oh..."
       
        s write "My..."
        
        s smile "Goodness..."

        $renpy.play("victory.mp3")

        s "You investigated the crime scene perfectly!"
        s "I always knew you could do it without ever making a single mistake."

    # Performance Results rubric, then the Mistakes clipboard (results.rpy).
    call show_results

    # Done was pressed: the clipboard is gone, Nina signs off, back to the main menu.
    s smile "Great work today!"
    $ MainMenu(confirm=False)()
