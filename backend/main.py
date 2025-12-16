from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models.customer import ChatRequest, ChatResponse
from graph.state import AgentState
from agents.master_agent import master_agent_node
from langchain_core.messages import HumanMessage
import uuid
from typing import Dict

# Initialize FastAPI app
app = FastAPI(
    title="Loan Agent API",
    description="Agentic AI system for personal loan processing",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # to be changed in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions: Dict[str, AgentState] = {}


def initialize_state(phone: str, session_id: str) -> AgentState:
    """
    Create a new conversation state for a customer.
    
    Args:
        phone: Customer's phone number
        session_id: Unique session identifier
    
    Returns:
        Initialized AgentState
    """
    return AgentState(
        messages=[],
        phone=phone,
        customer_name=None,
        customer_id=None,
        age=None,
        city=None,
        current_loan_details=None,
        requested_loan_amount=None,
        requested_tenure=None,
        negotiated_interest_rate=None,
        kyc_verified=False,
        verified_phone=None,
        verified_address=None,
        credit_score=None,
        pre_approved_limit=None,
        salary_slip_required=False,
        salary_slip_uploaded=False,
        monthly_salary=None,
        calculated_emi=None,
        loan_status="initial",
        rejection_reason=None,
        sanction_letter_generated=False,
        sanction_letter_path=None,
        current_agent="master",
        workflow_complete=False
    )


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "service": "Loan Agent API",
        "version": "1.0.0",
        "endpoints": {
            "chat": "POST /chat",
            "session_status": "GET /session/{session_id}/status",
            "delete_session": "DELETE /session/{session_id}"
        }
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint - handles conversation with the loan agent.
    
    Args:
        request: ChatRequest with phone, message, and optional session_id
    
    Returns:
        ChatResponse with agent's reply and updated status
    """
    
    session_id = request.session_id or str(uuid.uuid4())
    
    if session_id not in sessions:
        sessions[session_id] = initialize_state(request.phone, session_id)
    
    state = sessions[session_id]
    
    state["messages"].append(HumanMessage(content=request.message))
    
    try:
        updated_state = master_agent_node(state)
        sessions[session_id] = updated_state
        
        ai_messages = [
            msg.content for msg in updated_state["messages"] 
            if hasattr(msg, 'content') and msg.content and not isinstance(msg, HumanMessage)
        ]
        last_response = ai_messages[-1] if ai_messages else "I'm processing your request..."
        
        requires_action = None
        if updated_state["loan_status"] == "awaiting_salary_slip":
            requires_action = "upload_salary_slip"
        
        return ChatResponse(
            response=last_response,
            session_id=session_id,
            loan_status=updated_state["loan_status"],
            requires_action=requires_action
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@app.get("/session/{session_id}/status")
async def get_session_status(session_id: str):
    """
    Get current status of a loan application session.
    
    Args:
        session_id: Session identifier
    
    Returns:
        Current loan status and customer details
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = sessions[session_id]
    
    return {
        "session_id": session_id,
        "customer_name": state["customer_name"],
        "phone": state["phone"],
        "loan_status": state["loan_status"],
        "requested_amount": state["requested_loan_amount"],
        "requested_tenure": state["requested_tenure"],
        "credit_score": state["credit_score"],
        "pre_approved_limit": state["pre_approved_limit"],
        "workflow_complete": state["workflow_complete"],
        "current_agent": state["current_agent"]
    }


@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """
    Delete a conversation session.
    
    Args:
        session_id: Session identifier
    
    Returns:
        Success message
    """
    if session_id in sessions:
        del sessions[session_id]
        return {"message": "Session deleted successfully", "session_id": session_id}
    
    raise HTTPException(status_code=404, detail="Session not found")


@app.get("/sessions")
async def list_sessions():
    """
    List all active sessions (for debugging).
    
    Returns:
        List of all session IDs and their status
    """
    return {
        "total_sessions": len(sessions),
        "sessions": [
            {
                "session_id": sid,
                "customer_name": state["customer_name"],
                "phone": state["phone"],
                "status": state["loan_status"]
            }
            for sid, state in sessions.items()
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)