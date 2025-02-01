import requests
from userSync import logger
from dotenv import load_dotenv
import os
import json

# Load the .env file
load_dotenv()

# Access the API key
EXTENDED_API_TOKEN = os.getenv("EXTENDED_API_TOKEN")
API_KEY = None

url = "https://api.verkada.com/token"


def generate_api_token():
    headers = {"accept": "application/json", "x-api-key": EXTENDED_API_TOKEN}
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        logger.info("Token has been successfully generated.")
        return response.text
    else:
        logger.error(
            f"Error generating API token: {response.status_code}, {response.text}"
        )
