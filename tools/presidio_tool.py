from presidio_analyzer import AnalyzerEngine, PatternRecognizer
from presidio_analyzer.nlp_engine import NlpEngineProvider
import re

provider = NlpEngineProvider(nlp_configuration={"nlp_engine_name": "spacy", "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}]})
nlp_engine = provider.create_engine()
analyzer = AnalyzerEngine(nlp_engine=nlp_engine)

def detect_credit_cards(text):
    # Standard Presidio detection
    results = analyzer.analyze(
        text=text,
        entities=["CREDIT_CARD"],
        language="en"
    )
    
    findings = []
    for result in results:
        card = text[result.start:result.end]
        findings.append({
            "card": card.replace("-", "").replace(" ", "").replace("\n", ""),
            "score": result.score,
            "format": "standard"
        })
    
    # Detect vertical numbers (newline separated) - support 13-19 digits
    vertical_pattern = r'(\d\s*\n\s*){12,18}\d'
    for match in re.finditer(vertical_pattern, text):
        card_str = match.group()
        card_digits = re.sub(r'\D', '', card_str)
        if len(card_digits) >= 13 and len(card_digits) <= 19:
            # Check if not already found
            if not any(f['card'] == card_digits for f in findings):
                findings.append({
                    "card": card_digits,
                    "score": 0.7,
                    "format": "vertical"
                })
    
    # Detect various credit card formats with spaces/dashes
    # 4-4-4-4, 4-6-5, 4-4-4-4-3, etc.
    flexible_pattern = r'\b(\d{4})[\s-]+(\d{4})[\s-]+(\d{4})[\s-]+(\d{4,7})\b'
    for match in re.finditer(flexible_pattern, text):
        card_str = match.group()
        card_digits = re.sub(r'\D', '', card_str)
        if len(card_digits) >= 13 and len(card_digits) <= 19:
            if not any(f['card'] == card_digits for f in findings):
                findings.append({
                    "card": card_digits,
                    "score": 0.65,
                    "format": "spaced"
                })
    
    # Additional pattern for continuous digits that Presidio might miss
    # Matches 13-19 consecutive digits
    continuous_pattern = r'\b\d{13,19}\b'
    for match in re.finditer(continuous_pattern, text):
        card_digits = match.group()
        if not any(f['card'] == card_digits for f in findings):
            findings.append({
                "card": card_digits,
                "score": 0.6,
                "format": "standard"
            })
    
    return findings
