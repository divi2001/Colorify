# apps\subscription_module\payu_utils.py
import hashlib
import hmac
import urllib.parse
from django.conf import settings
import uuid

class PayUConfig:
    def __init__(self):
        # Replace these with your actual PayU credentials in settings.py
        self.merchant_key = settings.PAYU_MERCHANT_KEY
        self.merchant_salt = settings.PAYU_MERCHANT_SALT
        self.base_url = settings.PAYU_BASE_URL  # Use settings.PAYU_TEST_URL for testing
        
    def generate_txnid(self):
        """Generate a unique transaction ID"""
        return str(uuid.uuid4())
        
    def calculate_hash(self, data_dict):
        """
        Calculate PayU hash for transaction
        """
        # Remove all None values
        data_dict = {k: v for k, v in data_dict.items() if v is not None}
        
        # Get all keys except hash
        hash_sequence = "key|txnid|amount|productinfo|firstname|email|udf1|udf2|udf3|udf4|udf5|udf6|udf7|udf8|udf9|udf10"
        hash_values = []
        
        for item in hash_sequence.split('|'):
            hash_values.append(str(data_dict.get(item, '')))
        
        hash_values.append(self.merchant_salt)
        hash_string = '|'.join(hash_values)
        
        return hashlib.sha512(hash_string.encode('utf-8')).hexdigest().lower()
        
    def verify_hash(self, data_dict):
        """
        Verify the hash returned by PayU
        """
        received_hash = data_dict.get('hash')
        if not received_hash:
            return False
        
        status = data_dict.get('status', '')
        
        # Hash string format: SALT|status|udf10|udf9|udf8|udf7|udf6|udf5|udf4|udf3|udf2|udf1|email|firstname|productinfo|amount|txnid|key
        hash_sequence = "salt|status|udf10|udf9|udf8|udf7|udf6|udf5|udf4|udf3|udf2|udf1|email|firstname|productinfo|amount|txnid|key"
        hash_values = []
        
        # Add salt first
        hash_values.append(self.merchant_salt)
        
        # Add remaining values
        for item in hash_sequence.split('|')[1:]:  # Skip salt as we've already added it
            if item == 'salt':
                continue
            hash_values.append(str(data_dict.get(item, '')))
        
        hash_string = '|'.join(hash_values)
        calculated_hash = hashlib.sha512(hash_string.encode('utf-8')).hexdigest().lower()
        
        return calculated_hash == received_hash