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
            scan_date TEXT
        )
    """)
    
    # Clear existing data
    cursor.execute("DELETE FROM findings")
    
    # Insert findings
    scan_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for finding in findings:
        cursor.execute("""
            INSERT INTO findings (file, card_number, risk_level, context_analysis, scan_date)
            VALUES (?, ?, ?, ?, ?)
        """, (
            finding.get("file", ""),
            finding.get("card_number", ""),
            finding.get("risk_level", "Medium"),
            finding.get("context_analysis", ""),
            scan_date
        ))
    
    conn.commit()
    conn.close()
    
    print(f"Database created: outputs/findings.db")
    print(f"Imported {len(findings)} findings")

if __name__ == "__main__":
    create_database()
