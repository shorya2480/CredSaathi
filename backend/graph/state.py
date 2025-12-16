from typing import TypedDict, Annotated, Literal, Optional
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """
    This state object is passed between all agents.
    Each agent reads from it and updates it.
    
    The 'Annotated[list, add_messages]' means messages will be appended,
    not replaced.
    """
    
    # Chat history 
    messages: Annotated[list, add_messages] 
    
    phone: str  
    customer_name: Optional[str] 
    customer_id: Optional[int]  
    age: Optional[int]
    city: Optional[str]
    current_loan_details: Optional[str]
    
    # These get filled during sales conversation
    requested_loan_amount: Optional[float]
    requested_tenure: Optional[int] 
    negotiated_interest_rate: Optional[float] 
    
    # Verification agent data
    kyc_verified: bool  
    verified_phone: Optional[str]  
    verified_address: Optional[str] 
    
    
    credit_score: Optional[int] 
    pre_approved_limit: Optional[float] 
    
    # Salary related
    salary_slip_required: bool 
    salary_slip_uploaded: bool  
    monthly_salary: Optional[float]  
    calculated_emi: Optional[float] 
    
    loan_status: Literal[
        "initial", 
        "negotiating",  
        "verifying",  
        "underwriting",  
        "awaiting_salary_slip",  
        "approved", 
        "rejected"  
    ]
    
    rejection_reason: Optional[str]  
    
    sanction_letter_generated: bool
    sanction_letter_path: Optional[str] 
    
    current_agent: str
    workflow_complete: bool  