from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2 import sql
import csv
from fastapi import UploadFile, File
from io import StringIO

# FastAPI app
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ticket model
class TicketSubmission(BaseModel):
    title: str
    description: str
    status: str
    priority: str
    product_id: int
    assigned_to: str

# PostgreSQL DB credentials
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "stc",
    "user": "postgres",
    "password": "NR1316"
}

# Create DB connection
def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Ticket Categorization API!"}

@app.post("/submit_ticket")
def submit_ticket(ticket: TicketSubmission):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        insert_query = sql.SQL("""
            INSERT INTO tickets (title, description, status, priority, product_id, assigned_to)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING ticket_id;
        """)

        values = (
            ticket.title,
            ticket.description,
            ticket.status,
            ticket.priority,
            ticket.product_id,
            ticket.assigned_to
        )

        cursor.execute(insert_query, values)
        ticket_id = cursor.fetchone()[0]
        conn.commit()

        cursor.close()
        conn.close()

        return {"message": "Ticket submitted successfully", "ticket_id": ticket_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    
@app.get("/tickets")
def get_all_tickets():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                t.ticket_id, t.title, t.description, t.status, t.priority, t.product_id, 
                t.created_at, t.updated_at,
                u.first_name, u.last_name, u.email, u.role
            FROM tickets t
            JOIN users u ON t.assigned_to = u.user_id
            ORDER BY t.ticket_id DESC;
        """)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        tickets = [
            {
                "ticket_id": row[0],
                "title": row[1],
                "description": row[2],
                "status": row[3],
                "priority": row[4],
                "product_id": row[5],
                "created_at": row[6],
                "updated_at": row[7],
                "assigned_to_first_name": row[8],
                "assigned_to_last_name": row[9],
                "assigned_to_email": row[10],
                "assigned_to_role": row[11]
            }
            for row in rows
        ]
        return tickets

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@app.get("/products")
def get_products():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT product_id, product_name FROM product ORDER BY product_name;")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        products = [{"product_id": row[0], "product_name": row[1]} for row in rows]
        return products

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


@app.get("/users")
def get_users():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, first_name, last_name FROM users ORDER BY first_name;")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        users = [{"user_id": row[0], "name": f"{row[1]} {row[2]}"} for row in rows]
        return users

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    
@app.post("/import_tickets_csv")
async def import_tickets_csv(file: UploadFile = File(...)):
    try:
        content = await file.read()
        decoded = content.decode('utf-8')
        csv_reader = csv.DictReader(StringIO(decoded))

        inserted_ids = []
        conn = get_db_connection()
        cursor = conn.cursor()

        for row in csv_reader:
            title = row.get("Ticket Subject", "").strip()
            description = row.get("Ticket Description", "").strip()
            status = row.get("Ticket Status", "").strip()
            priority = row.get("Ticket Priority", "").strip()

            # Optional: you may need default or dummy values for missing fields
            product_id = None  # or fetch based on logic
            assigned_to = None
            customer_id = None

            if not title or not status or not priority:
                continue  # Skip rows with missing essential fields

            cursor.execute("""
                INSERT INTO tickets (title, description, status, priority, product_id, assigned_to, customer_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING ticket_id;
            """, (title, description, status, priority, product_id, assigned_to, customer_id))

            ticket_id = cursor.fetchone()[0]
            inserted_ids.append(ticket_id)

        conn.commit()
        cursor.close()
        conn.close()

        return {"message": f"{len(inserted_ids)} tickets imported successfully.", "ticket_ids": inserted_ids}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error importing tickets: {e}")

