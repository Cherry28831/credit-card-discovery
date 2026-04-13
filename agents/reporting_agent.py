from config.config_bedrock import get_bedrock_llm
from datetime import datetime
import json

llm = get_bedrock_llm(max_tokens=400, temperature=0.5)

def reporting_agent(state):
    print("  Reporting: Generating AI-powered report...")
    findings = state["enriched_findings"]
    
    # Count by risk level
    risk_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    for f in findings:
        risk = f.get("risk_level", "Medium")
        if risk in risk_counts:
            risk_counts[risk] += 1
    
    total = len(findings)
    critical_high = risk_counts["Critical"] + risk_counts["High"]

    print(f"    Generating AI executive report for {total} findings...")

    prompt = f"""Generate a professional PCI DSS compliance security report for a security testing application.

This system scans for exposed credit card data to help organizations identify compliance risks.

Scan Results:
- Total Findings: {total}
- Critical Risk: {risk_counts["Critical"]}
- High Risk: {risk_counts["High"]}
- Medium Risk: {risk_counts["Medium"]}
- Low Risk: {risk_counts["Low"]}

Sample Critical Findings:
{json.dumps([f for f in findings if f.get('risk_level') == 'Critical'][:2], indent=2)}

Create an executive report with:

## Executive Summary
3-4 sentences on security posture and key concerns.

## Risk Analysis
Breakdown by severity with specific concerns.

## Critical Issues
Detailed analysis of severe findings and impact.

## Compliance Impact
PCI DSS requirements affected and consequences.

## Recommended Actions
Prioritized remediation:
1. Immediate (Critical/High)
2. Short-term (Medium)
3. Long-term (Low)

## Conclusion
Overall assessment and next steps.

Write professionally for executive and technical audiences."""

    try:
        response = llm.invoke(prompt)
        # Extract text from AIMessage object
        if hasattr(response, 'content'):
            report_body = response.content
        else:
            report_body = str(response)
    except:
        report_body = "Report generation failed. Please review findings manually."
    
    # Build full report
    full_report = f"""# Credit Card Data Discovery - Security Report

**Scan Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total Findings:** {total}
**Critical/High Risk:** {critical_high}

---

## Overview

| Risk Level | Count | Percentage |
|------------|-------|------------|
| Critical   | {risk_counts['Critical']} | {risk_counts['Critical']/total*100:.1f}% |
| High       | {risk_counts['High']} | {risk_counts['High']/total*100:.1f}% |
| Medium     | {risk_counts['Medium']} | {risk_counts['Medium']/total*100:.1f}% |
| Low        | {risk_counts['Low']} | {risk_counts['Low']/total*100:.1f}% |

---

{report_body}

---

## Detailed Findings

"""
    
    # Add findings details
    for i, f in enumerate(findings, 1):
        full_report += f"""\n### Finding #{i} - {f.get('risk_level', 'Unknown')} Risk

**File:** `{f['file']}`  
**Card:** `{f['card_number'][:4]}****{f['card_number'][-4:]}`  
**Risk Level:** {f.get('risk_level', 'Unknown')}

**Analysis:**
{f.get('context_analysis', 'No analysis available')[:500]}...

---
"""

    state["report"] = full_report
    print("  AI executive report generated")
    return state
