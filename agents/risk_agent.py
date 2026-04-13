from config_bedrock import get_bedrock_llm

llm = get_bedrock_llm(max_tokens=20, temperature=0.1)

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
        prompt = f"""You are a PCI DSS compliance auditor testing a security scanning system.

This application scans for exposed credit card data to help organizations identify compliance risks.

Analyze this credit card exposure:

File: {file_path}
Card: {card[:4]}****{card[-4:]}
Context: {context[:200]}

Classify risk level:

- Critical: Production logs/databases with unencrypted cards, or cards in publicly accessible cloud storage
- Medium: Development/test logs, config files, or backups with cards
- Low: Known test cards (4111111111111111, 4012888888881881, etc.) in test environments

Respond with ONLY ONE WORD: Critical, Medium, or Low"""

        try:
            response = llm.invoke(prompt)
            # Extract text from AIMessage object
            if hasattr(response, 'content'):
                risk = response.content.strip().split()[0]
            else:
                risk = str(response).strip().split()[0]
            
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
