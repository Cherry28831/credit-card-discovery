from presidio_analyzer import AnalyzerEngine, PatternRecognizer
from presidio_analyzer.nlp_engine import NlpEngineProvider
import re

provider = NlpEngineProvider(nlp_configuration={"nlp_engine_name": "spacy", "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}]})
nlp_engine = provider.create_engine()
analyzer = AnalyzerEngine(nlp_engine=nlp_engine)

def detect_credit_cards(text):
    results = analyzer.analyze(
        text=text,
        entities=["CREDIT_CARD"],
        language="en"
    )
    
    findings = []
    for result in results:
        card = text[result.start:result.end]
        findings.append({
            "card": card.replace("-", "").replace(" ", ""),
            "score": result.score
        })
    
    return findings
