from fastapi import FastAPI
from pydantic import BaseModel
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import joblib

# Define the FastAPI app
app = FastAPI()

# Load the trained model and vectorizer (ensure you've saved them earlier)
model = joblib.load('naive_bayes_model.pkl')          # Save your model after training
vectorizer = joblib.load('tfidf_vectorizer.pkl')      # Save your vectorizer after fitting

# Request body schema
class TicketRequest(BaseModel):
    description: str

# FastAPI route to predict ticket type
@app.post("/predict_ticket_type")
async def predict_ticket(ticket: TicketRequest):
    # Transform the input description using the loaded vectorizer
    ticket_tfidf = vectorizer.transform([ticket.description])
    
    # Predict the category using the trained model
    predicted_category = model.predict(ticket_tfidf)[0]
    
    # Return the predicted category
    return {"predicted_category": predicted_category}

# To run this API server:
# Run this in your terminal: uvicorn script_name:app --reload
