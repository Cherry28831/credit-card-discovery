import re
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider

# Initialize Presidio for name detection
provider = NlpEngineProvider(nlp_configuration={
    "nlp_engine_name": "spacy", 
    "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}]
})
nlp_engine = provider.create_engine()
analyzer = AnalyzerEngine(nlp_engine=nlp_engine)


def detect_cvv(text):
    """
    Detect CVV/CVC/CVV2/CID codes (3-4 digit security codes)
    CVV patterns:
    - 3 digits for Visa, Mastercard, Discover
    - 4 digits for Amex
    - Often labeled as CVV, CVC, CVV2, CID, Security Code
    """
    findings = []
    
    # Pattern 1: Labeled CVV (e.g., "CVV: 123", "CVC: 456", "Security Code: 789")
    labeled_patterns = [
        r'(?:CVV|CVC|CVV2|CID|Security\s*Code|Card\s*Security\s*Code|CSC)[\s:]*(\d{3,4})\b',
        r'(?:cvv|cvc|cvv2|cid|security\s*code)[\s:]*(\d{3,4})\b',
    ]
    
    for pattern in labeled_patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            cvv = match.group(1)
            context_start = max(0, match.start() - 30)
            context_end = min(len(text), match.end() + 30)
            context = text[context_start:context_end].strip()
            
            findings.append({
                "type": "CVV",
                "value": cvv,
                "confidence": 0.95,
                "context": context,
                "position": match.start()
            })
    
    # Pattern 2: Standalone 3-4 digits near card-related keywords
    # Only flag if near card/payment context to reduce false positives
    card_context_pattern = r'(?:card|payment|credit|debit|visa|mastercard|amex|discover).*?(\d{3,4})\b'
    for match in re.finditer(card_context_pattern, text, re.IGNORECASE):
        cvv = match.group(1)
        # Avoid flagging years, amounts, etc.
        if not re.search(r'(19|20)\d{2}', cvv) and not cvv.startswith('0'):
            context_start = max(0, match.start())
            context_end = min(len(text), match.end() + 20)
            context = text[context_start:context_end].strip()
            
            # Check if not already found
            if not any(f['value'] == cvv and abs(f['position'] - match.start()) < 50 for f in findings):
                findings.append({
                    "type": "CVV",
                    "value": cvv,
                    "confidence": 0.7,
                    "context": context,
                    "position": match.start()
                })
    
    return findings


def detect_expiry_date(text):
    """
    Detect credit card expiry dates
    Common formats:
    - MM/YY, MM/YYYY
    - MM-YY, MM-YYYY
    - MMYY, MMYYYY
    - Labeled: "Exp: 12/25", "Expiry: 01/2025", "Valid Thru: 12/25"
    """
    findings = []
    
    # Pattern 1: Labeled expiry dates
    labeled_patterns = [
        r'(?:Exp(?:iry)?|Valid\s*(?:Thru|Through|Until)|Expires?)[\s:]*(\d{1,2})[/\-](\d{2,4})\b',
        r'(?:exp(?:iry)?|valid\s*(?:thru|through|until)|expires?)[\s:]*(\d{1,2})[/\-](\d{2,4})\b',
    ]
    
    for pattern in labeled_patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            month = match.group(1).zfill(2)
            year = match.group(2)
            
            # Validate month
            if 1 <= int(month) <= 12:
                expiry = f"{month}/{year}"
                context_start = max(0, match.start() - 20)
                context_end = min(len(text), match.end() + 20)
                context = text[context_start:context_end].strip()
                
                findings.append({
                    "type": "EXPIRY_DATE",
                    "value": expiry,
                    "confidence": 0.95,
                    "context": context,
                    "position": match.start()
                })
    
    # Pattern 2: Standalone MM/YY or MM/YYYY near card context
    standalone_pattern = r'\b(\d{1,2})[/\-](\d{2,4})\b'
    for match in re.finditer(standalone_pattern, text):
        month = match.group(1).zfill(2)
        year = match.group(2)
        
        # Validate month and year format
        if 1 <= int(month) <= 12 and len(year) in [2, 4]:
            # Check if near card-related context
            context_start = max(0, match.start() - 50)
            context_end = min(len(text), match.end() + 50)
            context = text[context_start:context_end]
            
            if re.search(r'(?:card|payment|credit|debit|exp|valid)', context, re.IGNORECASE):
                expiry = f"{month}/{year}"
                
                # Check if not already found
                if not any(f['value'] == expiry and abs(f['position'] - match.start()) < 30 for f in findings):
                    findings.append({
                        "type": "EXPIRY_DATE",
                        "value": expiry,
                        "confidence": 0.75,
                        "context": context.strip(),
                        "position": match.start()
                    })
    
    return findings


def detect_cardholder_name(text):
    """
    Detect cardholder names using Presidio NER
    Looks for PERSON entities near card-related keywords
    """
    findings = []
    
    # Use Presidio to detect person names
    results = analyzer.analyze(
        text=text,
        entities=["PERSON"],
        language="en"
    )
    
    for result in results:
        name = text[result.start:result.end].strip()
        
        # Get context around the name
        context_start = max(0, result.start - 50)
        context_end = min(len(text), result.end + 50)
        context = text[context_start:context_end]
        
        # Check if near card-related keywords
        card_keywords = r'(?:card\s*holder|cardholder|name\s*on\s*card|account\s*holder|customer|payment|billing)'
        
        if re.search(card_keywords, context, re.IGNORECASE):
            findings.append({
                "type": "CARDHOLDER_NAME",
                "value": name,
                "confidence": result.score,
                "context": context.strip(),
                "position": result.start
            })
    
    # Also look for explicitly labeled names
    labeled_pattern = r'(?:Card\s*Holder|Cardholder|Name\s*on\s*Card|Account\s*Holder)[\s:]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)'
    for match in re.finditer(labeled_pattern, text, re.IGNORECASE):
        name = match.group(1).strip()
        context_start = max(0, match.start() - 20)
        context_end = min(len(text), match.end() + 20)
        context = text[context_start:context_end].strip()
        
        # Check if not already found
        if not any(f['value'].lower() == name.lower() for f in findings):
            findings.append({
                "type": "CARDHOLDER_NAME",
                "value": name,
                "confidence": 0.9,
                "context": context,
                "position": match.start()
            })
    
    return findings


def detect_pin(text):
    """
    Detect PIN codes (4-6 digit codes)
    Only flag if explicitly labeled to avoid false positives
    """
    findings = []
    
    # Pattern: Labeled PIN
    labeled_patterns = [
        r'(?:PIN|Pin|pin)[\s:]*(\d{4,6})\b',
        r'(?:Personal\s*Identification\s*Number)[\s:]*(\d{4,6})\b',
    ]
    
    for pattern in labeled_patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            pin = match.group(1)
            context_start = max(0, match.start() - 20)
            context_end = min(len(text), match.end() + 20)
            context = text[context_start:context_end].strip()
            
            findings.append({
                "type": "PIN",
                "value": pin,
                "confidence": 0.95,
                "context": context,
                "position": match.start()
            })
    
    return findings


def detect_track_data(text):
    """
    Detect magnetic stripe track data
    Track 1: Starts with %, contains ^, ends with ?
    Track 2: Starts with ;, ends with ?
    """
    findings = []
    
    # Track 1 pattern: %B1234123412341234^CARDUSER/JOHN^2512101?
    track1_pattern = r'%[A-Z]?\d{13,19}\^[^\^]+\^\d{4}[^\?]*\?'
    for match in re.finditer(track1_pattern, text):
        track_data = match.group()
        context_start = max(0, match.start() - 20)
        context_end = min(len(text), match.end() + 20)
        context = text[context_start:context_end].strip()
        
        findings.append({
            "type": "TRACK_DATA",
            "value": track_data[:20] + "...",  # Truncate for display
            "confidence": 0.95,
            "context": context,
            "position": match.start()
        })
    
    # Track 2 pattern: ;1234123412341234=2512101?
    track2_pattern = r';\d{13,19}=\d{4}[^\?]*\?'
    for match in re.finditer(track2_pattern, text):
        track_data = match.group()
        context_start = max(0, match.start() - 20)
        context_end = min(len(text), match.end() + 20)
        context = text[context_start:context_end].strip()
        
        findings.append({
            "type": "TRACK_DATA",
            "value": track_data[:20] + "...",
            "confidence": 0.95,
            "context": context,
            "position": match.start()
        })
    
    return findings


def detect_all_cardholder_data(text):
    """
    Detect all types of cardholder data in text
    Returns a dictionary with all findings categorized by type
    """
    all_findings = {
        "cvv": detect_cvv(text),
        "expiry_date": detect_expiry_date(text),
        "cardholder_name": detect_cardholder_name(text),
        "pin": detect_pin(text),
        "track_data": detect_track_data(text)
    }
    
    # Remove duplicates based on value
    for key in all_findings:
        seen = set()
        unique_findings = []
        for item in all_findings[key]:
            if item['value'] not in seen:
                seen.add(item['value'])
                unique_findings.append(item)
        all_findings[key] = unique_findings
    
    # Calculate total count
    total_count = sum(len(findings) for findings in all_findings.values())
    
    return {
        "findings": all_findings,
        "total_count": total_count,
        "has_sensitive_data": total_count > 0
    }


def format_cardholder_data_summary(findings_dict):
    """
    Format cardholder data findings into a readable summary
    """
    summary_lines = []
    findings = findings_dict["findings"]
    
    if findings["cvv"]:
        summary_lines.append(f"  • {len(findings['cvv'])} CVV/Security Code(s)")
    if findings["expiry_date"]:
        summary_lines.append(f"  • {len(findings['expiry_date'])} Expiry Date(s)")
    if findings["cardholder_name"]:
        summary_lines.append(f"  • {len(findings['cardholder_name'])} Cardholder Name(s)")
    if findings["pin"]:
        summary_lines.append(f"  • {len(findings['pin'])} PIN Code(s)")
    if findings["track_data"]:
        summary_lines.append(f"  • {len(findings['track_data'])} Track Data")
    
    if not summary_lines:
        return "No additional cardholder data detected"
    
    return "\n".join(summary_lines)
