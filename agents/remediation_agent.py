def remediation_agent(state):
    print("  [6/6] Remediation: Auto-masking paused by user...")
    masked_count = 0
    
    for item in state["enriched_findings"]:
        if item["risk_level"] == "Critical":
            # Disabled actual file writing to preserve test data
            item["remediation"] = "Remediation paused"
            
    print("  ✓ Remediation skipped")
    return state
