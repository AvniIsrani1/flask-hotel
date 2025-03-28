from langchain_huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
import pandas as pd
import os
import numpy as np

def setup_csv_retrieval():
    "Set up the CSV-based retrieval system."
    # Path to your hotel information CSV
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'csv_data', 'hotel_info.csv')
    
    try:
        # Load hotel information from CSV
        df = pd.read_csv(csv_path)
        
        # Combine all text columns for embedding
        df['combined'] = df.apply(lambda row: ' '.join(row.astype(str).values), axis=1)
        texts = df['combined'].tolist()
        
        # Create embeddings
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        
        # Create vector store
        db = FAISS.from_texts(texts, embeddings)
        return db
    except Exception as e:
        print(f"Error setting up CSV retrieval: {e}")
        return None

def get_answer_from_csv(db, question):
    "Get answer from CSV data based on similarity search."
    if not db:
        return None
        
    try:
        # Use the updated langchain method
        results = db.similarity_search_with_score(question, k=1)
        
        if not results:
            return None
            
        # Get the document and test term similarity 
        doc, score = results[0]
        
        # If similarity score is low do not use CSV info
        if score > 1.0:  # Adjust this threshold based on testing
            return None
            
        # Check if the content is actually relevant to the question
        if "restaurant" in question.lower() or "eat" in question.lower() or "food" in question.lower():
            if not any(term in doc.page_content.lower() for term in ["restaurant", "dining", "food", "eat"]):
                return None
                
        if "activities" in question.lower() or "things to do" in question.lower():
            if not any(term in doc.page_content.lower() for term in ["activities", "entertainment", "recreation"]):
                return None
        
        return doc.page_content
    except Exception as e:
        print(f"Error in CSV retrieval: {e}")
        return None