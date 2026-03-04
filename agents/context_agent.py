from langchain_ollama import OllamaLLM

llm = OllamaLLM(model="llama3", num_predict=200)

def context_agent(state):
    enriched = []

    for finding in state["valid_cards"]:
        file_path = finding["file"]
        card = finding["card_number"]

        prompt = f"""
        You are a PCI DSS security analyst.

        A credit card number was found.

        File Path: {file_path}
        Card Number: {card}

        Determine:
        1. Is this likely production data or test data?
        2. Is this likely stored securely?
        3. What type of file is this? (log, config, data file, etc.)

        Return your answer in JSON format:
        {{
            "environment": "...",
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
    return state
