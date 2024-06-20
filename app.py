from flask import Flask, request, jsonify
import google.generativeai as genai
from twilio.rest import Client

# Access your API key as an environment variable.
genai.configure(api_key='AIzaSyBd08-_HORcZFjkYZ94mMI2fDHr47s5nUk')
# Choose a model that's appropriate for your use case.
model = genai.GenerativeModel('gemini-1.5-flash')
app = Flask(__name__)

# Dictionary to store product information
product_info_storage = {}

# Twilio configuration
twilio_account_sid = 'AC520300032d92fa952838b77df67be3e8'
twilio_auth_token = 'e16d30058104f0ff3eaddd85bce71502'
twilio_phone_number = '+14695027531'
client = Client(twilio_account_sid, twilio_auth_token)

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
    client.messages.create(
        body=message,
        from_=twilio_phone_number,
        to=to_phone_number
    )

@app.route('/process-scan', methods=['POST'])
def process_scan():
    data = request.json
    product_info = data.get('info', '')

    # Save the product information in a dictionary
    product_id = len(product_info_storage) + 1
    product_info_storage[product_id] = product_info

    return jsonify({'message': 'Product information received', 'product_id': product_id})

@app.route('/get-product-info/<int:product_id>', methods=['GET'])
def get_product_info(product_id):
    product_info = product_info_storage.get(product_id, 'Product not found')

    # Translate product information to Luganda
    translated_info = translate_to_luganda(product_info)

    # Send the translated information via SMS
    # Actual phone number of the farmer
    recipient_phone_number = '+256703151746'
    send_sms(translated_info, recipient_phone_number)

    return jsonify({'product_info': translated_info})

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5000)
