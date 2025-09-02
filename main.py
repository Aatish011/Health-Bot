import os
import json
from fastapi import FastAPI, Form, Response
from twilio.twiml.messaging_response import MessagingResponse
from openai import OpenAI

# --- CONFIGURATION ---
# Paste your OpenAI API key here
import os # Add this line to the top with your other imports
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
# ---------------------

# Load the knowledge base from the JSON file
with open('knowledge_base.json', 'r') as f:
    knowledge_base = json.load(f)

app = FastAPI()

@app.post("/webhook")
async def handle_webhook(Body: str = Form(...)):
    user_message = Body.lower()

    # Simple logic to see if the user is asking about a known disease
    found_disease = None
    for disease in knowledge_base['diseases']:
        if disease['name'] in user_message:
            found_disease = disease
            break

    response_text = ""
    if found_disease:
        # If a known disease is mentioned, provide the info directly
        response_text = f"Symptoms of {found_disease['name'].title()}: {found_disease['symptoms']}"
    else:
        # If not, use OpenAI for a general response
        try:
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful public health assistant. Keep your answers brief and clear."},
                    {"role": "user", "content": user_message}
                ]
            )
            response_text = completion.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API error: {e}")
            response_text = "I'm sorry, I'm having trouble thinking right now. Please try again."

    # Send the response back to Twilio
    twiml_response = MessagingResponse()
    twiml_response.message(response_text)
    return Response(content=str(twiml_response), media_type="application/xml")