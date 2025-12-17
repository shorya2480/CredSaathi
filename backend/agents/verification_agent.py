from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage, SystemMessage
from graph.state import AgentState
import os

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.7,
    groq_api_key=os.getenv("GROQ_API_KEY")
)


def verification_agent_node(state: AgentState) -> AgentState:
    """
    Verification Agent - Verifies KYC details and requests salary slip if needed.
    
    Workflow:
    1. Check if KYC already verified
    2. Verify phone and address from CRM (already done in master agent)
    3. Request salary slip upload if needed
    4. Inform customer about verification
    5. Move to underwriting stage
    """
    
    if state['verified_phone'] and state['verified_address']:
        state['kyc_verified'] = True
    
    # ========== CHECK IF SALARY SLIP NEEDED ==========
    
    # If requested loan is between 1-2x pre-approved limit, need salary slip for EMI check
    if state['requested_loan_amount'] and state['pre_approved_limit']:
        loan_ratio = state['requested_loan_amount'] / state['pre_approved_limit']
        
        if 1.0 < loan_ratio <= 2.0:
            state['salary_slip_required'] = True
        else:
            state['salary_slip_required'] = False
    
    # ========== GENERATE KYC MESSAGE ==========
    
    verification_prompt = f"""You are a verification agent at a bank.

Customer: {state['customer_name']}
Phone: {state['verified_phone']}
Address: {state['verified_address']}

KYC Status: {'Verified' if state['kyc_verified'] else 'Failed'}
Loan Requested: ₹{state['requested_loan_amount']:,.0f}
Salary Slip Required: {'Yes' if state['salary_slip_required'] else 'No'}

Generate a brief verification message (2-3 sentences):
1. Confirm that KYC verification is complete
2. Mention that details are verified from our records
3. {'If salary slip needed: Say you need salary slip for final verification' if state['salary_slip_required'] else 'Say you are proceeding with credit check'}

Keep it professional and reassuring."""
    
    response = llm.invoke([SystemMessage(content=verification_prompt)])
    state["messages"].append(AIMessage(content=response.content))
    
    # ========== UPDATE STATUS & ROUTE ==========
    
    state["loan_status"] = "underwriting"
    state["current_agent"] = "underwriting"
    
    return state


__all__ = ["verification_agent_node"]