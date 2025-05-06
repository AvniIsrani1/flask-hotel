"""
Create routes for chatbot model page element.

Note:
    Author: Elijah Cortez
    Documentation: Devansh Sharma
    Created: March 2, 2025
    Modified: April 17, 2025
"""
from flask import Blueprint, jsonify, render_template, request
from HOTEL.AImodels.csv_retriever import setup_csv_retrieval, get_answer_from_csv
from HOTEL.AImodels.ai_model import load_ai_model, generate_ai_response
from ..services.response import format_response

ai_model = load_ai_model()
ai_db, ai_df = setup_csv_retrieval()


class AIRoutes:
    """
    Process a user query using CSV data first, falling back to AI.
    
    Parameters:
        user_question (str): The user's question.
        
    Returns:
        str: The formatted response to the question.
    """
    def __init__(self, app):
        self.ai_model = load_ai_model()
        self.ai_db, self.ai_df = setup_csv_retrieval()
        self.bp = Blueprint('chat', __name__)
        self.setup_routes()
        app.register_blueprint(self.bp)

    def setup_routes(self):
        self.bp.route('/chat')(self.chat)
        self.bp.route('/get_response', methods=[ "POST"])(self.get_response)


    def chat(self):
         """
         Render the chat interface.
         
         Returns:
             Template: The chat page template.
         """
         return render_template("chat.html")

    def get_response(self):
        """
        Process an AI chat request.
        
        Returns:
            JSON: The AI response as JSON.
        """
        try:
            csv_data = request.get_json()
            user_message = csv_data.get("message", "")
            
            if not user_message:
                return jsonify({"response": "No message provided."}), 400
            
            ai_response = self.process_query(user_message)
            return jsonify({"response": ai_response})
        except Exception as e:
            print(f"Error: {str(e)}")
            return jsonify({"response": "An error occurred while processing your request."}), 500


    def process_query(self, user_question):
        """
        Process a user query using CSV data first, falling back to AI.
        
        Parameters:
            user_question (str): The user's question.
            
        Returns:
            str: The formatted response to the question.
        """
        self.ai_db, self.ai_df = setup_csv_retrieval()
        csv_answer = get_answer_from_csv(self.ai_db, self.ai_df, user_question)
        formatted_response = format_response(csv_answer, user_question)

        if formatted_response:
            return formatted_response

        return generate_ai_response(self.ai_model, user_question)
