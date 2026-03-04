import re


def find_card_patterns(text):
    pattern = r"\b\d{13,16}\b"
    return re.findall(pattern, text)
