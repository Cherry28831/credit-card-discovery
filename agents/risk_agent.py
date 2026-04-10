from langchain_ollama import OllamaLLM

llm = OllamaLLM(model="llama3", num_predict=50)

def risk_agent(state):
    print("  Risk: Classifying findings with AI...")
    updated = []
    total = len(state["enriched_findings"])
    
    # Known test cards
    test_cards = [
        "4111111111111111", "4012888888881881", "5555555555554444",
        "378282246310005", "6011111111111117", "3530111333300000"
    ]

    print(f"    Processing {total} findings individually...")
    
    for idx, item in enumerate(state["enriched_findings"], 1):
        card = item["card_number"]
        file_path = item["file"]
        context = item.get("context_analysis", "")
        
        # Check for test cards in test environments
        if card in test_cards and ("test" in file_path.lower() or "sample" in file_path.lower()):
            item["risk_level"] = "Low"
            updated.append(item)
            continue
        
        # AI-based risk classification
        prompt = f"""You are a PCI DSS compliance auditor.

Analyze this credit card exposure:

File: {file_path}
Card: {card[:4]}****{card[-4:]}
Context: {context[:200]}

Classify risk level:

- Critical: Unencrypted cards in logs or production files
- Medium: Cards in test environments or config files
- Low: Properly masked or tokenized cards

Respond with ONLY ONE WORD: Critical, Medium, or Low"""

        try:
            risk = llm.invoke(prompt).strip().split()[0]
            if risk not in ["Critical", "Medium", "Low"]:
                risk = "Medium"
        except:
            risk = "Medium"
        
        item["risk_level"] = risk
        updated.append(item)
        
        if idx % 5 == 0 or idx == total:
            print(f"    Classified {idx}/{total}...")

    state["enriched_findings"] = updated
    print(f"  Risk classification complete for {total} findings")
    return state
