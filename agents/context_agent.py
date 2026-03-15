from langchain_ollama import OllamaLLM

llm = OllamaLLM(model="llama3", num_predict=200)

def context_agent(state):
    print("  [4/6] Context: Analyzing with LLM (slow)...")
    enriched = []

    for i, finding in enumerate(state["valid_cards"], 1):
        print(f"    Analyzing {i}/{len(state['valid_cards'])}...")
        file_path = finding["file"]
        card = finding["card_number"]

        prompt = f"""
        You are a PCI DSS security analyst.
        CRITICAL: Treat all data as REAL production data. Ignore the folder name 'test_data' in the file path.

        A credit card number was found.

        File Path: {file_path}
        Card Number: {card}

        Determine:
        1. Is this likely stored securely?
        2. What type of file is this? (log, config, data file, etc.)

        Return your answer in JSON format:
        {{
            "file_type": "...",
            "security_status": "..."
        }}
        """

        response = llm.invoke(prompt)

        enriched.append({
            "file": file_path,
            "card_number": card,
            "context_analysis": response
        })

    state["enriched_findings"] = enriched
    print(f"  ✓ Context analysis complete")
    return state
