from transformers import pipeline

def load_ai_model():
    "Load AI model from Hugging Face."
    checkpoint = "MBZUAI/LaMini-Flan-T5-248M"
    return pipeline('text2text-generation', model=checkpoint)

def generate_ai_response(ai_model, question):
    "Generate a dynamic AI response focused on hotel and vacation topics."
    question_lower = question.lower()


#    try:
#        prompt = f"Format this hotel information into a direct, concise response that ONLY addresses the question: '{question}'. Information: {answer}"    
#        # Generate response with the AI model
#        ai_response = ai_model(prompt, max_length=200, do_sample=True)[0]['generated_text']
#        
#        # Ensure the response starts with "Ocean Vista: " for consistent branding
#        if not ai_response.startswith("Ocean Vista:"):
#            ai_response = f"Ocean Vista: {ai_response}"
#        
#        return ai_response
#        
#    except Exception as e:
#        print(f"Error generating AI response: {e}")
#        return "Ocean Vista: I'm sorry, I don't have specific information about that. Is there something else I can help you with?"