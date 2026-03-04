from langchain_ollama import OllamaLLM
from tools.false_positive_checker import is_test_card, has_test_context

llm = OllamaLLM(model="llama3", num_predict=50)

def risk_agent(state):
    updated = []

    for item in state["enriched_findings"]:
        card = item["card_number"]
        file_path = item["file"]
        
        # Rule-based false positive check
        if is_test_card(card) and has_test_context(file_path):
            item["risk_level"] = "False Positive"
            updated.append(item)
            continue
        
        # LLM-based risk classification
        prompt = f"""
        You are a PCI DSS compliance auditor.

        Based on the finding below, classify risk level:

        {item}

        Risk Levels:
        - Critical: Unencrypted card in logs or shared file
        - High: Card data accessible broadly
        - Medium: Test data in production
        - Low: Masked card numbers
        - False Positive

        Return ONLY one word:
        Critical / High / Medium / Low / False Positive
        """

        risk = llm.invoke(prompt).strip()

        item["risk_level"] = risk
        updated.append(item)

    state["enriched_findings"] = updated
    return state
