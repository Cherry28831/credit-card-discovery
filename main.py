import json
from workflow.graph import build_graph

if __name__ == "__main__":
    print("🚀 Starting Autonomous Compliance System...")
    
    graph = build_graph()

    initial_state = {
        "folder_path": "test_data",
        "files": [],
        "raw_text": {},
        "potential_cards": {},
        "valid_cards": [],
        "enriched_findings": [],
        "report": "",
    }

    print("📂 Scanning test_data folder...")
    final_state = graph.invoke(initial_state)

    print("💾 Saving findings...")
    with open("outputs/findings.json", "w") as f:
        json.dump(final_state["enriched_findings"], f, indent=4)
    
    with open("outputs/report.txt", "w") as f:
        f.write(final_state["report"])
    
    print("\n✅ Report generated: outputs/report.txt")
    print("✅ Findings saved: outputs/findings.json")
    print(f"✅ Total findings: {len(final_state['enriched_findings'])}")
