from langchain_ollama import OllamaLLM

llm = OllamaLLM(model="llama3", num_predict=250, temperature=0.7)

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

            prompt = f"""As a PCI DSS security analyst, analyze this credit card exposure:

File: {file_path}
Card: {card[:4]}****{card[-4:]}

Provide concise analysis:

**File Type**: Identify the file type (log/config/backup/data)

**Security Status**: Plaintext or encrypted? Production or test environment?

**PCI DSS Violation**: Which requirements are violated?

**Remediation**: Key actions needed to secure this data

Keep response under 150 words, be direct and actionable."""

            try:
                response = llm.invoke(prompt)
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
