from tools.luhn_tool import luhn_check

# All 13-16 digit numbers from sample files
numbers = [
    ("4532015112830366", "dev_environment.log"),
    ("5425233430109903", "dev_environment.log"),
    ("1234567890123456", "dev_environment.log - Account"),
    ("4111111111111111", "payment_processing.log"),
    ("4000000000000002", "payment_processing.log"),
    ("5555555555554444", "payment_processing.log"),
    ("378282246310005", "payment_processing.log"),
    ("234567890123", "payment_processing.log - ID"),
    ("4024007134564842", "backup_dev.sql"),
    ("5200828282828210", "backup_dev.sql"),
    ("6011111111111117", "backup_dev.sql"),
    ("4532015112830366", "backup_dev.sql - duplicate"),
    ("5425233430109903", "backup_dev.sql - duplicate"),
    ("234567890123", "backup_dev.sql - ID"),
    ("1234567890123456", "backup_dev.sql - Account"),
    ("9876543210987654", "backup_dev.sql - Account"),
    ("4916338506082832", "staging_config.ini"),
    ("5425233430109903", "staging_config.ini - duplicate"),
    ("378282246310005", "staging_config.ini - duplicate"),
    ("123456789012", "staging_config.ini - ID"),
]

print("Luhn Validation Results:\n")
valid_count = 0
for num, source in numbers:
    result = luhn_check(num)
    if result:
        valid_count += 1
        print(f"[VALID] {num} - {source}")
    else:
        print(f"[INVALID] {num} - {source}")

print(f"\nTotal: {len(numbers)} numbers checked")
print(f"Valid cards: {valid_count}")
print(f"Invalid: {len(numbers) - valid_count}")
