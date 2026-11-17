# The script of the game goes in this file.

# Declare characters used by this game. The color argument colorizes the
# name of the character.

define s = Character("Supervisor")


# The game starts here.

screen back_button_screen(old_location):
    zorder 1
    hbox:
        xalign 0.01 yalign 0.98
        imagebutton:
            idle "back_button" at Transform(zoom=0.2)
            hover "back_button_hover"
            action [SetVariable("imported_print", ""), SetVariable("print_imported", False), Hide('afis_screen'), Hide("casefile_physical"), SetVariable("location", old_location), Jump(old_location)]

label start:
    jump oven
