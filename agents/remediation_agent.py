def remediation_agent(state):
    print("  [6/6] Remediation: Auto-masking critical findings...")
    masked_count = 0
    
    for item in state["enriched_findings"]:
        if item["risk_level"] == "Critical":
            file_path = item["file"]
            card = item["card_number"]
            
            try:
                with open(file_path, "r") as f:
                    content = f.read()
                
                masked = content.replace(card, "****" + card[-4:])
                
                with open(file_path, "w") as f:
                    f.write(masked)
                
                item["remediation"] = "Card masked successfully"
                masked_count += 1
            
            except Exception as e:
                item["remediation"] = f"Remediation failed: {str(e)}"
    
    print(f"  ✓ Masked {masked_count} critical findings")
    return state
