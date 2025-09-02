from fastapi import FastAPI, Form, Response
from fastapi import FastAPI
import json
with open('knowledge_base.json', 'r') as f:
    knowledge_base = json.load(f)
app = FastAPI()
@app.post("/webhook")
async def handle_webhook(Body: str = Form(...)):
    user_message = Body
    
    # Convert the entire knowledge base into a string for the AI
    context = "Available Health Information:\n"
    for disease in knowledge_base['diseases']:
        context += f"- Disease: {disease['name'].title()}\n"
        context += f"  Symptoms: {disease['symptoms']}\n"
        context += f"  Prevention: {disease['prevention']}\n\n"

    # Create a new, more advanced prompt
    system_prompt = f"""
    You are a friendly and helpful public health assistant for rural communities.

    Here is your trusted health data:
    {context}

    Follow these rules strictly:
    1.  First, check if the user's question can be fully answered using the trusted health data provided. If yes, use ONLY that information for your answer.
    2.  If the question is a general greeting, a simple question, or on a health topic NOT covered in the trusted data (e.g., 'what is a vitamin?', 'how do vaccines work?'), you may use your general knowledge to provide a helpful, non-medical answer.
    3.  **CRITICAL SAFETY RULE: NEVER, under any circumstances, provide a medical diagnosis or treatment advice.** If a user describes their personal symptoms (e.g., 'I have a fever and a headache'), your ONLY response must be to advise them to see a doctor immediately. Do not try to guess their illness.
    """

    try:
        completion = client.chat.completions.create(
            model="gpt-4o",  # Using a more powerful model for better reasoning
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        )
        response_text = completion.choices[0].message.content
    except Exception as e:
        print(f"OpenAI API error: {e}")
        response_text = "I'm sorry, I'm having trouble thinking right now. Please try again later."

    # Send the response back to Twilio
    twiml_response = MessagingResponse()
    twiml_response.message(response_text)

    return Response(content=str(twiml_response), media_type="application/xml")



