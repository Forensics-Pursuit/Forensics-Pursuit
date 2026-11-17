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
#           Optional "category": one of identify / process / collect / preserve.
#           The rubric then groups the steps under those headings (in that
#           order), and leaves out any heading with no steps.
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

# The furthest rubric page the player has looked at (0 = the first page).
# The right arrow to the Mistakes clipboard stays greyed out until every
# rubric page has been seen.
default results_pages_seen = 0

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

    RESULTS_CATEGORIES = [
        ("identify", "Identify"),
        ("process", "Process"),
        ("collect", "Collect"),
        ("preserve", "Preserve"),
    ]

    def results_rubric_rows():
        """Rows for the rubric checklist: ("header", title) for each category
        that has steps, then ("step", (label, done)) for each of its steps.
        Steps without a category are listed after the categories, and if no
        step has a category it's just the plain list of steps.
        """
        steps = [(step.get("category"), (step["label"], results_step_done(step)))
                 for step in results_config["steps"]]
        rows = []
        for key, title in RESULTS_CATEGORIES:
            in_category = [s for c, s in steps if c == key]
            if in_category:
                rows.append(("header", title))
                rows.extend(("step", s) for s in in_category)
        known = [key for key, _ in RESULTS_CATEGORIES]
        rows.extend(("step", s) for c, s in steps if c not in known)
        return rows

    # The ruled lines on the rubric paper (y of each line, top to bottom).
    # Each checklist row is written on one of these lines.
    RESULTS_LINES = [296, 357, 418, 478, 539, 599, 660, 721, 781, 842, 902, 963, 1023]
    # Page 1 starts on the 4th line (under "Grade:" and the percentage circle);
    # later pages start on the 2nd line.
    RESULTS_FIRST_LINE = [3, 1]

    def results_page_lines(page):
        start = RESULTS_FIRST_LINE[0] if page == 0 else RESULTS_FIRST_LINE[1]
        return RESULTS_LINES[start:]

    def results_rubric_pages():
        """Splits the checklist rows into pages: [(rows, more_follow), ...].

        A category (its heading and steps) is never split between pages; if it
        doesn't fit, it moves to the next page. When another page follows, the
        last line of the page is kept free for "...". A category too long to
        fit on a page of its own is the only thing that gets split, and its
        heading is repeated on the next page.
        """
        blocks = []
        for row in results_rubric_rows():
            if row[0] == "header" or not blocks or blocks[-1][0][0] != "header":
                blocks.append([row])
            else:
                blocks[-1].append(row)

        pages = []
        while True:
            capacity = len(results_page_lines(len(pages)))
            if sum(len(b) for b in blocks) <= capacity:
                pages.append(([row for b in blocks for row in b], False))
                return pages

            room = capacity - 1 # last line is for "..."
            page = []
            while blocks and len(page) + len(blocks[0]) <= room:
                page.extend(blocks.pop(0))

            if not page:
                block = blocks[0]
                page = block[:room]
                rest = block[room:]
                blocks[0] = ([block[0]] if block[0][0] == "header" else []) + rest

            pages.append((page, True))

    def results_grade_color(percent):
        """Grade colour: red under 40%, yellow 40-69%, light green 70-79%,
        green 80% and up.
        """
        if percent < 40:
            return "#c62828"
        elif percent < 70:
            return "#d4a21f"
        elif percent < 80:
            return "#7cb342"
        return "#2e7d32"

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

    # Which rubric page is showing (0 = the first, with the grade).
    default page = 0

    $ done, total, percent = results_grade()
    $ pages = results_rubric_pages()
    $ rows, more_follow = pages[page]
    $ lines = results_page_lines(page)

    fixed:
        xysize (735, 1080)
        xalign 0.5

        if page == 0:
            add "images/results/rubric_blank.png"

            # Grade (next to "Grade:") and percentage (inside the red circle).
            text "[done]/[total]":
                font results_font
                size 52
                color results_grade_color(percent)
                xpos 216
                ypos 296

            text "[percent]%":
                font results_font
                size 54
                color "#a3161a"
                xcenter 619
                ycenter 382
        else:
            add "images/results/rubric_blank_page2.png"

        # Checklist: each row is written on one of the paper's ruled lines.
        for i, (kind, row) in enumerate(rows):
            fixed:
                xpos 72
                ypos lines[i] - 50
                xysize (640, 50)

                if kind == "header":
                    # "▶ Identify:" heading, a little left of the steps.
                    add "images/results/heading_arrow.png" xpos -24 yalign 0.5
                    text "[row]:":
                        font results_font
                        size 40
                        bold True
                        italic True
                        color "#3b3b3b"
                        yalign 0.5

                else:
                    $ label, step_done = row
                    if step_done:
                        add "images/results/checkbox_done.png" xpos 20 yalign 0.5
                        text "{s}[label]{/s}":
                            font results_font
                            size 38
                            color "#a9a9a9"
                            xpos 68
                            yalign 0.5
                    else:
                        add "images/results/checkbox_empty.png" xpos 26 yalign 0.5
                        text "[label]":
                            font results_font
                            size 38
                            color "#3b3b3b"
                            xpos 68
                            yalign 0.5

        # More on the next page: "..." on the bottom line, and a down arrow in
        # the bottom-right corner of the clipboard.
        if more_follow:
            text "...":
                font results_font
                size 40
                color "#3b3b3b"
                xpos 72
                yanchor 0.5
                ypos lines[-1] - 25

            imagebutton:
                # The screen's arrow, turned down, with a dark backing so it shows on paper.
                auto "images/results/arrow_down_%s.png"
                at Transform(zoom=0.6)
                xanchor 0.5
                yanchor 0.5
                xpos 664
                ypos 1000
                action [
                    SetScreenVariable("page", page + 1),
                    SetVariable("results_pages_seen", max(results_pages_seen, page + 1)),
                ]

        # Later pages: an up arrow in the top-right corner of the paper (beside
        # the clip) goes back a page.
        if page > 0:
            imagebutton:
                # The screen's arrow, turned up, with a dark backing so it shows on paper.
                auto "images/results/arrow_up_%s.png"
                at Transform(zoom=0.6)
                xanchor 0.5
                yanchor 0.5
                xpos 664
                ypos 212
                action SetScreenVariable("page", page - 1)

    # Next: go to the Mistakes clipboard. Greyed out until the player has
    # looked at every rubric page.
    imagebutton:
        idle "ui/inventory-arrow-right-enabled-idle.png"
        hover "ui/inventory-arrow-right-enabled-hover.png"
        insensitive "images/results/arrow_right_disabled.png"
        sensitive results_pages_seen >= len(pages) - 1
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
    $ results_pages_seen = 0

# Coming back from the Mistakes clipboard doesn't lock the right arrow again.
label show_results_again:
    call screen results_1
    call screen results_2
    if _return == "back":
        jump show_results_again
    return
