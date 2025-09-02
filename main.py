import json
from fastapi import FastAPI, Form, Response
from twilio.twiml.messaging_response import MessagingResponse

# Load the knowledge base from the JSON file
with open('knowledge_base.json', 'r') as f:
    knowledge_base = json.load(f)

# Initialize the FastAPI application
app = FastAPI()

@app.post("/webhook")
async def handle_webhook(Body: str = Form(...)):
    user_message = Body.lower()
    response_text = "I'm sorry, I don't have that information. Please ask me about symptoms or prevention for a specific disease like Malaria or Dengue."

    # Simple rule-based logic to find the answer
    for disease in knowledge_base['diseases']:
        if disease['name'].lower() in user_message:
            # The user mentioned a known disease. Now check what they want to know.
            if 'prevent' in user_message or 'avoid' in user_message:
                response_text = f"Prevention for {disease['name'].title()}: {disease['prevention']}"
                break
            else: # Default to showing symptoms if prevention isn't mentioned
                response_text = f"Symptoms of {disease['name'].title()}: {disease['symptoms']}"
                break
    
    # Handle general greetings
    if 'hello' in user_message or 'hi' in user_message:
        response_text = "Hello! I am a public health chatbot. You can ask me about symptoms or prevention for diseases like Malaria, Dengue, and Typhoid."

    # Send the response back to Twilio
    twiml_response = MessagingResponse()
    twiml_response.message(response_text)
    return Response(content=str(twiml_response), media_type="application/xml")
