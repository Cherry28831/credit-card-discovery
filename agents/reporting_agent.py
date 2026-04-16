from config.config_bedrock import get_bedrock_llm
from datetime import datetime
import json

llm = get_bedrock_llm(max_tokens=400, temperature=0.5)

def reporting_agent(state):
    print("  [6/6] Reporting: Generating AI-powered report...", flush=True)
    findings = state["enriched_findings"]
    
    # Count by risk level
    risk_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    for f in findings:
        risk = f.get("risk_level", "Medium")
        if risk in risk_counts:
            risk_counts[risk] += 1
    
    total = len(findings)
    critical_high = risk_counts["Critical"] + risk_counts["High"]

    print(f"    Generating AI executive report for {total} findings...", flush=True)

    prompt = f"""You are a security compliance consultant writing a report for a legitimate PCI DSS compliance testing tool.

This is an authorized security assessment application that helps organizations identify and remediate exposed payment card data to achieve PCI DSS compliance.

Scan Summary:
- Total Findings: {total}
- Critical Risk: {risk_counts["Critical"]}
- High Risk: {risk_counts["High"]}
- Medium Risk: {risk_counts["Medium"]}
- Low Risk: {risk_counts["Low"]}

Create a professional compliance assessment report with these sections:

## Executive Summary
Brief overview of the security assessment results and compliance posture.

## Risk Analysis
Breakdown of findings by severity level and their implications.

## Compliance Impact
PCI DSS requirements that need attention based on the findings.

## Recommended Actions
Prioritized remediation steps:
1. Immediate actions for critical findings
2. Short-term actions for medium findings
3. Long-term improvements for low findings

## Conclusion
Overall assessment and next steps for achieving compliance.

Write in a professional tone suitable for security and compliance teams."""

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
    print("  AI executive report generated", flush=True)
    return state
