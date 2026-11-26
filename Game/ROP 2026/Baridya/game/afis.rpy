################################################################################
## Lab Level
################################################################################
##
## FINGERPRINTS (working): an AFIS terminal. Since fingerprint evidence is
## collected optionally in different spots (door handle is mandatory, the can
## and steering wheel prints are optional), we don't hardcode which evidence
## item name to expect. Instead, on entering the lab we scan `evidence`
## (the same Inventory object used everywhere else) for any collected item
## whose name looks like a print, and wire each one up as importable.
##
## DNA (placeholder, unchanged): gel-band matching minigame. Not the focus
## of this pass.
##
## ---------------------------------------------------------------------------
## ASSET REQUIREMENTS
## ---------------------------------------------------------------------------
##   lab_hallway, data_analysis_lab_idle/hover, materials_lab_idle/hover
##                                  -> the lab hallway hub background + room
##                                     buttons (see screen lab_hub)
##
## AFIS database cards (from your source lab images, ~431x578):
##   print_1, print_2, print_3   -> however you already have these named/
##                                  loaded from your source project. If your
##                                  existing image names differ, just edit
##                                  the `image=` values in afis_prints below.
##
## For the IMPORTED side, each collected print gets its own card. If you
## already have specific art for "the door handle print" etc., add an entry
## to PRINT_EVIDENCE_IMAGES below (evidence item name -> image name) and
## it'll be used automatically. Anything not listed there just falls back
## to that evidence item's own inventory icon, so nothing breaks if you
## haven't made dedicated AFIS art for every possible print yet.
################################################################################

init -5 python:

    ############################################################################
    ## AFIS -- fingerprint database
    ############################################################################

    import os

    ## Where your source lab's print_1.png..print_7.png and their
    ## print_i_closeup_j.png files live. Change this if yours are elsewhere.
    DATA_LAB_DIR = "images/data_analysis_lab"

    def afis_file_exists(file_name):
        """file_name must end in .png"""
        file_path = os.path.join(renpy.config.gamedir, DATA_LAB_DIR, file_name)
        return os.path.isfile(file_path)

    NUM_DB_PRINTS = 6

    ## --- Who's who --------------------------------------------------------
    _robber_name = "Denise Cole"
    _owner_name = "Patricia Nguyen"

    ## print_5 and print_6 are both booking-card scans of the SAME finger --
    ## the robber's, taken at two different arrests -- so print_6 is set to
    ## reuse print_5's actual image file below. That's what guarantees they
    ## look identical, not just that they're flagged as a match in code.
    ##
    ## The real matches (robber x2, elimination x1) are deliberately placed
    ## at the END of the browsable deck (print_4/5/6), with pure decoys at
    ## print_1/2/3, so the default starting card is never a match and the
    ## player actually has to browse the whole database instead of winning
    ## on the very first click.
    ROBBER_PRINT_KEYS = ["print_5", "print_6"]
    ELIMINATION_PRINT_KEY = "print_4"

    class AfisMCQ(object):
        """
        A multiple-choice pattern-matching question, asked about a database
        print's ridge pattern (whorl/loop/arch/etc.) after Compare and
        before the match result -- teaches the player to actually look at
        what's on screen instead of just clicking through. Answering wrong
        loops the question again instead of moving on.

        - choices: list of (text, is_correct) tuples
        - responses: list of lists of strings -- responses[i] is what plays
          after picking choice i, whether right or wrong
        """
        def __init__(self, question, choices, responses):
            self.question = question
            self.choices = choices
            self.responses = responses

        def items(self):
            return [(text, i) for i, (text, _correct) in enumerate(self.choices)]

        def is_correct(self, choice):
            if 0 <= choice < len(self.choices):
                return self.choices[choice][1]
            return False

    DB_PRINT_INFO = {
        # key: (image asset to use, description)
        "print_1": ("print_3", "Unrelated record on file, not connected to this case."),
        "print_2": ("print_2", "Unrelated record on file, not connected to this case."),
        "print_3": ("print_7", "Unrelated record on file, not connected to this case."),
        "print_4": ("print_6", "Elimination print on file for %s, the car's registered owner." % _owner_name),
        "print_5": ("print_1", "Booking record from an arrest two years ago: %s." % _robber_name),
        "print_6": ("print_1", "A second booking record, eight months ago: %s again." % _robber_name),
    }

    ## Pattern-matching quiz per database card, asked after Compare and
    ## before the result. Keyed by which IMAGE each slot actually shows
    ## (per DB_PRINT_INFO above), since the question is about what's
    ## visually on screen, not the slot number.
    DB_PRINT_MCQS = {
        "print_5": AfisMCQ(
            question="Examine the core and delta positioning. What is the primary ridge classification?",
            choices=[("Loop", False), ("Arch", False), ("Whorl", True)],
            responses=[
                ["That's not a loop pattern.", "Take another look."],
                ["That's not an arch pattern.", "Take another look."],
                ["That's a whorl, the ridges circle back on themselves.", "Let's finish the comparison."],
            ],
        ),
        "print_4": AfisMCQ(
            question="Identify the ridge flow pattern shown in this sample.",
            choices=[("Whorl", False), ("Loop", True), ("Arch", False)],
            responses=[
                ["That's not a whorl pattern.", "Take another look."],
                ["That's a loop, the ridges curve and come back out the same side.", "Let's finish the comparison."],
                ["That's not an arch pattern.", "Take another look."],
            ],
        ),
        "print_1": AfisMCQ(
            question="Classify the friction ridge pattern displayed above.",
            choices=[("Arch", True), ("Whorl", False), ("Loop", False)],
            responses=[
                ["That's an arch, the ridges rise in the middle with no backward turn.", "Let's finish the comparison."],
                ["That's not a whorl pattern.", "Take another look."],
                ["That's not a loop pattern.", "Take another look."],
            ],
        ),
        "print_2": AfisMCQ(
            question="What dermatoglyphic classification does this print exhibit?",
            choices=[("Loop", False), ("Whorl", True), ("Arch", False)],
            responses=[
                ["That's not a loop pattern.", "Take another look."],
                ["That's a whorl, the ridges circle back on themselves.", "Let's finish the comparison."],
                ["That's not an arch pattern.", "Take another look."],
            ],
        ),
        "print_3": AfisMCQ(
            question="Identify the focal points to determine the ridge pattern group.",
            choices=[("Whorl", False), ("Loop", False), ("Arch", True)],
            responses=[
                ["That's not a whorl pattern.", "Take another look."],
                ["That's not a loop pattern.", "Take another look."],
                ["That's an arch, the ridges rise in the middle with no backward turn.", "Let's finish the comparison."],
            ],
        ),
    }
    DB_PRINT_MCQS["print_6"] = DB_PRINT_MCQS["print_5"]  # shares print_5's image

    ## Every imported print reuses a database card's image, since it's meant
    ## to be an actual finger already in one of those records -- not a new
    ## unknown person. Which one depends on WHERE it was lifted from:
    ##   - steering wheel  -> the owner's print (elimination, print_4)
    ##   - anything else (door handle, can, ...) -> the robber's print (print_5)
    ## Add more entries to PRINT_SOURCE_RULES below if you add more pickup
    ## spots later (each entry is (keyword-in-item-name, db_key)).
    PRINT_SOURCE_RULES = [
        ("wheel", "print_4"),
    ]
    PRINT_SOURCE_DEFAULT_DB_KEY = "print_5"

    ## Map specific evidence item names to dedicated AFIS card art, if/when
    ## you make some. Anything collected that isn't listed here falls back
    ## to the rule above.
    PRINT_EVIDENCE_IMAGES = {
        # "Fingerprint": "afis-print-door-handle",
        # "Can Fingerprint": "afis-print-can",
        # "Wheel Fingerprint": "afis-print-wheel",
    }

    ## Only evidence items whose name contains one of these (case-insensitive)
    ## are treated as importable prints in the AFIS terminal.
    PRINT_NAME_KEYWORDS = ["print", "fingerprint"]

    ## Score every imported print against each database card. True/False
    ## marks whether it's a match; the number is the displayed consistency %.
    ROBBER_SOURCE_SCORES = {
        "print_1": (False, 18),
        "print_2": (False, 24),
        "print_3": (False, 15),
        "print_4": (False, 9),
        "print_5": (True, 96),
        "print_6": (True, 91),
    }
    OWNER_SOURCE_SCORES = {
        "print_1": (False, 17),
        "print_2": (False, 22),
        "print_3": (False, 16),
        "print_4": (True, 94),
        "print_5": (False, 11),
        "print_6": (False, 13),
    }

    class AfisPrint(object):
        """
        A single print card in the AFIS system.

        - image: the big comparison image (~431x578), no file extension.
        - closeup_1/2/3 (optional): zoomed-in detail shots shown during
          "Compare". Falls back to `image` when unset.
        - description: revealed in dialogue once this print is identified.
        - scores: REQUIRED for imported prints. Maps a database card's key
          to (is_match, consistency_percent).
        - mcq (optional): only meaningful on database cards -- an AfisMCQ
          asked while that card is the one being viewed.
        """
        def __init__(self, image, closeup_1="", closeup_2="", closeup_3="", description="", scores=None, mcq=None):
            self.image = image
            self.closeup_1 = closeup_1
            self.closeup_2 = closeup_2
            self.closeup_3 = closeup_3
            self.description = description
            self.scores = scores or {}
            self.mcq = mcq
            self.processed = False

        def process(self):
            self.processed = True

    def make_afis_print(image, description="", scores=None, mcq=None):
        """Builds an AfisPrint and auto-attaches closeup_1/2/3 if matching
        <image>_closeup_1/2/3.png files exist in DATA_LAB_DIR -- same
        detection technique your source lab's afis.rpy used."""
        p = AfisPrint(image=image, description=description, scores=scores, mcq=mcq)
        for j in range(1, 4):
            closeup_filename = "%s_closeup_%d.png" % (image, j)
            closeup_name = "%s_closeup_%d" % (image, j)
            if afis_file_exists(closeup_filename):
                setattr(p, "closeup_%d" % j, closeup_name)
        return p

    afis_prints = {}
    for _db_key, (_image, _desc) in DB_PRINT_INFO.items():
        afis_prints[_db_key] = make_afis_print(_image, description=_desc)
    for _db_key, _mcq in DB_PRINT_MCQS.items():
        afis_prints[_db_key].mcq = _mcq

    ## Runtime state for the AFIS terminal.
    afis_active = False        # True only while the terminal is open
    imported_print = None      # key into afis_prints, set by importing evidence
    print_imported = False     # has anything been imported yet this session
    current_db_print = 1       # 1..NUM_DB_PRINTS, which database card is shown
    afis_import_keys = []      # keys of every importable print discovered this visit
    _compare_left_img = None   # currently-shown image in the compare view's left slot
    _compare_right_img = None  # currently-shown image in the compare view's right slot

    def is_print_evidence(item):
        name_lower = item.name.lower()
        return any(k in name_lower for k in PRINT_NAME_KEYWORDS)

    def get_print_evidence_items():
        """All collected evidence items that look like fingerprints."""
        return [item for item in evidence._inventory if is_print_evidence(item)]

    def slugify_print_key(name):
        cleaned = "".join(c if c.isalnum() else "_" for c in name.lower()).strip("_")
        return "print_evidence_%s" % cleaned

    def resolve_print_source(item):
        """Decides which database card (and therefore whose scores/image)
        an evidence item's print should be treated as, based on a keyword
        in its name. Falls through to PRINT_SOURCE_DEFAULT_DB_KEY."""
        name_lower = item.name.lower()
        for keyword, db_key in PRINT_SOURCE_RULES:
            if keyword in name_lower:
                return db_key
        return PRINT_SOURCE_DEFAULT_DB_KEY

    def register_importable_print(item):
        """Ensures there's an AfisPrint entry for this evidence item, and
        returns its key. Safe to call repeatedly -- won't wipe out a card
        that's already been processed."""
        key = slugify_print_key(item.name)
        if key not in afis_prints:
            source_db_key = resolve_print_source(item)
            default_image = DB_PRINT_INFO[source_db_key][0]
            default_scores = OWNER_SOURCE_SCORES if source_db_key == ELIMINATION_PRINT_KEY else ROBBER_SOURCE_SCORES
            image = PRINT_EVIDENCE_IMAGES.get(item.name, default_image)
            afis_prints[key] = make_afis_print(
                image,
                description="The %s." % item.name.lower(),
                scores=dict(default_scores),
            )
        return key

    def make_afis_import_action(print_key):
        """Wired onto an evidence item's .action while the AFIS terminal is
        open, so clicking 'Use' on it in the inventory imports it."""
        def _action():
            global imported_print, print_imported
            if not afis_active:
                renpy.notify("Take this to the AFIS terminal first.")
                return
            if afis_prints[print_key].processed:
                renpy.notify("We've already identified this print.")
                return
            imported_print = print_key
            print_imported = True
            renpy.hide_screen("inventory")
            renpy.jump("afis_import_print")
        return _action


################################################################################
## AFIS screens
################################################################################

screen afis():
    modal True
    add Solid("#000c")

    frame:
        xalign 0.5
        yalign 0.5
        xpadding 60
        ypadding 40
        background Frame("gui/frame.png", gui.frame_borders, tile=False)

        vbox:
            spacing 20
            xalign 0.5

            text "AFIS: Automated Fingerprint Identification System" size 38 xalign 0.5

            hbox:
                xalign 0.5
                spacing 90

                vbox:
                    xalign 0.5
                    spacing 10
                    text "Imported Print" size 24 xalign 0.5
                    frame:
                        xsize 260
                        ysize 350
                        background Solid("#111")
                        if print_imported:
                            add afis_prints[imported_print].image:
                                xalign 0.5
                                yalign 0.5
                                zoom 0.6
                        else:
                            text "No print imported" xalign 0.5 yalign 0.5 size 20

                vbox:
                    xalign 0.5
                    spacing 10
                    text "Database Record [current_db_print]/[NUM_DB_PRINTS]" size 24 xalign 0.5
                    frame:
                        xsize 260
                        ysize 350
                        background Solid("#111")
                        add afis_prints["print_%d" % current_db_print].image:
                            xalign 0.5
                            yalign 0.5
                            zoom 0.6

            hbox:
                xalign 0.5
                spacing 30

                textbutton "Import" action ToggleScreen("inventory")
                textbutton "Prev" action Jump("afis_show_prev") sensitive print_imported
                textbutton "Next" action Jump("afis_show_next") sensitive print_imported
                textbutton "Compare" action Jump("afis_compare") sensitive print_imported
                textbutton "Back to Lab" action Jump("afis_exit")


screen afis_analyzing():
    frame:
        xalign 0.5
        yalign 0.85
        background Frame("gui/frame.png", gui.frame_borders, tile=False)
        text "Analyzing..." size 34


screen afis_compare_view():
    ## Used for both the import reveal and the closeup zoom-through during
    ## Compare -- same dark backdrop + gui frame as the main afis() screen,
    ## so nothing ever just floats loose on the bare background.
    zorder 60
    add Solid("#000c")
    frame:
        xalign 0.5
        yalign 0.5
        xpadding 60
        ypadding 40
        background Frame("gui/frame.png", gui.frame_borders, tile=False)

        hbox:
            xalign 0.5
            spacing 90

            vbox:
                xalign 0.5
                spacing 10
                text "Imported Print" size 24 xalign 0.5
                frame:
                    xsize 300
                    ysize 400
                    background Solid("#111")
                    if _compare_left_img:
                        add _compare_left_img:
                            xalign 0.5
                            yalign 0.5
                            xsize 280
                            ysize 380
                            fit "contain"

            vbox:
                xalign 0.5
                spacing 10
                text "Database Record" size 24 xalign 0.5
                frame:
                    xsize 300
                    ysize 400
                    background Solid("#111")
                    if _compare_right_img:
                        add _compare_right_img:
                            xalign 0.5
                            yalign 0.5
                            xsize 280
                            ysize 380
                            fit "contain"


screen afis_quiz_images():
    ## Used only during the pattern-matching quiz -- deliberately NO dark
    ## backdrop and NO frame here, since the full afis_compare_view was
    ## covering the question text. Negative zorder keeps this behind the
    ## dialogue box and menu choices, but it still renders above the base
    ## scene since screens always sit above the master layer.
    ##
    ## Just the database record, single and large -- that's the print the
    ## question is actually asking about, so no need for the imported
    ## print alongside it here.
    zorder -5
    if _compare_right_img:
        add _compare_right_img:
            xalign 0.5
            yalign 0.4
            xsize 420
            ysize 560
            fit "contain"


################################################################################
## AFIS labels
################################################################################

label lab_fingerprint_station:
    $ afis_active = True
    $ current_db_print = 1
    hide afis_print_l
    hide afis_print_r
    show nina thinknote1 at right
    $ _print_items = get_print_evidence_items()
    if not _print_items:
        n "The automated fingerprint identification system (AFIS) requires a high-resolution digitized input file. We cannot run a database query until the scene processing is finalized."
        jump afis_exit
    $ afis_import_keys = []
    python:
        for _item in _print_items:
            _key = register_importable_print(_item)
            _item.usable = True
            _item.action = make_afis_import_action(_key)
            afis_import_keys.append(_key)
    call screen afis


label afis_exit:
    $ afis_active = False
    hide afis_print_l
    hide afis_print_r
    hide nina with dissolve
    jump lab_hub_loop


label afis_import_print:
    call screen afis


label afis_show_prev:
    $ current_db_print = NUM_DB_PRINTS if current_db_print <= 1 else current_db_print - 1
    call screen afis


label afis_show_next:
    $ current_db_print = 1 if current_db_print >= NUM_DB_PRINTS else current_db_print + 1
    call screen afis


label afis_compare:
    show screen afis_analyzing
    $ _db_key = "print_%d" % current_db_print
    $ _left = afis_prints[imported_print]
    $ _right = afis_prints[_db_key]
    $ _left_shots = [_left.closeup_1, _left.closeup_2, _left.closeup_3, _left.image]
    $ _right_shots = [_right.closeup_1, _right.closeup_2, _right.closeup_3, _right.image]
    show screen afis_compare_view
    python:
        for _m in range(4):
            _compare_left_img = _left_shots[_m] if _left_shots[_m] else _left.image
            _compare_right_img = _right_shots[_m] if _right_shots[_m] else _right.image
            renpy.restart_interaction()
            renpy.pause(0.6)
    hide screen afis_analyzing
    hide screen afis_compare_view
    show screen afis_quiz_images
    jump afis_quiz


label afis_quiz:
    $ _quiz = afis_prints[_db_key].mcq
    if _quiz is None:
        jump afis_show_results
    python:
        renpy.say(n, _quiz.question)
        _quiz_choice = renpy.display_menu(_quiz.items())
        for _quiz_line in _quiz.responses[_quiz_choice]:
            renpy.say(n, _quiz_line)
        _quiz_correct = _quiz.is_correct(_quiz_choice)
    if _quiz_correct:
        jump afis_show_results
    else:
        jump afis_quiz


label afis_show_results:
    hide screen afis_quiz_images
    $ is_match, score = afis_prints[imported_print].scores[_db_key]
    n "[score]% consistency."

    if is_match:
        $ lab_fingerprint_done = True
        $ afis_prints[imported_print].process()
        n "Search complete. The AFIS algorithm reports an optimal minutiae configuration match."
        n "Confirming match. The minutiae points match a record within our active database: [afis_prints[_db_key].description]."
    else:
        if _db_key == ELIMINATION_PRINT_KEY:
            n "Search concluded. The configuration returned no corresponding profiles within the repository: [afis_prints[_db_key].description]."
            n "This exclusion is forensically valuable. It confirms the latent print does not belong to the victim, [_owner_name]."
        else:
            n "No matching fingerprint records identified within the database."

    call screen afis
