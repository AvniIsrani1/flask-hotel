def format_response(answer, question):
    #Decipher whether User input should be derived from CSV or from ai model 
    # If answer from CSV not found fallback model
    if not answer:
        return None
    
    # Remove CSV metadata from the response if present
    if "category:" in answer or "sub_category:" in answer or "description:" in answer:
        try:
            # Try to extract just the description
            if "description:" in answer:
                description = answer.split("description:")[1].strip()
                return f"Ocean Vista: {description}"
            else:
                # If no description found, initiate AI fallback
                return None
        except:
            # If parsing fails, use the AI fallback
            return None
    
    #return Answer
    return f"Ocean Vista: {answer}"