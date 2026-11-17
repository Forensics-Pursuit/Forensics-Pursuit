# Level Select mockup (test build of The Studio).
#
# Flow:
#     main_menu (Forensics Pursuit hub, same look as FinalCrimeScene's menu)
#       -> "Start" -> select_level
#       -> hover / click the Level 02 "The Studio" box, then click Play
#       -> fades to studio_main_menu (The Studio's original menu, in screens.rpy)
#       -> "Play" -> label start (the real game)
#
# The level select images are full mockup screenshots (3420x2214). They aren't
# 16:9, so they're scaled to the full 1080 height and centred, with black bars
# at the sides (the mockup's edges are black, so the bars blend in).
#
# Only The Studio is hooked up. To add another level later, copy the Studio
# imagebutton in select_level and give it that level's box from the hover image.

init python:
    LS_DIR = "images/level_select/"
    LS_SCALE = 1080.0 / 2214.0
    LS_XOFFSET = int(round((1920 - 3420 * LS_SCALE) / 2))

    # Regions in the full-size (3420x2214) mockup images: (x, y, width, height).
    LS_STUDIO_BOX = (1149, 780, 2157, 379)
    LS_PLAY_BUTTON = (210, 1804, 762, 266)

    def ls_image(name):
        """A whole level select image, scaled to the screen height."""
        return Transform(LS_DIR + name + ".png", zoom=LS_SCALE)

    def ls_crop(name, box):
        """One region of a level select image, scaled the same way."""
        return Transform(Crop(box, LS_DIR + name + ".png"), zoom=LS_SCALE)

    def ls_pos(box):
        """Screen position of a region's top-left corner."""
        return (LS_XOFFSET + int(round(box[0] * LS_SCALE)), int(round(box[1] * LS_SCALE)))

    # STARS --------------------------------------------------------------------
    # Each level's best star count (0-3), saved in persistent data so it stays
    # after quitting the game. A level with no entry hasn't been finished yet,
    # so no stars are shown for it.

    LS_STAR_STEP = 135                # distance between stars in the mockup
    LS_STUDIO_STARS = (2087, 826)     # top-left of the Studio's first star

    def studio_stars_earned():
        """Stars for the Studio playthrough that just ended.

        Demo: always 0 for now. To grade it later, use the Performance Results
        score, e.g.:
            done, total, percent = results_grade()
            return 3 if percent >= 90 else 2 if percent >= 70 else 1 if percent >= 40 else 0
        """
        return 0

    def record_level_stars(level, stars):
        """Saves a finished level's stars, keeping the player's best result."""
        best = persistent.level_stars.get(level)
        if best is None or stars > best:
            persistent.level_stars[level] = stars
        renpy.save_persistent()


default persistent.level_stars = {}


# HUB MAIN MENU ----------------------------------------------------------------
# Same as FinalCrimeScene's main menu, except Start opens the level selector.

screen main_menu():
    tag menu

    add "gui/hub_main_menu.png"

    frame:
        style "hub_menu_frame"

    use hub_navigation


screen hub_navigation():
    vbox:
        style_prefix "hub_navigation"

        xpos gui.navigation_xpos
        yalign 0.5

        spacing 6

        textbutton _("Start") action ShowMenu("select_level")

        textbutton _("Load") action ShowMenu("load")

        textbutton _("Preferences") action ShowMenu("preferences")

        textbutton _("About") action ShowMenu("about")

        if renpy.variant("pc") or (renpy.variant("web") and not renpy.variant("mobile")):
            textbutton _("Help") action ShowMenu("help")

        if renpy.variant("pc"):
            textbutton _("Quit") action Quit(confirm=False)


style hub_menu_frame is empty
style hub_menu_frame:
    xsize 420
    yfill True
    background "gui/overlay/hub_main_menu_overlay.png"

# FinalCrimeScene's colours (The Studio's own gui.rpy uses white / yellow).
style hub_navigation_button is gui_button
style hub_navigation_button_text is gui_button_text

style hub_navigation_button:
    size_group "hub_navigation"
    properties gui.button_properties("navigation_button")

style hub_navigation_button_text:
    properties gui.text_properties("navigation_button")
    idle_color "#888888"
    hover_color "#66c1e0"
    selected_color "#ffffff"
    insensitive_color "#8888887f"


# LEVEL SELECT -----------------------------------------------------------------

screen select_level():
    tag menu

    # False: nothing chosen yet (select_level / select_level_hover).
    # True: The Studio was clicked (select_level_info / select_level_play_hover).
    default studio_selected = False

    add Solid("#000")

    if not studio_selected:
        add ls_image("select_level") xpos LS_XOFFSET

        # Level 02 - The Studio: highlights on hover, shows its info on click.
        imagebutton:
            pos ls_pos(LS_STUDIO_BOX)
            idle Null(int(LS_STUDIO_BOX[2] * LS_SCALE), int(LS_STUDIO_BOX[3] * LS_SCALE))
            hover ls_crop("select_level_hover", LS_STUDIO_BOX)
            action SetScreenVariable("studio_selected", True)

    else:
        add ls_image("select_level_info") xpos LS_XOFFSET

        # Clicking The Studio again deselects it.
        button:
            pos ls_pos(LS_STUDIO_BOX)
            xysize (int(LS_STUDIO_BOX[2] * LS_SCALE), int(LS_STUDIO_BOX[3] * LS_SCALE))
            background None
            action SetScreenVariable("studio_selected", False)

        # Play: brightens on hover, fades into The Studio's own main menu.
        imagebutton:
            pos ls_pos(LS_PLAY_BUTTON)
            idle Null(int(LS_PLAY_BUTTON[2] * LS_SCALE), int(LS_PLAY_BUTTON[3] * LS_SCALE))
            hover ls_crop("select_level_play_hover", LS_PLAY_BUTTON)
            action Show("studio_main_menu", transition=Fade(0.5, 0.3, 0.5))

    # Stars on The Studio's box, once it has been finished at least once.
    $ studio_stars = persistent.level_stars.get("studio")
    if studio_stars is not None:
        for i in range(3):
            add ls_image("star_filled" if i < studio_stars else "star_empty"):
                pos ls_pos((LS_STUDIO_STARS[0] + i * LS_STAR_STEP, LS_STUDIO_STARS[1]))

    # Back arrow (bottom right): returns to the hub menu.
    imagebutton:
        auto "back_button_%s.png"
        at Transform(zoom=0.2)
        xpos 1810
        ypos 965
        action Show("main_menu", transition=Dissolve(0.3))

    # Esc / right-click also goes back to the hub menu.
    key "game_menu" action Show("main_menu", transition=Dissolve(0.3))
