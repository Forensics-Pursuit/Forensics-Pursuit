init python:
    # To-Do List
    style.strikethrough_text = Style(style.default)
    style.strikethrough_text.strikethrough = True
    style.strikethrough_text.color = "#888"
    style.strikethrough_text.size = 20

    # Heading
    style.heading_text = Style(style.default)
    style.heading_text.size = 30
    style.heading_text.bold = True

    # Instructions
    style.instructions_text = Style(style.default)
    style.instructions_text.color = "#242424"
    style.instructions_text.size = 20
    style.instructions_strikethrough_text = Style(style.default)
    style.instructions_strikethrough_text.strikethrough = True
    style.instructions_strikethrough_text.color = "#888"
    style.instructions_strikethrough_text.size = 15