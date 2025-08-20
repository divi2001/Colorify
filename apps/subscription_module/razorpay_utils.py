# apps/subscription_module/razorpay_utils.py
import razorpay
import hmac
import hashlib
from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class RazorpayConfig:
    def __init__(self):
        self.client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )
    
    def create_order(self, amount, currency='INR', receipt=None, notes=None):
        """
        Create a Razorpay order
        amount: Amount in smallest currency unit (paise for INR)
        """
        try:
            order_data = {
                'amount': int(amount * 100),  # Convert to paise
                'currency': currency,
                'receipt': receipt or f'receipt_{timezone.now().timestamp()}',
                'notes': notes or {}
            }
            
            order = self.client.order.create(data=order_data)
            logger.info(f"Razorpay order created: {order['id']}")
            return order
        except Exception as e:
            logger.error(f"Error creating Razorpay order: {e}")
            raise
    
    def verify_payment_signature(self, razorpay_order_id, razorpay_payment_id, razorpay_signature):
        """
        Verify payment signature for security
        """
        try:
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            
            # Verify signature
            self.client.utility.verify_payment_signature(params_dict)
            return True
        except razorpay.errors.SignatureVerificationError:
            logger.error("Razorpay signature verification failed")
            return False
        except Exception as e:
            logger.error(f"Error verifying payment signature: {e}")
            return False
    
    def get_payment_details(self, payment_id):
        """
        Get payment details from Razorpay
        """
        try:
            payment = self.client.payment.fetch(payment_id)
            return payment
        except Exception as e:
            logger.error(f"Error fetching payment details: {e}")
            return None