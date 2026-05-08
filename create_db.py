"""
Create SQLite database from findings.json for dashboard
"""
import sqlite3
import json
import os
from datetime import datetime

def create_database():
    # Check if findings.json exists
    if not os.path.exists("outputs/findings.json"):
        print("No findings.json found. Run main.py first.")
        return
    
    # Load findings
    with open("outputs/findings.json", "r", encoding="utf-8") as f:
        findings = json.load(f)
    
    if not findings:
        print("No findings to import.")
        return
    
    # Create database
    conn = sqlite3.connect("outputs/findings.db")
    cursor = conn.cursor()
    
    # Create table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS findings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file TEXT,
            card_number TEXT,
            risk_level TEXT,
            context_analysis TEXT,
            scan_date TEXT,
            cardholder_data TEXT
        )
    """)
    
    # Check for duplicates and only insert new findings
    existing_cards = set()
    cursor.execute("SELECT file, card_number FROM findings")
    for row in cursor.fetchall():
        existing_cards.add((row[0], row[1]))
    
    # Insert only new findings
    scan_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_count = 0
    for finding in findings:
        file_path = finding.get("file", "")
        card_num = finding.get("card_number", "")
        
        # Skip if already exists
        if (file_path, card_num) in existing_cards:
            continue
        
        # Serialize cardholder data if present
        ch_data = finding.get("cardholder_data", {})
        ch_data_json = json.dumps(ch_data) if ch_data else ""
        
        cursor.execute("""
            INSERT INTO findings (file, card_number, risk_level, context_analysis, scan_date, cardholder_data)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            file_path,
            card_num,
            finding.get("risk_level", "Medium"),
            finding.get("context_analysis", ""),
            scan_date,
            ch_data_json
        ))
        new_count += 1
    
    conn.commit()
    conn.close()
    
    total_in_db = len(existing_cards) + new_count
    print(f"Database updated: outputs/findings.db")
    print(f"Added {new_count} new findings (Total: {total_in_db})")

if __name__ == "__main__":
    create_database()
