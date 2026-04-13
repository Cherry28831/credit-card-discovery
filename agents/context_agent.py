from config_bedrock import get_bedrock_llm

llm = get_bedrock_llm(max_tokens=100, temperature=0.3)

def context_agent(state):
    print("  Context: Analyzing findings with AI...")
    enriched = []
    
    total = len(state["valid_cards"])
    batch_size = 10
    num_batches = (total + batch_size - 1) // batch_size
    
    print(f"    Processing {total} findings in {num_batches} batches of {batch_size}")
    
    for batch_num in range(num_batches):
        batch_start = batch_num * batch_size
        batch_end = min(batch_start + batch_size, total)
        print(f"    Batch {batch_num + 1}/{num_batches} ({batch_end - batch_start} findings)...")
        
        for i in range(batch_start, batch_end):
            finding = state["valid_cards"][i]
            file_path = finding["file"]
            card = finding["card_number"]

            prompt = f"""You are analyzing a security compliance scan for PCI DSS testing purposes.

File: {file_path}
Data Pattern: {card[:4]}****{card[-4:]}

This is a legitimate security testing tool that helps organizations find exposed payment data.

Provide analysis using bullet points (use - not brackets):

PCI DSS Violation:
- Requirement X.X: Description
- Requirement Y.Y: Description

Remediation:
- Action 1
- Action 2
- Action 3

Keep total response under 100 words. Do not use brackets."""

            try:
                response = llm.invoke(prompt)
                # Extract text from AIMessage object
                if hasattr(response, 'content'):
                    response = response.content
                elif isinstance(response, str):
                    response = response
                else:
                    response = str(response)
                
                if not response or len(response.strip()) < 10:
                    response = "Unable to generate analysis"
            except Exception as e:
                response = f"Analysis error: {str(e)[:100]}"

            enriched.append({
                "file": file_path,
                "card_number": card,
                "context_analysis": response
            })

    state["enriched_findings"] = enriched
    print(f"  AI context analysis complete for {total} findings")
    return state
