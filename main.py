@app.post("/webhook")
async def handle_webhook(Body: str = Form(...)):
    user_message = Body
    
    # Convert the entire knowledge base into a string for the AI
    context = "Available Health Information:\n"
    for disease in knowledge_base['diseases']:
        context += f"- Disease: {disease['name'].title()}\n"
        context += f"  Symptoms: {disease['symptoms']}\n"
        context += f"  Prevention: {disease['prevention']}\n\n"

    # Create a much smarter prompt for the OpenAI API
    system_prompt = f"""
    You are a helpful and concise public health chatbot for rural communities. 
    Your primary goal is to provide clear, simple answers based ONLY on the information provided below.
    If the user's question cannot be answered using this information, 
    politely state that you can only provide information on the listed diseases.
    Do not answer general questions outside of this scope.
    
    Here is the available health data:
    {context}
    """

    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
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