# Crime Scene Investigation: design notes

Design notes moved out of the game scripts so the code stays readable. Sections name the file they came from.

## Why `swabbing` is a variable (`environment_screens.rpy`)

This variable is how the game will be able to tell if the player has a swab equipped. I wanted to tie this check to what the mouse pointer was
but the value of that variable, mouse.config, cannot be directly accessed from within the game.

After further examination there is a function that does exactly what I wanted making this variable redundant.

After further, further, playtesting, the current mouse changes when you are hovering over a button. This is an issue if you want to interact with a hotspot 
while swabbing is on going. Thus, we must have a swabbing variable.

## The `main` screen (`environment_screens.rpy`)

I've addded this screen to help make the visual parts of the game more modular. For example, the bedroom_screen previously implemented 
the interactable hotspots and also used the leave_button. While this is fine, I found that it made implementing the presumptive test portion
more difficult as I wanted to only have the interactable hotspots without the leave button. In other words, there was high coupling between the 
two screens.

The solution was to add this new screen. In this way every single screen has a single responsibility. The leave_button is responsible for ending the
game, the bedroom_main screen is responsible for implementing user interaction with the environment, and the main screen is the top screen that controls
everything that is being show to the player.

I went back to the CSC207 notes to try understanding what kind of design pattern this was. If I am not mistaken, this screen will essentially be the 
view of the clean architecture engine. The ViewModel of my program would then be the Scene class. By definition a view model stores the information
that the view must acess to display something. In this case, that information would be the variable current_scene.

I should mention that the Scene class does violate the SRP as it is also a member of the entity layer and stores all temporary information on player
progress trough the level, Additionally, the swabbing variable should ideally be an attribute of the view model class as it is also used to determine what is 
displayed; however, given how little information is required by the view model and the limited scope of this project, I see no point in 
refactoring to address these issues :)

In addition to the above, there are a few more really convenient things about moving this logic here:

- 1: In my mind, the back_button and leave_button are analgous to one another. They both take the use a step out of where they are
  currently and are both displayed in the top right. Previously, I had to split the usage of this button in every single environment screen.
  By centralizing the logic, this relationship is made far more clear.

- 2: Previously I had to explicitly control every single bedroom screen. This meant using a show statement every time the user clicked on the
  relevant hotspot and a hide statement when they used the back button. Furthermore, to make this hide statement work, the back button needed a parameter
  that represented what screen should be hidden. Encapsulating the logic of screen changes behind the use expression above allowed me to avoid
  copy pasting use statements in every class and allowed me to remove that extra parameter from the back_button screen!

## The presumptive test screen (`environment_screens.rpy`)

This screen is where the presumptive test will be implemented. There will be four image buttons. Three for the 
Kastle-meyer reagents and one return button. 

I will not allow the player to make the mistake of adding too much of a reagent as this quantitative error is hard 
to accurately represent. I will allow them to make the mistake of doing the procedure in the wrong order and allow
for a false positive to occur. These will be implemented by making each button interactable with once and having a colour
change after adding the phenophtahlin. 

## Debugging tip (`environment_screens.rpy`, `environment_tester` screen)

For the past three weeks I have tried and failed to make a simple variable change work after using one of the items.
Or so I thought. I was checking by using the built in renpy console that is brought up by shift+o. The issue is,
That stupid thing for some reason does not reflect changes made to global variables within functions. 
If you want to ensure that a function does change what you want it to...USE A KEY LIKE BELOW.

## The removed glove mechanic (`inventory_functions.rpy`)

I have made the decision not to include anything glove related. 

The most frequently repeated mistake in playtesting was people forgetting to put gloves on or to change gloves between evidence items. 
Initially I felt that this was an indication that testing for proper gloving was essential. In my mind it is simlar to taking photographs of 
everything: an unglamorous step that is integral to ensuring that the integrity of evidence and your credibility as an investigator is maintained.

With that said, I feel that there is no proper way to include gloving within the game as gloves are entirely tactile. By the very nature of video games,
there is a diminishing of touch. Players cannot feel their hands getting sweaty in a pair of gloves or the sensation of grabbing an object and rendering
the gloves unclean. In Ren'py especially, there is no body that the player can look at and they exist as naught but a crime solving ghostly apparition. 

The issue can be simplified as a single implication: if you touch an item without gloves then you have contaminated it and made a mistake in the crime
scene investigation. Given that the feeling of touch essentially does not exist within the game, this statement will always be vaccuously true rendering
a gloving mechanic useless.

There is likely a way to invoke the missing tactile sensation but I feel that Ren'py is poorly suited for such a task and that I lack the visual design
elements to sucessfully execute such a task.

The old glove code, kept for reference:

```python
from enum import Enum

class GloveStatus(Enum):
    CLEAN = 1
    GLOVELESS = 0
    DIRTY_MAIN = -1
    DIRTY_ANGEL_HEAD = -2
    DIRTY_ANGEL_STATUES = -3

def use_gloves():
    global clean_gloves
    renpy.notify("You have put a clean pair of gloves on.")
    clean_gloves = GloveStatus.CLEAN.value
    renpy.play("gloves.mp3")

def glove_check():
    global clean_gloves
    if clean_gloves == -1:
        mistake_inventory.add_to_inventory(mistakes["Dirty Gloves"])
    elif clean_gloves == 0:
        mistake_inventory.add_to_inventory(mistakes["No Gloves"])
    else:
        clean_gloves = -1
```
