from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

app = FastAPI()

# Allow CORS for the frontend running at http://127.0.0.1:5500
origins = [
    "http://127.0.0.1:5500",  # Replace with your frontend's URL if different
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the table schema
table_schema = {
    "Clients": {
        "columns": ["ClientID", "ClientName", "ContactPerson", "Email", "Phone", "Address", "City", "State", "Country", "PostalCode", "CreatedAt"],
        "primary_key": "ClientID"
    },
    "Employees": {
        "columns": ["EmployeeID", "FirstName", "LastName", "Email", "Phone", "HireDate", "JobTitle", "Department", "Salary", "Address", "City", "State", "Country", "PostelCode"],
        "primary_key": "EmployeeID"
    },
    "ProjectAssignments": {
        "columns": ["AssignmentID", "ProjectID", "EmployeeID", "AssignedDate", "Role"],
        "primary_key": "AssignmentID"
    },
    "Projects": {
        "columns": ["ProjectID", "ProjectName", "ClientID", "StartDate", "EndDate", "Status", "Budget", "Description"],
        "primary_key": "ProjectID"
    },
    "Services": {
        "columns": ["ServiceID", "ServiceName", "Description", "Price"],
        "primary_key": "ServiceID"
    }
}

# Load tokenizer and model for your custom NL2SQL model
model_name = 'charanhu/text_to_sql_5'
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

# Model to handle incoming chat messages
class ChatMessage(BaseModel):
    content: str

# Function to handle user input and generate response
def answer_question(question, sql_result, schema):
    try:
        # Tokenize input and feed into your NL2SQL model
        inputs = tokenizer(question, return_tensors="pt")
        with torch.no_grad():
            outputs = model(**inputs)
            generated_sql = tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]

        # Here you can use the schema to validate or modify the generated SQL query if needed
        # Replace with actual SQL query execution and result handling
        # For now, returning the generated SQL query as a response
        return {"response": generated_sql}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Route to handle user input and generate response
@app.post("/chat/")
async def chat(chat_message: ChatMessage):
    try:
        prompt = chat_message.content

        # Example SQL result (replace with actual SQL query execution and result)
        sql_result = "Example SQL result"

        # Get answer based on question and SQL result using your NL2SQL model
        response = answer_question(prompt, sql_result, table_schema)

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
