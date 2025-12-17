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
    Verification Agent - Verifies KYC details.
    
    Workflow:
    1. Check if KYC already verified
    2. Verify phone and address from CRM (already done in master agent)
    3. Inform customer about verification
    4. Move to underwriting stage
    """
    
    if state['verified_phone'] and state['verified_address']:
        state['kyc_verified'] = True
    
    verification_prompt = f"""You are a verification agent at a bank.

Customer: {state['customer_name']}
Phone: {state['verified_phone']}
Address: {state['verified_address']}

KYC Status: {'Verified' if state['kyc_verified'] else 'Failed'}

Generate a brief verification message (2-3 sentences):
1. Confirm that KYC verification is complete
2. Mention that details are verified from our records
3. Say you're now proceeding with credit check

Keep it professional and reassuring."""
    
    response = llm.invoke([SystemMessage(content=verification_prompt)])
    state["messages"].append(AIMessage(content=response.content))
    
    # Move to underwriting
    state["loan_status"] = "underwriting"
    state["current_agent"] = "underwriting"
    
    return state


__all__ = ["verification_agent_node"]