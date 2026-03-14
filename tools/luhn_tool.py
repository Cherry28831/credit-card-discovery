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
