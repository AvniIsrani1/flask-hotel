from transformers import pipeline

def load_ai_model():
    """
    Load and return the AI model from Hugging Face for text generation.

    Args:
        None

    Returns:
        Pipeline: A Hugging Face pipeline ready for text2text generation.
    """
    checkpoint = "MBZUAI/LaMini-Flan-T5-248M"
    return pipeline('text2text-generation', model=checkpoint)

def generate_ai_response(ai_model, question):
    """
    Generate a dynamic AI response focused on hotel and vacation topics.

    Args:
        ai_model (Pipeline): The loaded Hugging Face model for text generation.
        question (str): The user's original question input.

    Returns:
        str: A response string branded with 'Ocean Vista' or a fallback message.
    """
    
    prompt = (
        "You're a helpful assistant for Ocean Vista Hotel in Malibu, California. "
        "Only provide answers related to Malibu or Los Angeles—especially about hotels, vacations, food, local attractions, and activities. "
        "Never say you're an AI model or refer users to other websites. "
        "If you don't know something, reply with a helpful suggestion related to Malibu. "
        "If the question does not pertain to hotels, vacations, food, local attractions, and activities, "
        "politely redirect to these topics. "
        f"User asked: {question}"
    )
    
    try:
        # Generate response with the AI model
        ai_response = ai_model(prompt, max_length=128, do_sample=True)[0]['generated_text']
        
        # Ensure the response starts with "Ocean Vista: " for consistent branding
        if not ai_response.startswith("Ocean Vista:"):
            ai_response = f"Ocean Vista: {ai_response}"
        
        return ai_response
        
    except Exception as e:
        print(f"Error generating AI response: {e}")
        return "Ocean Vista: I'm sorry, I don't have specific information about that. Is there something else I can help you with?"