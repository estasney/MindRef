KBD_PATTERN = "(?:<kbd>)(.+?)(?:</kbd>)"


def parse_kbd(inline, m, state):
    text = m.group(1)
    return "kbd", text


def plugin_kbd(md):
    md.inline.register_rule("kbd", KBD_PATTERN, parse_kbd)
    md.inline.rules.insert(1, "kbd")

    if md.renderer.NAME == "ast":
        md.renderer.register("kbd", lambda x: {"type": "kbd", "text": x})
