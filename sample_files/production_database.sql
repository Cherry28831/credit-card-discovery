-- Production Database Backup
-- Server: prod-db-01.company.com
-- Database: customer_payments
-- Date: 2024-01-15

INSERT INTO customer_transactions (customer_id, card_number, amount, timestamp) VALUES
(1001, '4532015112830366', 299.99, '2024-01-15 10:23:45'),
(1002, '5425233430109903', 1499.00, '2024-01-15 11:15:22'),
(1003, '4916338506082832', 89.50, '2024-01-15 12:45:10');

-- Production payment gateway logs
-- CRITICAL: Unencrypted card data in production database
