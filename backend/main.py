from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from models.customer import ChatRequest, ChatResponse
from graph.state import AgentState
from graph.workflow import loan_workflow
from langchain_core.messages import HumanMessage
import uuid
from typing import Dict, Optional
from pathlib import Path
import shutil

app = FastAPI(
    title="CredSaathi Loan Agent API",
    description="Agentic AI system for personal loan processing with multi-agent workflow",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions: Dict[str, AgentState] = {}

def extract_salary_from_file(file_path: Path) -> Optional[float]:
    """
    Extract monthly salary from PDF / image salary slip.
    Returns salary as float if found, else None.
    """
    text = ""

    try:
        if file_path.suffix.lower() == ".pdf":
            import pdfplumber
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""

        elif file_path.suffix.lower() in [".jpg", ".jpeg", ".png"]:
            from PIL import Image
            import pytesseract
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)

        # Extract numbers like 50000, 50,000, ₹50000
        numbers = re.findall(r"\d{2,6}", text.replace(",", ""))
        if numbers:
            return float(max(numbers, key=int))

    except Exception:
        pass

    return None


def initialize_state(phone: str, session_id: str) -> AgentState:
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
    return {
        "status": "running",
        "service": "CredSaathi Loan Agent API",
        "version": "1.0.0",
        "agents": ["Master", "Sales", "Verification", "Underwriting", "Sanction Generator"],
        "endpoints": {
            "chat": "POST /chat",
            "upload_salary": "POST /upload-salary-slip",
            "session_status": "GET /session/{session_id}/status",
            "download_letter": "GET /download-sanction-letter/{session_id}",
            "list_sessions": "GET /sessions",
            "delete_session": "DELETE /session/{session_id}"
        }
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    session_id = request.session_id or str(uuid.uuid4())
    
    if session_id not in sessions:
        sessions[session_id] = initialize_state(request.phone, session_id)
    
    state = sessions[session_id]
    
    state["messages"].append(HumanMessage(content=request.message))
    
    try:
        updated_state = loan_workflow.invoke(state)
        sessions[session_id] = updated_state
        
        ai_messages = [
            msg.content for msg in updated_state["messages"] 
            if hasattr(msg, 'content') and msg.content and not isinstance(msg, HumanMessage)
        ]
        last_response = ai_messages[-1] if ai_messages else "Processing your request..."
        
        requires_action = None
        if updated_state["loan_status"] == "awaiting_salary_slip":
            requires_action = "upload_salary_slip"
        elif updated_state["sanction_letter_generated"]:
            requires_action = "download_sanction_letter"
        
        return ChatResponse(
            response=last_response,
            session_id=session_id,
            loan_status=updated_state["loan_status"],
            requires_action=requires_action
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@app.post("/upload-salary-slip/{session_id}")
async def upload_salary_slip(
    session_id: str,
    file: UploadFile = File(...),
    # monthly_salary: float = Form(...)
):
    
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = sessions[session_id]
    
    upload_dir = Path(__file__).parent / "data" / "uploaded_salary_slips"
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_ext = Path(file.filename).suffix
    saved_filename = f"salary_slip_{state['customer_id']}_{uuid.uuid4().hex[:8]}{file_ext}"
    file_path = upload_dir / saved_filename
    
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    extracted_salary = extract_salary_from_file(file_path)

    if not extracted_salary:
        raise HTTPException(
            status_code=400,
            detail="Could not extract salary from uploaded file"
        )

    state['salary_slip_uploaded'] = True
    state['monthly_salary'] = extracted_salary
    
    state['loan_status'] = 'underwriting'
    state['current_agent'] = 'underwriting'
    
    try:
        updated_state = loan_workflow.invoke(state)
        sessions[session_id] = updated_state
        
        ai_messages = [
            msg.content for msg in updated_state["messages"] 
            if hasattr(msg, 'content') and msg.content and not isinstance(msg, HumanMessage)
        ]
        last_response = ai_messages[-1] if ai_messages else "Processing your salary slip..."
        
        return {
            "message": "Salary slip uploaded successfully",
            "status": updated_state["loan_status"],
            "response": last_response,
            "requires_action": "download_sanction_letter" if updated_state["sanction_letter_generated"] else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing salary slip: {str(e)}")


@app.get("/download-sanction-letter/{session_id}")
async def download_sanction_letter(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = sessions[session_id]
    
    if not state['sanction_letter_generated'] or not state['sanction_letter_path']:
        raise HTTPException(status_code=404, detail="Sanction letter not yet generated")
    
    pdf_path = Path(state['sanction_letter_path'])
    
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="Sanction letter file not found")
    
    return FileResponse(
        path=pdf_path,
        filename=f"sanction_letter_{state['customer_name'].replace(' ', '_')}.pdf",
        media_type="application/pdf"
    )


@app.get("/session/{session_id}/status")
async def get_session_status(session_id: str):    
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = sessions[session_id]
    
    return {
        "session_id": session_id,
        "customer_name": state["customer_name"],
        "phone": state["phone"],
        "loan_status": state["loan_status"],
        "current_agent": state["current_agent"],
        "requested_amount": state["requested_loan_amount"],
        "requested_tenure": state["requested_tenure"],
        "interest_rate": state["negotiated_interest_rate"],
        "monthly_emi": state["calculated_emi"],
        "credit_score": state["credit_score"],
        "pre_approved_limit": state["pre_approved_limit"],
        "kyc_verified": state["kyc_verified"],
        "salary_slip_required": state["salary_slip_required"],
        "salary_slip_uploaded": state["salary_slip_uploaded"],
        "sanction_letter_generated": state["sanction_letter_generated"],
        "workflow_complete": state["workflow_complete"],
        "rejection_reason": state["rejection_reason"]
    }


@app.delete("/session/{session_id}")
async def delete_session(session_id: str):    
    if session_id in sessions:
        del sessions[session_id]
        return {"message": "Session deleted successfully", "session_id": session_id}
    
    raise HTTPException(status_code=404, detail="Session not found")


@app.get("/sessions")
async def list_sessions():    
    return {
        "total_sessions": len(sessions),
        "sessions": [
            {
                "session_id": sid,
                "customer_name": state["customer_name"],
                "phone": state["phone"],
                "status": state["loan_status"],
                "current_agent": state["current_agent"],
                "workflow_complete": state["workflow_complete"]
            }
            for sid, state in sessions.items()
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)