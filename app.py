from flask import Flask, request, jsonify
import google.generativeai as genai
from twilio.rest import Client
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Access your API key as an environment variable.
genai.configure(api_key=os.environ.get('GENAI_API_KEY'))
# Choose a model that's appropriate for your use case.
model = genai.GenerativeModel('gemini-1.5-flash')
app = Flask(__name__)

# Dictionary to store product information
product_info_storage = {}

# Twilio configuration
twilio_account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
twilio_auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
twilio_phone_number = os.environ.get('TWILIO_PHONE_NUMBER')
client = Client(twilio_account_sid, twilio_auth_token)

# SendGrid configuration
sendgrid_api_key = os.environ.get('SENDGRID_API_KEY')
sendgrid_from_email = os.environ.get('SENDGRID_MAIL')

# RECIPIENT info
RECIPIENT_MAIL = os.environ.get('RECIPIENT_MAIL')
RECIPIENT_NO = os.environ.get('RECIPIENT_NO')

# DEBUGGING---
print(RECIPIENT_MAIL)
print(RECIPIENT_NO)
print(sendgrid_from_email)
print(sendgrid_api_key)
print(twilio_phone_number)
print(twilio_account_sid)
print(twilio_auth_token)

def translate_to_luganda(sentence):
    prompt = f"""I will give you a json format data, analyse it..then extract expiry date and approximate when
    the product will expire, then create a short sentence, then Translate it into Luganda.
    Don't give me the pronunciation, just return the translated sentence. Here it is: '{sentence}' """

    # Call the generate_content method
    response = model.generate_content(prompt)

    # Extract the translated sentence
    translated_sentence = response.text.strip()
    return translated_sentence

def send_sms(message, to_phone_number):
    try:
        client.messages.create(
            body=message,
            from_=twilio_phone_number,
            to=to_phone_number
        )
        logging.info(f"SMS sent to {to_phone_number}")
    except Exception as e:
        logging.error(f"Failed to send SMS: {e}")

def send_email(subject, html_content, to_email):
    try:
        message = Mail(
            from_email=sendgrid_from_email,
            to_emails=to_email,
            subject=subject,
            html_content=html_content)
        sg = SendGridAPIClient(api_key=sendgrid_api_key)
        response = sg.send(message)
        logging.info(f"Email sent to {to_email}: {response.status_code}")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")

@app.route('/process-scan', methods=['POST'])
def process_scan():
    try:
        data = request.json
        product_info = data.get('info', '')

        # Save the product information in a dictionary
        product_id = len(product_info_storage) + 1
        product_info_storage[product_id] = product_info

        return jsonify({'message': 'Product information received', 'product_id': product_id})
    except Exception as e:
        logging.error(f"Error in process_scan: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/get-product-info/<int:product_id>', methods=['GET'])
def get_product_info(product_id):
    try:
        product_info = product_info_storage.get(product_id, 'Product not found')

        if product_info == 'Product not found':
            return jsonify({'error': 'Product not found'}), 404

        # Translate product information to Luganda
        translated_info = translate_to_luganda(product_info)

        # Send the translated information via SMS
        recipient_phone_number = RECIPIENT_NO
        send_sms(translated_info, recipient_phone_number)

        # Send the translated information via email
        recipient_email = RECIPIENT_MAIL
        subject = 'Your iScan Results'
        html_content = f'<strong>{translated_info}</strong>'
        send_email(subject, html_content, recipient_email)

        return jsonify({'product_info': translated_info})
    except Exception as e:
        logging.error(f"Error in get_product_info: {e}")
        return jsonify({'error': str(e)}), 500

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5000)
