import re

def format_response(answer, question):
    """
    Process and format the response returned by either the CSV faiss similarity system or fallback to text 2 text AI model.

    Args:
        answer (str): The retrieved from CSV file or AI generated answer related to the user's question.
        question (str): The original question prompted via the user (not directly used, but uses relative context terms).

    Returns:
        str | None: A cleaned and formatted answer prefixed with 'Ocean Vista:', or None then fault to AI fallback if CSV answer not found.
    """
    
    # If answer from CSV not found fallback model
    if not answer:
        return None
        
    # Check if the answer follows the pattern: "category sub_category combined"
    # Example: "rooms standard rooms - standard: there are 200 standard rooms in total."
    
    # First, try to extract description from format with "description:" label
    if "description:" in answer.lower():
        try:
            description = answer.split("description:")[1].strip()
            return f"Ocean Vista: {description}"
        except:
            # If parsing fails, continue to other methods
            pass
            
    # Second, try to extract from format with category - subcategory: description
    match = re.search(r'.*?:(.+)', answer)
    if match:
        description = match.group(1).strip()
        return f"Ocean Vista: {description}"
        
    # Third, try to extract from CSV row format (like in the original BugginFace.py)
    parts = answer.split(',')
    if len(parts) >= 3:
        # Assume last part is description
        description = parts[2].strip()
        return f"Ocean Vista: {description}"
    
    # If all extraction methods fail, just return the answer with branding
    return f"Ocean Vista: {answer}"

def is_greeting(text):
    """
    Check whether the user input is a greeting.

    Args:
        text (str): The user's input text.

    Returns:
        bool: True if it's a greeting, False otherwise.
    """
    greetings = ["hello", "hi", "hey", "good morning", "good evening"]
    return any(greet in text.lower() for greet in greetings)

def is_small_talk(text):
    """
    Check whether the user input qualifies as small talk.

    Args:
        text (str): The user's input text.

    Returns:
        bool: True if it's casual small talk, False otherwise.
    """
    return any(p in text.lower() for p in ["how are you", "what's up", "how's it going"])

def handle_special_queries(user_input):
    """
    Handle user input that is either a greeting or small talk, and generate an appropriate Ocean Vista response.

    Args:
        user_input (str): The user's typed message.

    Returns:
        str | None: A branded greeting/small talk reply, or None if not applicable.
    """
    if is_greeting(user_input):
        return "Ocean Vista: Hello! Welcome to the Ocean Vista Hotel Website."
    
    if is_small_talk(user_input):
        return "Ocean Vista: I'm doing great, thank you! What information can I help you with today?"
    
    return None