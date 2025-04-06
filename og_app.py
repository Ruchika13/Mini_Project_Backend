from fastapi import FastAPI
from pydantic import BaseModel

#from pydantic import BaseModel
#from transformers import pipeline
#import torch

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow all origins (you can restrict it later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific origins if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TicketSubmission(BaseModel):
    title: str
    description: str
    status: str
    priority: str
    product_id: int
    assigned_to: str

# Load the pre-trained text classification model for multi-class classification
# You can replace this model with a custom one if you have one fine-tuned for support tickets
# classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")


# # Define Pydantic model for request body
# class TicketInput(BaseModel):
#     description: str

# # Ticket categories
# ticket_categories = [
#     "Hardware Issue",
#     "Software Issue",
#     "Account Issue",
#     "Billing Issue",
#     "Network Issue",
#     "Other"
# ]

# @app.post("/categorize_ticket")
# def categorize_ticket(input_data: TicketInput):
#     # Use zero-shot classification model to classify the text into one of the categories
#     result = classifier(input_data.description, candidate_labels=ticket_categories)
#     label = result['labels'][0]  # Get the category with the highest score
#     score = result['scores'][0]  # Get the confidence score of the classification
    
#     # Return the predicted category and confidence score
#     return {
#         "category": label,
#         "confidence_score": score
#     }

@app.get("/")
def read_root():
    return {"message": "Welcome to the Ticket Categorization API!"}


@app.post("/submit_ticket")
# def submit_ticket(
#     title: str, description: str, status: str, priority: str, product_id: int, assigned_to: str
# ):
def submit_ticket(ticket: TicketSubmission):
    input = ticket.dict()
    print(input)
    # Insert into database
    # For now, just return the payload
    return input
