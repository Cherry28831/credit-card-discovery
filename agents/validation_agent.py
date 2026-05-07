from tools.luhn_tool import luhn_check


def validation_agent(state):
    print("  [3/6] Validation: Running Luhn algorithm...", flush=True)
    valid = []

    for file, cards in state["potential_cards"].items():
        for card_data in cards:
            # Handle both dict and string formats
            if isinstance(card_data, dict):
                card = card_data.get("card")
                card_format = card_data.get("format", "standard")
            else:
                card = card_data
                card_format = "standard"
            
            if luhn_check(card):
                valid.append({
                    "file": file, 
                    "card_number": card,
                    "format": card_format
                })

    state["valid_cards"] = valid
    print(f"  > Validated {len(valid)} real cards", flush=True)
    return state
