from tools.luhn_tool import luhn_check


def validation_agent(state):
    valid = []

    for file, cards in state["potential_cards"].items():
        for card in cards:
            if luhn_check(card):
                valid.append({"file": file, "card_number": card})

    state["valid_cards"] = valid
    return state
