# Production Deployment Guide - Razorpay Integration Fix

## Issue Summary
The production server is throwing `OperationalError: (1054, "Unknown column 'razorpay_order_id' in 'field list'")` because the database schema is missing the new Razorpay fields that were added to the Django models.

## Immediate Fix (Option 1: Direct SQL)

### Step 1: Connect to Production Database
```bash
mysql -u your_db_user -p colorify3
```

### Step 2: Run the SQL Script
Execute the contents of `add_razorpay_columns.sql`:

```sql
USE colorify3;

-- Add the missing Razorpay columns
ALTER TABLE subscription_module_paymenttransaction 
ADD COLUMN razorpay_order_id VARCHAR(255) NULL,
ADD COLUMN razorpay_payment_id VARCHAR(255) NULL,
ADD COLUMN razorpay_signature VARCHAR(255) NULL;

-- Update payment_method default
ALTER TABLE subscription_module_paymenttransaction 
MODIFY COLUMN payment_method VARCHAR(50) DEFAULT 'Razorpay';

-- Verify changes
DESCRIBE subscription_module_paymenttransaction;
```

## Proper Migration Fix (Option 2: Django Migrations)

### Step 1: Deploy Code to Production
1. Push the `prod_setup` branch to your production server:
```bash
git push origin prod_setup
```

2. On production server, pull the changes:
```bash
cd /path/to/your/production/code
git checkout prod_setup
git pull origin prod_setup
```

### Step 2: Install Dependencies
```bash
source your_venv/bin/activate
pip install django-jazzmin razorpay django-allauth djangorestframework
```

### Step 3: Run Migrations
```bash
python manage.py migrate
```

### Step 4: Restart Production Server
```bash
# For Gunicorn
sudo systemctl restart gunicorn

# For uWSGI  
sudo systemctl restart uwsgi

# Or however you restart your Django application
```

## Files Modified in this Branch

### 1. `tif_editor_project/settings.py`
- Added CSRF_TRUSTED_ORIGINS for https://colorifystudio.ai
- Added security settings for production
- Enhanced CSRF cookie settings

### 2. `apps/subscription_module/models.py`
- Fixed duplicate payment_method field
- Added razorpay_order_id, razorpay_payment_id, razorpay_signature fields
- Reorganized field definitions for better structure

### 3. Migration Files Created
- `apps/subscription_module/migrations/0001_initial.py`
- `apps/mainadmin/migrations/0001_initial.py`
- `apps/tif_to_picker/migrations/0001_initial.py`

## Testing the Fix

After applying either fix option:

1. **Test the payment flow:**
   - Navigate to `/subscriptions/plans/`
   - Click "Upgrade" on any plan
   - Verify the payment initiation page loads without errors

2. **Check database:**
   ```sql
   SELECT razorpay_order_id, razorpay_payment_id, razorpay_signature 
   FROM subscription_module_paymenttransaction 
   LIMIT 5;
   ```

3. **Monitor logs:**
   ```bash
   tail -f /path/to/your/django.log
   ```

## Rollback Plan

If issues occur, you can quickly rollback:

### For SQL Fix:
```sql
ALTER TABLE subscription_module_paymenttransaction 
DROP COLUMN razorpay_order_id,
DROP COLUMN razorpay_payment_id,
DROP COLUMN razorpay_signature;
```

### For Migration Fix:
```bash
python manage.py migrate subscription_module zero
git checkout final-integration-div
```

## Additional Production Settings

Consider updating these settings for production:

```python
# In settings.py
DEBUG = False
ALLOWED_HOSTS = ['colorifystudio.ai', 'www.colorifystudio.ai']

# Security settings
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

## Next Steps

1. Apply the immediate fix (Option 1) for quick resolution
2. Test thoroughly in production
3. Plan proper migration deployment (Option 2) for long-term maintenance
4. Update your deployment pipeline to include migration checks

## Support

If you encounter issues:
1. Check Django logs for detailed error messages
2. Verify database connectivity and permissions
3. Ensure all dependencies are installed
4. Confirm the correct git branch is deployed 