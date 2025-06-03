import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def get_openai_client():
    # Note: This function will not work if user enters API_KEY in streamlit app
    print(os.getenv("OPENAI_API_KEY"))
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)
    return client


