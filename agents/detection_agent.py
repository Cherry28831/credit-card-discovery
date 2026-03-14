from tools.presidio_tool import detect_credit_cards


def detection_agent(state):
    print("  [2/6] Detection: Running Presidio (this may take 30s on first run)...")
    potential = {}

    for file, text in state["raw_text"].items():
        results = detect_credit_cards(text)
        cards = [r["card"] for r in results if r["score"] > 0.5]
        if cards:
            potential[file] = cards

    state["potential_cards"] = potential
    print(f"  ✓ Detected {sum(len(v) for v in potential.values())} potential cards")
    return state
