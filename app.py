from flask import Flask, request, jsonify
from flask import Flask, render_template
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
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

# Dictionary to store business information
business_info_storage = {}

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

# Upcoming Feature (For Multilingual support)
Language = 'Luganda'

# DEBUGGING --- IF YOU HAVE THESE: YOU CAN TEST WITH DUMMY DATA in the test file
print(RECIPIENT_MAIL)
print(RECIPIENT_NO)
print(sendgrid_from_email)
print(sendgrid_api_key)
print(twilio_phone_number)
print(twilio_account_sid)
print(twilio_auth_token)

def summarize(sentence):
    prompt = f"""I will give you some data from a business card, analyse it..
    then extract important info & insights, then summarise it in not more
    than 50 words starting' You have just scanned a business card
    of {sentence} ... (Complete)' """

    # Call the generate_content method
    response = model.generate_content(prompt,
    safety_settings={
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    })

    logging.info(f"Generative AI Response: {response}")

    # Ensure the response has candidates
    if response and response.candidates:
        # Extract the summarised sentence from the first candidate's content parts
        candidate = response.candidates[0]
        if candidate.content and candidate.content.parts:
            summarised_sentence = candidate.content.parts[0].text.strip()
            return summarised_sentence

    logging.error("Summarisation failed, response blocked or invalid.")
    return "summarisation failed, response blocked or invalid."

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
        print(data)
        business_info = data.get('info', '')

        # Save the business information in a dictionary
        business_id = len(business_info_storage) + 1
        business_info_storage[business_id] = business_info
        # print(business_info_storage)
        get_business_info(business_id)

        return jsonify({'message': 'Business information received', 'business_id': business_id})
    except Exception as e:
        logging.error(f"Error in process_scan: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/get-business-info/<int:business_id>', methods=['GET'])
def get_business_info(business_id):
    try:
        business_info = business_info_storage.get(business_id, 'Business not found')
        print(business_info)

        if business_info == 'Business not found':
            return jsonify({'error': 'Business not found'}), 404

        # Summarise business information to Luganda
        summarised_info = summarize(business_info)

        # Send the summarised information via SMS
        recipient_phone_number = RECIPIENT_NO
        send_sms(summarised_info, recipient_phone_number)

        # Send the summarised information via email
        recipient_email = RECIPIENT_MAIL
        subject = 'Your iScan Business Card Results 🎉'
        html_content = f'<strong>{summarised_info}</strong>'
        send_email(subject, html_content, recipient_email)

        return jsonify({'business_info': summarised_info})
    except Exception as e:
        logging.error(f"Error in get_business_info: {e}")
        print(e)
        return jsonify({'error': str(e)}), 500

print(business_info_storage)

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5000)
