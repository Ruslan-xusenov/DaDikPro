import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class EskizClient:
    BASE_URL = "https://notify.eskiz.uz/api"

    def __init__(self):
        self.email = getattr(settings, 'ESKIZ_EMAIL', None)
        self.password = getattr(settings, 'ESKIZ_PASSWORD', None)
        self.token = None

    def get_token(self):
        url = f"{self.BASE_URL}/auth/login"
        data = {
            'email': self.email,
            'password': self.password
        }
        try:
            response = requests.post(url, data=data)
            if response.status_code == 200:
                self.token = response.json().get('data', {}).get('token')
                return self.token
            else:
                logger.error(f"Eskiz login failed: {response.text}")
        except Exception as e:
            logger.error(f"Eskiz connection error: {e}")
        return None

    def send_sms(self, phone, message):
        if not self.token:
            if not self.get_token():
                return False

        # Ensure phone is in format 998XXXXXXXXX (without +)
        clean_phone = ''.join(filter(str.isdigit, str(phone)))
        if clean_phone.startswith('00'):
            clean_phone = clean_phone[2:]
        
        url = f"{self.BASE_URL}/message/sms/send"
        headers = {
            'Authorization': f"Bearer {self.token}"
        }
        data = {
            'mobile_phone': clean_phone,
            'message': message,
            'from': '4546' # Default for Eskiz if not specified
        }
        
        try:
            response = requests.post(url, headers=headers, data=data)
            if response.status_code == 200:
                return True
            elif response.status_code == 401: # Token expired
                self.token = None
                return self.send_sms(phone, message) # Retry once
            else:
                logger.error(f"Eskiz SMS failed: {response.text}")
        except Exception as e:
            logger.error(f"Eskiz send error: {e}")
        return False
