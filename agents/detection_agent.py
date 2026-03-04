from tools.regex_tool import find_card_patterns


def detection_agent(state):
    potential = {}

    for file, text in state["raw_text"].items():
        matches = find_card_patterns(text)
        if matches:
            potential[file] = matches

    state["potential_cards"] = potential
    return state
