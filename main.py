from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import logging

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logging.basicConfig(level=logging.DEBUG)

# Load the model and vectorizer with error handling
try:
    model = joblib.load('naive_bayes_model.pkl')
    vectorizer = joblib.load('tfidf_vectorizer.pkl')
    logging.info("Model and vectorizer loaded successfully.")
except Exception as e:
    logging.error(f"Loading error: {e}")
    raise HTTPException(status_code=500, detail=f"Loading error: {e}")

class TicketRequest(BaseModel):
    description: str

@app.post("/predict_ticket_type")
async def predict_ticket(ticket: TicketRequest):
    try:
        # Validate input
        if not ticket.description.strip():
            raise HTTPException(status_code=400, detail="Empty description.")

        # Transform and predict
        ticket_tfidf = vectorizer.transform([ticket.description])
        predicted_category = model.predict(ticket_tfidf)[0]
        return {"predicted_category": predicted_category}

    except Exception as e:
        logging.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction error: {e}")
