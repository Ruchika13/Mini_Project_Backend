from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Define the FastAPI app
app = FastAPI()

# Load the trained model and vectorizer
try:
    model = joblib.load('naive_bayes_model.pkl')
    vectorizer = joblib.load('tfidf_vectorizer.pkl')
    logging.info("Model and vectorizer loaded successfully.")
except Exception as e:
    logging.error(f"Error loading model or vectorizer: {e}")
    raise HTTPException(status_code=500, detail="Model loading error")

# Request body schema
class TicketRequest(BaseModel):
    description: str

# FastAPI route to predict ticket type
@app.post("/predict_ticket_type")
async def predict_ticket(ticket: TicketRequest):
    try:
        # Transform the input description using the loaded vectorizer
        ticket_tfidf = vectorizer.transform([ticket.description])
        # Predict the category using the trained model
        predicted_category = model.predict(ticket_tfidf)[0]
        return {"predicted_category": predicted_category}
    except Exception as e:
        logging.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail="Prediction error")
