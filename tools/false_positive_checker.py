# Known test credit card numbers used by payment processors
TEST_CARDS = {
    "4242424242424242",  # Stripe test card
    "4111111111111111",  # Generic test Visa
    "5555555555554444",  # Generic test Mastercard
    "378282246310005",   # Amex test
    "6011111111111117",  # Discover test
    "5105105105105100",  # Mastercard test
}

def is_test_card(card_number):
    """Check if card is a known test card"""
    return card_number in TEST_CARDS

import os

def has_test_context(file_path, surrounding_text=""):
    """Check if file/context suggests test data"""
    test_indicators = [
        "test", "demo", "sample", "example", 
        "mock", "dummy", "fake", "dev"
    ]
    
    file_lower = os.path.basename(file_path).lower()
    text_lower = surrounding_text.lower()
    
    return any(indicator in file_lower or indicator in text_lower 
               for indicator in test_indicators)
