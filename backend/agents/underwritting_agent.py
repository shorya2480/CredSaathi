from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage, SystemMessage
from graph.state import AgentState
from services.data_services import credit_bureau_service
import os

llm = ChatGroq(
    model="llama-3.1-70b-versatile",
    temperature=0.7,
    groq_api_key=os.getenv("GROQ_API_KEY")
)


def underwriting_agent_node(state: AgentState) -> AgentState:
    """
    Underwriting Agent - Credit check and eligibility validation.
    
    Business Rules:
    1. Credit score must be >= 700 (reject if less)
    2. If loan amount <= pre-approved limit → Instant approval
    3. If loan amount <= 2x pre-approved limit → Need salary slip
       - Approve only if EMI <= 50% of monthly salary
    4. If loan amount > 2x pre-approved limit → Reject
    """
    
    if not state['credit_score']:
        credit_score = credit_bureau_service.get_credit_score(state['phone'])
        state['credit_score'] = credit_score
    
    # Rule 1: Check credit score
    if state['credit_score'] < 700:
        state['loan_status'] = 'rejected'
        state['rejection_reason'] = f"Credit score ({state['credit_score']}/900) is below minimum requirement of 700"
        state['current_agent'] = 'master'
        state['workflow_complete'] = True
        return state
    
    # Calculate loan ratio
    loan_ratio = state['requested_loan_amount'] / state['pre_approved_limit']
    
    # Rule 2: Instant approval if within pre-approved limit
    if loan_ratio <= 1.0:
        state['loan_status'] = 'approved'
        state['current_agent'] = 'sanction'
        
        approval_prompt = f"""You are an underwriting agent approving a loan.

Customer: {state['customer_name']}
Credit Score: {state['credit_score']}/900 
Loan Amount: ₹{state['requested_loan_amount']:,.0f}
Pre-approved Limit: ₹{state['pre_approved_limit']:,.0f}

Status: INSTANT APPROVAL (within pre-approved limit)

Generate a brief approval message (2-3 sentences):
1. Congratulate them on the approval
2. Mention their excellent credit score
3. Say the sanction letter is being generated

Keep it enthusiastic and professional."""
        
        response = llm.invoke([SystemMessage(content=approval_prompt)])
        state["messages"].append(AIMessage(content=response.content))
        
        return state
    
    elif loan_ratio <= 2.0:
        # Check if salary slip already uploaded
        if state['salary_slip_uploaded'] and state['monthly_salary']:
            # Verify EMI is within 50% of salary
            emi_ratio = (state['calculated_emi'] / state['monthly_salary']) * 100
            
            if emi_ratio <= 50:
                state['loan_status'] = 'approved'
                state['current_agent'] = 'sanction'
                
                approval_prompt = f"""You are an underwriting agent approving a loan after salary verification.

Customer: {state['customer_name']}
Monthly Salary: ₹{state['monthly_salary']:,.0f}
Monthly EMI: ₹{state['calculated_emi']:,.0f}
EMI Ratio: {emi_ratio:.1f}% of salary 

Status: APPROVED (EMI is affordable)

Generate a brief approval message (2-3 sentences):
1. Confirm salary verification is complete
2. Mention EMI is well within affordable limits
3. Say the sanction letter is being generated"""
                
                response = llm.invoke([SystemMessage(content=approval_prompt)])
                state["messages"].append(AIMessage(content=response.content))
                
                return state
            else:
                state['loan_status'] = 'rejected'
                state['rejection_reason'] = f"Monthly EMI (₹{state['calculated_emi']:,.0f}) exceeds 50% of your salary (₹{state['monthly_salary']:,.0f})"
                state['current_agent'] = 'master'
                state['workflow_complete'] = True
                return state
        else:
            # Need salary slip upload
            state['loan_status'] = 'awaiting_salary_slip'
            state['salary_slip_required'] = True
            state['current_agent'] = 'master'
            return state
    
    else:
        state['loan_status'] = 'rejected'
        state['rejection_reason'] = f"Requested amount (₹{state['requested_loan_amount']:,.0f}) exceeds 2x pre-approved limit (₹{state['pre_approved_limit'] * 2:,.0f})"
        state['current_agent'] = 'master'
        state['workflow_complete'] = True
        return state


__all__ = ["underwriting_agent_node"]