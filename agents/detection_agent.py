from tools.presidio_tool import detect_credit_cards
from tools.cardholder_data_tool import detect_all_cardholder_data, format_cardholder_data_summary


def detection_agent(state):
    print("  [2/6] Detection: Running Presidio (this may take 30s on first run)...", flush=True)
    potential = {}
    cardholder_data = {}

    for file, text in state["raw_text"].items():
        # Detect credit cards
        results = detect_credit_cards(text)
        cards = [r for r in results if r["score"] > 0.5]
        if cards:
            potential[file] = cards
        
        # Detect additional cardholder data (CVV, expiry, names, etc.)
        ch_data = detect_all_cardholder_data(text)
        if ch_data["has_sensitive_data"]:
            cardholder_data[file] = ch_data

    state["potential_cards"] = potential
    state["cardholder_data"] = cardholder_data
    
    total_cards = sum(len(v) for v in potential.values())
    total_ch_data = sum(ch["total_count"] for ch in cardholder_data.values())
    
    print(f"  > Detected {total_cards} potential cards", flush=True)
    if total_ch_data > 0:
        print(f"  > Detected {total_ch_data} additional cardholder data items", flush=True)
    
    return state
