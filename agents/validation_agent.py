from tools.luhn_tool import luhn_check


def validation_agent(state):
    print("  [3/6] Validation: Running Luhn algorithm...", flush=True)
    valid = []

    for file, cards in state["potential_cards"].items():
        for card in cards:
            if luhn_check(card):
                valid.append({"file": file, "card_number": card})

    state["valid_cards"] = valid
    print(f"  > Validated {len(valid)} real cards", flush=True)
    return state
