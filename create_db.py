import json
import sqlite3
from datetime import datetime

# Load findings
with open("outputs/findings.json", "r") as f:
    findings = json.load(f)

# Create SQLite database
conn = sqlite3.connect("outputs/findings.db")
cursor = conn.cursor()

# Create table
cursor.execute("""
CREATE TABLE IF NOT EXISTS findings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file TEXT,
    card_number TEXT,
    risk_level TEXT,
    remediation TEXT,
    scan_date TEXT,
    context_analysis TEXT,
    UNIQUE(file, card_number)
)
""")

# Insert or replace findings (keeps existing + adds new)
for finding in findings:
    cursor.execute("""
        INSERT OR REPLACE INTO findings (file, card_number, risk_level, remediation, scan_date, context_analysis)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        finding.get("file", ""),
        finding.get("card_number", ""),
        finding.get("risk_level", "Unknown"),
        finding.get("remediation", "Pending"),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        finding.get("context_analysis", "No context provided.")
    ))

conn.commit()
conn.close()

print("SQLite database created: outputs/findings.db")
print("\nNext steps:")
print("1. Run: install_dashboard.bat (First time only)")
print("2. Run: start_dashboard.bat")
