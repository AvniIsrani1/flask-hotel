from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import pandas as pd
import os
import numpy as np

"""
Module for retrieval of CSV information. 

Note:
    Author: Elijah Cortez
    Documentation: Elijah Cortez
    Created: February 27, 2025
    Modified: April 17, 2025
"""

def setup_csv_retrieval():
    """
    Set up the CSV-based information retrieval system using FAISS and Hugging Face embeddings.

    Parameters:
        None

    Returns:
        tuple: A tuple (db, df) where db is a FAISS vector store and df is the original CSV DataFrame.
    
    Raises:
        Exception: Caught internally, and returns (None, None).
    """
    # Path construction
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(os.path.dirname(current_dir), 'csv_data', 'hotel_info.csv')
    
    print(f"Looking for CSV at: {csv_path}")
    
    try:
        # Check if file exists before trying to read it
        if not os.path.exists(csv_path):
            print(f"CSV file not found at: {csv_path}")
            return None, None
            
        # Load hotel information from CSV
        df = pd.read_csv(csv_path)
        
        if df.empty:
            print("CSV file is empty")
            return None, None
        
        # Format how we store the data similar to BugginFace.py
        df["combined"] = df.apply(
            lambda row: f"{row['category']} - {row['sub_category']}: {row['description']}", 
            axis=1
        )
        
        texts = df['combined'].tolist()
        
        # Create embeddings
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        
        # Create vector store
        db = FAISS.from_texts(texts, embeddings)
        print("Successfully created FAISS index")
        return db, df  # Return both db and df
    except Exception as e:
        print(f"Error setting up CSV retrieval: {e}")
        return None, None  # Return None for both when there's an error

def get_answer_from_csv(db, df, question):
    """
    Get the most relevant answer from the CSV dataset based on the user's question using FAISS similarity.

    Parameters:
        db (FAISS): The vector database of embedded CSV content.
        df (DataFrame): The raw CSV content as a Pandas DataFrame.
        question (str): The user's input question.

    Returns:
        str | None: The best matching text from the CSV or None if no suitable result is found.

    Raises:
        Exception: Caught internally, and returns None.
    """
    if db is None or df is None or df.empty:
        print("Database or DataFrame is None or empty")
        return None
        
    try:
        # Use the updated langchain method
        results = db.similarity_search_with_score(question, k=1)
        
        if not results:
            return None
            
        # Get the document and score
        doc, score = results[0]
        print(f"Found document with score: {score}")
        
        # If similarity score is low do not use CSV info
        if score > 1.5:  # Adjust this threshold based on testing
            print(f"Score {score} exceeds threshold, not using CSV info")
            return None
        
        # Return the document content - the format_response function will extract just the description
        print(f"Returning document content: {doc.page_content}")
        return doc.page_content
        
    except Exception as e:
        print(f"Error in CSV retrieval: {e}")
        return None