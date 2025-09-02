import os
import json
from fastapi import FastAPI, Form, Response
from twilio.twiml.messaging_response import MessagingResponse
from openai import OpenAI

# --- This section was missing ---
# It imports the libraries and sets up the connection to OpenAI
# --------------------------------

# Load the knowledge base from the JSON file
with open('knowledge_base.json', 'r') as f:
    knowledge_base = json.load(f)

# Initialize the OpenAI client using the secret key from Render's environment variables
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Initialize the FastAPI application
app = FastAPI()
# ----------------------------------


@app.post("/webhook")
async def handle_webhook(Body: str = Form(...)):
    user_message = Body
    
    context = "Available Health Information:\n"
    for disease in knowledge_base['diseases']:
        context += f"- Disease: {disease['name'].title()}\n"
        context += f"  Overview: {disease['overview']}\n"
        context += f"  Symptoms: {disease['symptoms']}\n"
        context += f"  Prevention: {disease['prevention']}\n\n"

    # Demo-ready system prompt
    system_prompt = f"""
    You are 'Arogya Sahayak', a friendly and reliable AI public health assistant from India. Your goal is to provide clear, simple health information. You can respond in English or Hindi.

    Here is your trusted health data:
    {context}

    Follow these rules strictly:
    1.  First, check if the user's question can be answered using the trusted health data. If yes, use ONLY that information. Format your answers with clear headings or bullet points to make them easy to read on WhatsApp.
    2.  If the question is a general greeting or on a topic NOT covered in your data, you may use your general knowledge for a helpful, non-medical answer.
    3.  **CRITICAL SAFETY RULE: NEVER provide a medical diagnosis.** If a user describes their personal symptoms (e.g., 'I have a fever'), your ONLY response must be: "I'm sorry to hear you're unwell. As an AI assistant, I cannot give medical advice. Please consult a qualified doctor for a proper diagnosis."
    """

    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        )
        response_text = completion.choices[0].message.content
    except Exception as e:
        print(f"OpenAI API error: {e}")
        response_text = "I'm sorry, I'm having trouble thinking right now. Please try again later."

    twiml_response = MessagingResponse()
    twiml_response.message(response_text)
    return Response(content=str(twiml_response), media_type="application/xml")
