################################################################################
## Lab hub
################################################################################

label scene_lab:
    scene lab_hallway with fade
    $ lab_fingerprint_done = False
    $ lab_dna_done = False
    $ dna_reset()
    $ gloves_worn = False
    show nina normal1 at right with moveinright
    n "Welcome to the lab. Now we let the physical evidence tell the story."
    n "Take the latent print card over to the Data Analysis desk for AFIS scanning. Then, we'll head to the DNA bench to extract our biological sample."
    hide nina with dissolve
    jump glove_gate_lab

label glove_gate_lab:
    if gloves_worn or not has_gloves_item():
        hide nina with dissolve
        jump lab_hub_loop
    $ _glove_return_label = "glove_gate_lab"
    $ _gloves_item = get_toolbox_item("Gloves")
    if _gloves_item:
        $ _gloves_item.usable = True
    show nina thinknote1 at right
    n "Fresh gloves before we handle anything in here."
    call screen inventory
    jump glove_gate_lab

label lab_hub_loop:
    call screen lab_hub
    jump lab_hub_loop


screen lab_hub():

    ## Data Analysis Lab -> AFIS (fingerprints)
    hbox:
        xpos 0.20 yalign 0.5
        imagebutton:
            idle "data_analysis_lab_idle"
            hover "data_analysis_lab_hover"
            action Jump("lab_fingerprint_station")
            hovered Notify("\u2713 Fingerprint Matched" if lab_fingerprint_done else "Data Analysis Lab")
            unhovered Notify("")

    ## Materials Lab -> DNA bio station (renamed "DNA Analysis Lab" in the
    ## hover tooltip only; the underlying art/asset name stays
    ## "materials_lab" since that's what the files are actually named)
    hbox:
        xpos 0.55 yalign 0.48
        imagebutton:
            idle "materials_lab_idle"
            hover "materials_lab_hover"
            action Jump("dna_lab_entry")
            hovered Notify("\u2713 DNA Matched" if lab_dna_done else "DNA Analysis Lab")
            unhovered Notify("")

    if lab_fingerprint_done and lab_dna_done:
        textbutton "Conclude Case":
            style "custom_button"
            xalign 0.5
            yalign 0.92
            action Jump("lab_conclusion")


################################################################################
## Conclusion
################################################################################

label lab_conclusion:
    scene bg_debrief with dissolve
    show nina thinknote1 at center with dissolve
    n "The forensic data is clear. The fingerprint minutiae from the outside handle and the DNA markers from the cabin lead to one person: [_robber_name], our Pontiac Bandit."
    n "We have undeniable physical proof placing the suspect inside that vehicle. I'm calling the District Attorney to get a felony arrest warrant signed."
    show nina normal1 at center
    n "Excellent protocol work today. The evidence is airtight. Case closed."
    hide nina with dissolve
    return
