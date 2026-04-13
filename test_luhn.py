def luhn_check(card_number):
    card_number = ''.join(filter(str.isdigit, card_number))
    digits = [int(d) for d in card_number]
    checksum = 0
    reverse_digits = digits[::-1]

    for i, digit in enumerate(reverse_digits):
        if i % 2 == 1:
            digit *= 2
            if digit > 9:
                digit -= 9
        checksum += digit

    return checksum % 10 == 0

numbers = [
    '4111111111111111',
    '4000000000000002',
    '5555555555554444',
    '378282246310005',
    '4532015112830366',
    '5425233430109903',
    '1234567890123456',
    '4916338506082832',
    '4024007134564842',
    '5200828282828210',
    '6011111111111117',
    '234567890123',
    '9876543210',
    '987654321098',
    '123456789012',
    '9123456789'
]

print("Luhn Validation Results:")
print("-" * 40)
valid_count = 0
for n in numbers:
    result = luhn_check(n)
    if result:
        valid_count += 1
    print(f"{n}: {'VALID' if result else 'INVALID'}")

print("-" * 40)
print(f"Total valid cards: {valid_count}")
