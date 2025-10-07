-- SQL script to add missing Razorpay columns to PaymentTransaction table
-- Run this on your production database (colorify3)

USE colorify3;

-- Add the missing Razorpay columns to the subscription_module_paymenttransaction table
ALTER TABLE subscription_module_paymenttransaction 
ADD COLUMN razorpay_order_id VARCHAR(255) NULL,
ADD COLUMN razorpay_payment_id VARCHAR(255) NULL,
ADD COLUMN razorpay_signature VARCHAR(255) NULL;

-- Update the payment_method default for new records (optional)
ALTER TABLE subscription_module_paymenttransaction 
MODIFY COLUMN payment_method VARCHAR(50) DEFAULT 'Razorpay';

-- Verify the columns were added
DESCRIBE subscription_module_paymenttransaction;

-- Show the updated table structure
SHOW CREATE TABLE subscription_module_paymenttransaction; 