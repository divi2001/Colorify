-- SQL Script to Create Invoice Table for Colorify
-- Run this SQL in your MySQL/MariaDB database

-- Create the subscription_module_invoice table
CREATE TABLE IF NOT EXISTS `subscription_module_invoice` (
    `id` bigint NOT NULL AUTO_INCREMENT,
    `invoice_number` varchar(50) NOT NULL UNIQUE,
    `issue_date` datetime(6) NOT NULL,
    `due_date` datetime(6) DEFAULT NULL,
    `subtotal` decimal(10, 2) NOT NULL,
    `tax_percentage` decimal(5, 2) NOT NULL DEFAULT 18.00,
    `tax_amount` decimal(10, 2) NOT NULL,
    `discount_amount` decimal(10, 2) NOT NULL DEFAULT 0.00,
    `total_amount` decimal(10, 2) NOT NULL,
    `status` varchar(20) NOT NULL DEFAULT 'issued',
    `notes` longtext DEFAULT NULL,
    `created_at` datetime(6) NOT NULL,
    `updated_at` datetime(6) NOT NULL,
    `transaction_id` bigint NOT NULL UNIQUE,
    `user_id` bigint NOT NULL,
    PRIMARY KEY (`id`),
    KEY `subscription_module_invoice_created_at_idx` (`created_at` DESC),
    KEY `subscription_module_invoice_user_created_idx` (`user_id`, `created_at` DESC),
    KEY `subscription_module_invoice_transaction_id` (`transaction_id`),
    KEY `subscription_module_invoice_user_id` (`user_id`),
    CONSTRAINT `subscription_module_invoice_transaction_id_fk` 
        FOREIGN KEY (`transaction_id`) 
        REFERENCES `subscription_module_paymenttransaction` (`id`) 
        ON DELETE CASCADE,
    CONSTRAINT `subscription_module_invoice_user_id_fk` 
        FOREIGN KEY (`user_id`) 
        REFERENCES `core_customuser` (`id`) 
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Add check constraint for status (if your MySQL version supports it - MySQL 8.0+)
-- ALTER TABLE `subscription_module_invoice` 
-- ADD CONSTRAINT `subscription_module_invoice_status_check` 
-- CHECK (`status` IN ('draft', 'issued', 'paid', 'cancelled'));

-- Verify the table was created
SELECT 'Invoice table created successfully!' as message;
DESCRIBE `subscription_module_invoice`;

