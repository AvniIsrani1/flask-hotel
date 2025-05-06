"""
Create routes for each page.

Note:
    Author: Avni Israni, Devansh Sharma, Elijah Cortez, Andrew Ponce
    Documentation: Devansh Sharma
    Created: March 2, 2025
    Modified: April 17, 2025
"""

from flask import Flask, Blueprint, jsonify, render_template, request
from flask import Blueprint, jsonify, render_template
from HOTEL.AImodels.csv_retriever import setup_csv_retrieval, get_answer_from_csv
from HOTEL.AImodels.ai_model import load_ai_model, generate_ai_response
from .Services.response import format_response  

ai_model = load_ai_model()
ai_db, ai_df = setup_csv_retrieval()



def process_query(user_question):
    """
    Process a user query using CSV data first, falling back to AI.
    
    Parameters:
        user_question (str): The user's question.
        
    Returns:
        str: The formatted response to the question.
    """
    global ai_db, ai_model  # Using only the globals that are defined
    
    # Initialize or re-initialize the CSV retrieval system
    ai_db, ai_df = setup_csv_retrieval()  # Get both db and df from the function call
    
    # Use ai_df from the local scope, not trying to access a non-existent global
    csv_answer = get_answer_from_csv(ai_db, ai_df, user_question)
    formatted_response = format_response(csv_answer, user_question)
    
    # If we got a valid formatted response, return it
    if formatted_response:
        return formatted_response
    
    # Otherwise, use the AI model to generate a response
    return generate_ai_response(ai_model, user_question)

def process_query(user_question):
    """
    Process a user query using CSV data first, falling back to AI.
    
    Parameters:
        user_question (str): The user's question.
        
    Returns:
        str: The formatted response to the question.
    """
    global ai_db, ai_df, ai_model
    
    # Try to get an answer from the CSV data first
    csv_answer = get_answer_from_csv(ai_db, ai_df, user_question)
    formatted_response = format_response(csv_answer, user_question)
    
    # If we got a valid formatted response, return it
    if formatted_response:
        return formatted_response
    
    # Otherwise, use the AI model to generate a response
    return generate_ai_response(ai_model, user_question)

def chat_routes():
    """
    Create chat-related routes and register them to a blueprint.
    
    Returns:
        Blueprint: The blueprint with chat routes registered.
    """
    bp_chat = Blueprint('chat', __name__)

    @bp_chat.route("/chat")
    def chat():
        """
        Render the chat interface.
        
        Returns:
            Template: The chat page template.
        """
        return render_template("chat.html")

    @bp_chat.route("/get_response", methods=["POST"])
    def get_response():
        """
        Process an AI chat request.
        
        Returns:
            JSON: The AI response as JSON.
        """
        try:
            csv_data = request.get_json()
            user_message = csv_data.get("message", "")
            
            if not user_message:
                return jsonify({"response": "I'm not sure what you mean."})
            
            ai_response = process_query(user_message)
            return jsonify({"response": ai_response})
        except Exception as e:
            # Log the error
            print(f"Error: {str(e)}")
            # Return a proper error response
            return jsonify({"response": "An error occurred while processing your request."}), 500
            
    return bp_chat



