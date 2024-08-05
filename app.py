from flask import Flask, request, jsonify
from flask import render_template
from ai71 import AI71
from dotenv import load_dotenv
import os
import logging
from twilio.rest import Client
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load environment variables from the .env file
load_dotenv()

# Get the API key from the environment variable
AI71_API_KEY = os.getenv("AI71_API_KEY")
MODEL = "tiiuae/falcon-180b-chat"

app = Flask(__name__)

# Dictionary to store business information
business_info_storage = {}

# Twilio configuration
twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')
twilio_phone_number = os.getenv('TWILIO_PHONE_NUMBER')
client = Client(twilio_account_sid, twilio_auth_token)

# SendGrid configuration
sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
sendgrid_from_email = os.getenv('SENDGRID_MAIL')

# RECIPIENT info
RECIPIENT_MAIL = os.getenv('RECIPIENT_MAIL')
RECIPIENT_NO = os.getenv('RECIPIENT_NO')

# Upcoming Feature (For Multilingual support)
Language = 'Luganda'

def summarize(sentence):
    prompt = f"""I will give you some data from a business card, analyse it..
    then extract important info & insights, then summarise it starting
    'You have just scanned a business card of {sentence} ... (Not more than 40 words)' """

    # Call the Falcon model
    try:
        # print("PROMPT", prompt)
        summary = ""
        for chunk in AI71(AI71_API_KEY).chat.completions.create(
            model = MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful Business Assistant."},
                {"role": "user", "content": prompt},
            ],
            stream=True,
        ):
            if chunk.choices[0].delta.content:
                # Finfo = chunk.choices[0]
                # print("FALCON INFO", Finfo, sep="", end="", flush=True)
                summary += chunk.choices[0].delta.content
        return summary
    except Exception as e:
        logging.error(f"Error during summarisation: {e}")

    return "Summarisation failed, response blocked or invalid."

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize_route():
    data = request.json
    sentence = data.get('sentence')
    if not sentence:
        return jsonify({"error": "No sentence provided"}), 400

    summary = summarize(sentence)
    return jsonify({"summary": summary})

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
        print(business_info_storage)
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


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
