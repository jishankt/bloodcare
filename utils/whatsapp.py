# utils/whatsapp.py
import requests
from django.conf import settings

def send_whatsapp_message(phone_number, message, is_template=False):
    """
    Send WhatsApp message using WhatsApp Business API
    """
    try:
        if not phone_number.startswith("91"):
            phone_number = "91" + phone_number
        
        api_url = "https://graph.facebook.com/v17.0/YOUR_PHONE_NUMBER_ID/messages"
        
        headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_API_KEY}",
            "Content-Type": "application/json"
        }
        
        if is_template:
            payload = {
                "messaging_product": "whatsapp",
                "to": phone_number,
                "type": "template",
                "template": {
                    "name": message,
                    "language": {"code": "en"}
                }
            }
        else:
            payload = {
                "messaging_product": "whatsapp",
                "to": phone_number,
                "type": "text",
                "text": {"body": message}
            }
        
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        return True, response.json()
    
    except Exception as e:
        print(f"WhatsApp sending error: {e}")
        return False, str(e)


def create_whatsapp_chat_link(phone_number):
    """
    Create WhatsApp chat link for donor-hospital communication
    """
    if not phone_number.startswith("91"):
        phone_number = "91" + phone_number
    return f"https://wa.me/{phone_number}"