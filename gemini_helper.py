import os
from dotenv import load_dotenv
from google import genai

# Load the .env file
load_dotenv()

# Read API key
API_KEY = os.getenv("GEMINI_API_KEY")

# Create Gemini client
client = genai.Client(api_key=API_KEY)


def generate_summary(text):
    """
    Generate a summary of the uploaded PDF.
    """

    prompt = f"""
    You are an AI Study Assistant.

    Read the following study notes and generate:

    1. A short summary
    2. Important topics
    3. Five 2-mark questions
    4. Five 5-mark questions

    Study Notes:
    {text}
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text