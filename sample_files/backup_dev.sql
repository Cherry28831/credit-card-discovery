-- Database Backup - Development Environment
-- Date: 2024-01-15
-- Server: dev-db-01

INSERT INTO test_transactions (token_id, amount, status) VALUES
('4024007134564842', 25.00, 'completed'),
('5200828282828210', 50.00, 'completed'),
('6011111111111117', 15.00, 'pending');

-- Test customer data
INSERT INTO customers (name, reference_id, national_id, contact) VALUES
('Test User 1', '4532015112830366', '234567890123', '9876543210'),
('Test User 2', '5425233430109903', '345678901234', '8765432109');

INSERT INTO kyc_data (customer_id, verification_code, tax_id, account_number) VALUES
(1001, '123-45-6789', 'ABCDE1234F', '1234567890123456'),
(1002, '987-65-4321', 'FGHIJ5678K', '9876543210987654');

-- Environment: DEVELOPMENT
-- Access: Restricted to dev team
