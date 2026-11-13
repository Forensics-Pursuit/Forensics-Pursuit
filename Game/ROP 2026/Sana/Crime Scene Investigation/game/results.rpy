# End-of-level results: the Performance Results rubric (screen results_1) and the
# Mistakes clipboard (screen results_2), plus add_mistake() for recording mistakes.
#
# This file is meant to be shared between levels unchanged (it is used by both
# The Studio and FinalCrimeScene). Each level only needs:
#
#     1. jsons/results.json with:
#         - "mistakes_file": the level's mistakes json (each mistake has name,
#           image_name and description, like inventory items).
#         - "steps": the graded investigation steps, in order. Each step has a
#           "label" (the text shown on the rubric) and either:
#               "task": a key in the level's `tasks` dict (done when True), or
#               "evidence": an evidence item name (done when it's in the evidence inventory).
#           The grade is one mark per completed step.
#         - "spots": the places in the level where mistakes can happen, in the
#           order they should appear on the Mistakes clipboard. Each spot has
#           "id", "name", "image" (a 338x223 thumbnail) and "evidence" (the
#           evidence item names collected there, so missing evidence is shown on
#           the right thumbnail).
#     2. A `mistake_inventory` (an Inventory) that is emptied when a new game starts.
#     3. Calls to add_mistake("<name>", spot="<spot id>", where="<detail>") when the
#        player makes a mistake. If spot is left out, results_default_spot() is
#        used when the level defines one (e.g. the scene the player is in).
#     4. add_missing_evidence_mistakes() and then "call show_results" when the
#        level ends. It shows results_1, then results_2, with a back arrow
#        between them; Done returns "done" to the level so it can wrap up.
#
# Up to 9 spots fit on the Mistakes clipboard (3 x 3).

define results_font = "gui/fonts/PatrickHand-Regular.ttf"


init python:
    import json

    def load_results(filename):
        with renpy.file(filename) as f:
            data = json.loads(f.read().decode("utf-8"))

        data["spot_by_id"] = {spot["id"]: spot for spot in data["spots"]}
        data["evidence_spot"] = {}
        for spot in data["spots"]:
            for name in spot.get("evidence", []):
                data["evidence_spot"][name] = spot["id"]
        return data

    results_config = load_results("jsons/results.json")
    results_mistake_items = load_items(results_config["mistakes_file"])

    # RECORDING MISTAKES -------------------------------------------------------

    def add_mistake(name, spot=None, where=None):
        """Records a mistake (a name from the mistakes json) at a spot from
        results.json. The same mistake at the same spot and detail is only
        recorded once.
        """
        if spot is None and "results_default_spot" in globals():
            spot = results_default_spot()

        for mistake in mistake_inventory._inventory:
            if mistake.name == name and getattr(mistake, "spot", None) == spot and getattr(mistake, "where", None) == where:
                return # already recorded

        base = results_mistake_items[name]
        mistake = Item(base.name, base.image_name, base.description)
        mistake.spot = spot
        mistake.where = where
        mistake_inventory.add_to_inventory(mistake)

    def collected_evidence_names():
        return set(item.name for item in evidence._inventory)

    def add_missing_evidence_mistakes():
        """Adds a "Missing Evidence" mistake for every evidence item listed under a
        spot in results.json that the player didn't collect.
        """
        collected = collected_evidence_names()
        for name, spot in results_config["evidence_spot"].items():
            if name not in collected:
                add_mistake("Missing Evidence", spot=spot, where=name)

    # GRADING -----------------------------------------------------------------

    def results_step_done(step):
        if "task" in step:
            return bool(globals().get("tasks", {}).get(step["task"]))
        if "evidence" in step:
            return step["evidence"] in collected_evidence_names()
        return False

    def results_steps():
        """[(label, done), ...] for every graded step."""
        return [(step["label"], results_step_done(step)) for step in results_config["steps"]]

    def results_grade():
        """(marks earned, total marks, percentage rounded down)."""
        steps = results_steps()
        done = sum(1 for _, d in steps if d)
        total = len(steps)
        percent = (100 * done) // total if total else 0
        return done, total, percent

    def results_spots_with_mistakes():
        """[(spot, [mistakes]), ...] for every spot where the player made a mistake,
        in the order the spots are listed in results.json.
        """
        grouped = []
        for spot in results_config["spots"]:
            found = [m for m in mistake_inventory._inventory if getattr(m, "spot", None) == spot["id"]]
            if found:
                grouped.append((spot, found))

        # Mistakes recorded without a spot still need to be shown somewhere.
        loose = [m for m in mistake_inventory._inventory if getattr(m, "spot", None) not in results_config["spot_by_id"]]
        if loose:
            grouped.append(({"id": "other", "name": "Other", "image": Solid("#555")}, loose))
        return grouped


# RESULTS 1: PERFORMANCE RESULTS RUBRIC ----------------------------------------

screen results_1():
    modal True
    add Solid("#0009")

    $ done, total, percent = results_grade()

    fixed:
        xysize (735, 1080)
        xalign 0.5

        add "images/results/rubric_blank.png"

        # Grade (next to "Grade:") and percentage (inside the red circle).
        text "[done]/[total]":
            font results_font
            size 52
            color "#d4a21f"
            xpos 216
            ypos 296

        text "[percent]%":
            font results_font
            size 54
            color "#a3161a"
            xcenter 619
            ycenter 382

        # Checklist: one row per ruled line on the paper.
        for i, (label, step_done) in enumerate(results_steps()):
            fixed:
                xpos 72
                ypos 428 + i * 61
                xysize (640, 50)

                if step_done:
                    add "images/results/checkbox_done.png" yalign 0.5
                    text "{s}[label]{/s}":
                        font results_font
                        size 38
                        color "#a9a9a9"
                        xpos 48
                        yalign 0.5
                else:
                    add "images/results/checkbox_empty.png" xoffset 6 yalign 0.5
                    text "[label]":
                        font results_font
                        size 38
                        color "#3b3b3b"
                        xpos 48
                        yalign 0.5

    # Next: go to the Mistakes clipboard.
    imagebutton:
        idle "ui/inventory-arrow-right-enabled-idle.png"
        hover "ui/inventory-arrow-right-enabled-hover.png"
        xalign 1.0
        yalign 1.0
        xoffset -40
        yoffset -30
        action Return()


# RESULTS 2: MISTAKES CLIPBOARD ------------------------------------------------

screen results_2():
    modal True
    add Solid("#0009")

    $ spots = results_spots_with_mistakes()

    fixed:
        xysize (1553, 1056)
        align (0.5, 0.5)

        add "images/results/mistakes_blank.png"

        if not spots:
            text "No mistakes, great work!":
                font results_font
                size 60
                color "#3b3b3b"
                xcenter 910
                ycenter 520

        # Thumbnails in a 3 x 3 grid, matching the mockup layout. Hovering one
        # outlines it in red and shows what went wrong there.
        for i, (spot, mistakes) in enumerate(spots[:9]):
            button:
                # The outline image has a 20px margin around the 338x223 thumbnail.
                xpos 364 + (i % 3) * 377 - 20
                ypos 188 + (i // 3) * 264 - 20
                xysize (378, 263)
                padding (0, 0)
                background None
                hover_background "images/results/spot_hover.png"
                tooltip (i, spot, mistakes)
                action NullAction()

                add Transform(spot["image"], xysize=(338, 223)) pos (20, 20)
                add "images/results/mistake_x.png" pos (20 + 290, 20 + 168)

    # Hover text: a note right below the hovered thumbnail (or above it if
    # there isn't room below). It may cover other thumbnails while hovering.
    $ tip = GetTooltip()
    if tip:
        $ tip_index, tip_spot, tip_mistakes = tip
        $ tip_lines = []
        for m in tip_mistakes:
            $ heading = m.name if not getattr(m, "where", None) else "{} ({})".format(m.name, m.where)
            $ tip_lines.append("{color=#b3161a}" + heading + ":{/color} " + m.description)
        # More than 3 mistakes: split into two columns with smaller text.
        $ half = (len(tip_lines) + 1) // 2
        $ tip_columns = [tip_lines] if len(tip_lines) <= 3 else [tip_lines[:half], tip_lines[half:]]
        $ tip_size = 27 if len(tip_lines) <= 3 else 23

        nearrect:
            focus "tooltip"
            prefer_top False

            # Line the note up with the thumbnail's column so it stays on the
            # clipboard: left column -> left edges, right column -> right edges.
            frame:
                xalign [0.0, 0.5, 1.0][tip_index % 3]
                yoffset 6
                background "#3a2a1e"
                padding (4, 4)

                frame:
                    background "#fffdf5"
                    padding (20, 10)

                    vbox:
                        spacing 4
                        text tip_spot["name"]:
                            font results_font
                            size 34
                            color "#3b3b3b"
                        hbox:
                            spacing 26
                            for column in tip_columns:
                                vbox:
                                    spacing 6
                                    xsize (640 if len(tip_columns) == 1 else 430)
                                    for line in column:
                                        text line:
                                            font results_font
                                            size tip_size
                                            color "#3b3b3b"
                                            substitute False

    # Back: return to the Performance Results rubric.
    imagebutton:
        idle "ui/inventory-arrow-left-enabled-idle.png"
        hover "ui/inventory-arrow-left-enabled-hover.png"
        xalign 0.0
        yalign 1.0
        xoffset 25
        yoffset -30
        action Return("back")

    # Done: close the clipboard and carry on with the level's ending.
    textbutton "Done":
        xalign 1.0
        yalign 1.0
        xoffset -50
        yoffset -30
        text_font results_font
        text_size 64
        text_color "#ffffff"
        text_hover_color "#e0453a"
        action Return("done")


# Shows the two results screens in order. The back arrow on results_2 returns
# "back", which goes round again to results_1.
label show_results:
    call screen results_1
    call screen results_2
    if _return == "back":
        jump show_results
    return
