from ai71 import AI71
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

# Get the API key from the environment variable
AI71_API_KEY = os.getenv("AI71_API_KEY")

def RE():
    prompt = "I will give you some data from a business card, analyse it.. then extract important info & insights, then summarise it starting 'You have just scanned a business card of {'Name: John Doe\r\nTitle: Sr Software Engineer\r\nCompany: John Doe Inc.\r\nEmail: john.doe@johndoe.com\r\nPhone: +256 (555) 123-456\r\nAddress: Makerere, Uganda\r\nWebsite: www.johndoe.com'} ... (Not more than 40 words)"
    try:
        for chunk in AI71(AI71_API_KEY).chat.completions.create(
            model="tiiuae/falcon-180b-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            stream=True,
        ):
            if chunk.choices[0].delta.content:
                print(chunk.choices)
                # print(chunk.choices[0].delta.content, sep="", end="", flush=True)
    except Exception as e:
        raise
    else:
        pass
RE()
