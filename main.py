import json
import re
from fastapi import FastAPI, Form, Response
from twilio.twiml.messaging_response import MessagingResponse

# Load the knowledge base from the JSON file
with open('knowledge_base.json', 'r') as f:
    knowledge_base = json.load(f)

# Initialize the FastAPI application
app = FastAPI()

def detect_language(text):
    """Detects if the text contains Hindi characters."""
    if re.search(r'[\u0900-\u097F]', text):
        return 'hi'
    return 'en'

@app.post("/webhook")
async def handle_webhook(Body: str = Form(...)):
    user_message = Body.lower()
    lang = detect_language(user_message)
    response_text = ""

    # Check for menu/help commands
    if 'help' in user_message or 'menu' in user_message or 'मदद' in user_message:
        disease_list = ", ".join([d['name'].title() for d in knowledge_base['diseases']])
        if lang == 'hi':
            response_text = f"नमस्ते! मैं इन बीमारियों के बारे में जानकारी दे सकता हूँ: {disease_list}. आप 'लक्षण' (symptoms) या 'बचाव' (prevention) के बारे में पूछ सकते हैं।"
        else:
            response_text = f"Hello! I can provide information on the following diseases: {disease_list}. You can ask about 'symptoms', 'prevention', 'treatment', or 'vaccination'."
    
    # If no help command, check for disease and topic
    if not response_text:
        for disease in knowledge_base['diseases']:
            # Check for disease name or aliases
            all_names = [disease['name'].lower()] + disease.get('aliases', [])
            if any(name in user_message for name in all_names):
                
                # The user mentioned a known disease. Now find the topic.
                topic_found = False
                if 'prevent' in user_message or 'बचाव' in user_message:
                    response_text = disease['prevention'][lang]
                    topic_found = True
                elif 'treat' in user_message or 'इलाज' in user_message:
                    response_text = disease.get('treatment_info', {}).get(lang, "Sorry, I don't have treatment information for this.")
                    topic_found = True
                elif 'vaccin' in user_message or 'टीका' in user_message:
                    response_text = disease.get('vaccination_info', {}).get(lang, "Sorry, I don't have vaccination information for this.")
                    topic_found = True
                else: # Default to symptoms if no other topic is found
                    response_text = disease['symptoms'][lang]
                    topic_found = True
                
                if topic_found:
                    response_text = f"{disease['name'].title()}:\n{response_text}"
                    break

    # If nothing was matched, use a default response
    if not response_text:
        if lang == 'hi':
            response_text = "माफ़ कीजिए, मुझे यह जानकारी नहीं मिली। कृपया 'मदद' टाइप करके देखें कि मैं क्या कर सकता हूँ।"
        else:
            response_text = "Sorry, I don't have that information. Please type 'help' to see what I can do."

    # Send the final response back to Twilio
    twiml_response = MessagingResponse()
    twiml_response.message(response_text)
    return Response(content=str(twiml_response), media_type="application/xml")