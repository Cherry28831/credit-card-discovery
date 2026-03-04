from langchain_ollama import OllamaLLM

llm = OllamaLLM(model="llama3", num_predict=600)


def reporting_agent(state):
    findings = state["enriched_findings"]
    
    # Count by risk level
    risk_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0, "False Positive": 0}
    for f in findings:
        risk = f.get("risk_level", "Unknown")
        if risk in risk_counts:
            risk_counts[risk] += 1
    
    total = len(findings)
    critical_high = risk_counts["Critical"] + risk_counts["High"]

    prompt = f"""
    Generate a professional PCI DSS compliance security report.

    Total Findings: {total}
    Critical: {risk_counts["Critical"]}
    High: {risk_counts["High"]}
    Medium: {risk_counts["Medium"]}
    Low: {risk_counts["Low"]}
    False Positives: {risk_counts["False Positive"]}

    Sample Findings:
    {findings[:3]}

    Create a report with:
    1. Executive Summary (2-3 sentences about the scan results)
    2. Risk Summary (breakdown by severity)
    3. Key Findings (highlight critical/high risks)
    4. Recommendations (specific actions to take)
    5. Compliance Status (PCI DSS implications)
    
    Keep it concise and actionable.
    """

    report = llm.invoke(prompt)
    
    # Add header
    full_report = f"""# Credit Card Data Discovery - Security Report

**Scan Date:** {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total Findings:** {total}
**Critical/High Risk:** {critical_high}

---

{report}

---

## Detailed Findings

"""
    
    # Add findings table
    for i, f in enumerate(findings, 1):
        full_report += f"""\n### Finding #{i}
- **File:** `{f['file']}`
- **Card:** `{f['card_number'][:4]}****{f['card_number'][-4:]}`
- **Risk Level:** {f.get('risk_level', 'Unknown')}
- **Context:** {f.get('context_analysis', 'N/A')[:100]}...

"""

    state["report"] = full_report
    return state
