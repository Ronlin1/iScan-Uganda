import requests
import json

# Test data
test_data = {
    "info": {
        "name": "John Doe",
        "title": "Senior Software Engineer",
        "company": "Tech Innovators Inc.",
        "email": "john.doe@techinnovators.com",
        "phone": "+256 (555) 123-4567",
        "address": "Makerere, Uganda",
        "website": "www.techinnovators.com"
    }
}

data = {'info': 'Name: John Doe\r\nTitle: Sr Software Engineer\r\nCompany: John Doe Inc.\r\nEmail: john.doe@johndoe.com\r\nPhone: +256 (555) 123-456\r\nAddress: Makerere, Uganda\r\nWebsite: www.johndoe.com'}
# API URL
process_scan_url = "http://127.0.0.1:5000/process-scan"
get_business_info_url = "http://127.0.0.1:5000/get-business-info"

# Send the POST request to process-scan endpoint
response = requests.post(process_scan_url, json=data)

# Print the response from process-scan
print("Process Scan Response Status Code:", response.status_code)
print("Process Scan Response JSON:", response.json())


# Extract business_id from response
business_id = response.json().get('business_id')

# Send GET request to /get-business-info/<business_id>
response_ = requests.get(f'{get_business_info_url}/{business_id}')
print(response_.json())

# def summarize(sentence):
#     prompt = f"""I will give you some data from a business card, analyse it..
#     then extract important info then summarise' You have just
#     scanned a business card of {sentence} ... (Complete)' """
#
#     # Call the generate_content method
#     response = model.generate_content(prompt)
#
#     # Extract the translated sentence
#     translated_sentence = response.text.strip()
#     # print(translated_sentence)
#     return translated_sentence
#
# print(summarize(data))
# print(response.json())

















# if response.status_code == 200:
#     business_id = response.json().get('business_id')
#     if business_id:
#         # Send the GET request to get-business-info endpoint
#         get_info_response = requests.get(f"{get_business_info_url}/{business_id}")
#
#         # Print the response from get-business-info
#         print("Get Business Info Response Status Code:", get_info_response.status_code)
#         print("Get Business Info Response JSON:", get_info_response.json())
#     else:
#         print("Business ID not found in response.")
# else:
#     print("Error in processing scan.")
