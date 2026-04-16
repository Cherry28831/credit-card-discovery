import json
import subprocess
import os
import sys
from agents.discovery_agent import discovery_agent
from agents.detection_agent import detection_agent
from agents.validation_agent import validation_agent
from agents.context_agent import context_agent
from agents.risk_agent import risk_agent
from agents.reporting_agent import reporting_agent

def print_flush(msg):
    """Print with immediate flush for real-time output"""
    print(msg, flush=True)

def run_pipeline(folder_path="sample_files"):
    """Run the credit card discovery pipeline"""
    
    state = {
        "folder_path": folder_path,
        "files": [],
        "raw_text": {},
        "potential_cards": {},
        "valid_cards": [],
        "enriched_findings": [],
        "report": "",
    }
    
    # Execute pipeline sequentially
    print_flush("[1/6] Discovery: Scanning files...")
    state = discovery_agent(state)
    
    print_flush("[2/6] Detection: Finding potential cards...")
    state = detection_agent(state)
    
    print_flush("[3/6] Validation: Checking card validity...")
    state = validation_agent(state)
    
    print_flush("[4/6] Context: AI analysis...")
    state = context_agent(state)
    
    print_flush("[5/6] Risk: Classification...")
    state = risk_agent(state)
    
    print_flush("[6/6] Reporting: Generating report...")
    state = reporting_agent(state)
    
    return state

if __name__ == "__main__":
    print_flush("Starting Autonomous Compliance System...")
    
    # Check for command line argument
    if len(sys.argv) > 1:
        scan_path = sys.argv[1]
        print_flush(f"Scanning custom path: {scan_path}")
    else:
        scan_path = "sample_files"
        print_flush("Scanning sample_files folder...")
    
    final_state = run_pipeline(scan_path)

    # Ensure outputs directory exists
    os.makedirs("outputs", exist_ok=True)
    
    print_flush("Saving findings...")
    with open("outputs/findings.json", "w", encoding="utf-8") as f:
        json.dump(final_state["enriched_findings"], f, indent=4, ensure_ascii=False)
    
    with open("outputs/report.txt", "w", encoding="utf-8") as f:
        f.write(final_state["report"])
    
    print_flush("\nReport generated: outputs/report.txt")
    print_flush("Findings saved: outputs/findings.json")
    print_flush(f"Total findings: {len(final_state['enriched_findings'])}")
    
    # Auto-create database for dashboard
    if len(final_state['enriched_findings']) > 0:
        print_flush("\nCreating dashboard database...")
        try:
            result = subprocess.run(["python", "create_db.py"], 
                                  capture_output=True, text=True, cwd=os.getcwd())
            if result.returncode == 0:
                print_flush("Database created successfully")
                print_flush("\nNext steps:")
                print_flush("   1. Run: py -m streamlit run dashboard.py")
                print_flush("   2. Or use: start_dashboard.bat")
                print_flush("   3. Dashboard will open at: http://localhost:8501")
            else:
                print_flush("Database creation failed. Run manually: python create_db.py")
        except Exception as e:
            print_flush(f"Could not auto-create database: {e}")
            print_flush("   Run manually: python create_db.py")
            print_flush("   Then: py -m streamlit run dashboard.py")
    else:
        print_flush("\nNo findings detected. Check your test data.")