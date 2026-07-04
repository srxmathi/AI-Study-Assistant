import os
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=API_KEY)


def generate_summary(text):



    # Prevent sending extremely large PDFs to the model
    if len(text) > 12000:
        text = text[:12000]

    prompt = f"""
You are an intelligent AI Study Assistant.

Analyze the following study notes carefully and generate your response in the EXACT format below.

# 📄 Summary
Write a clear summary in 6-8 sentences.

# ⭐ Important Topics
List the most important concepts as bullet points.

# 📝 2-Mark Questions
Generate 5 short exam questions.

# 📝 5-Mark Questions
Generate 5 descriptive exam questions.

# 🎯 Viva Questions
Generate 5 viva interview questions.

# 💡 Revision Tips
Give 5 quick revision tips for this topic.

Study Notes:
{text}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text

def ask_question(pdf_text, question):

    if len(pdf_text) > 12000:
        pdf_text = pdf_text[:12000]

    prompt = f"""
You are an AI Study Assistant.

Answer ONLY using the uploaded study notes.

If the answer is not present in the notes, reply exactly:
"I couldn't find this information in the uploaded notes."

Study Notes:
{pdf_text}

Question:
{question}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text