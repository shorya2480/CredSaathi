from pydantic import BaseModel, Field
from typing import Optional

class Customer(BaseModel):
    customer_id: int
    name: str
    age: int
    city: str
    current_loan_details: str
    credit_score: int = Field(ge=300, le=900) 
    pre_approved_limit: float = Field(gt=0)  

class CRMData(BaseModel):
    name: str
    phone: str
    address: str

class CreditScore(BaseModel):
    credit_score: int = Field(ge=300, le=900)

class Offer(BaseModel):
    phone: str
    offer_amount: float
    interest_rate: float
    tenure_months: int

class ChatRequest(BaseModel):
    phone: str  
    message: str 
    session_id: Optional[str] = None 

class ChatResponse(BaseModel):
    response: str 
    session_id: str
    loan_status: str
    requires_action: Optional[str] = None