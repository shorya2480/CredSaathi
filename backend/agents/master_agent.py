from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from graph.state import AgentState
from services.data_services import crm_service, customer_service  
import os

llm = ChatGroq(
    model="llama-3.1-8b-instant",  
    temperature=0.7,
    groq_api_key=os.getenv("GROQ_API_KEY")
)


def master_agent_node(state: AgentState) -> AgentState:    
    user_messages = [msg for msg in state["messages"] if isinstance(msg, HumanMessage)]
    
    if state["loan_status"] == "initial":
        crm_data = crm_service.verify_customer(state["phone"])
        
        if not crm_data:
            state["messages"].append(
                AIMessage(content="I'm sorry, I couldn't find your details in our system. Please contact customer support.")
            )
            state["workflow_complete"] = True
            return state
        
        customer = customer_service.get_customer_by_name(crm_data.name)
        
        state["customer_name"] = crm_data.name
        state["verified_phone"] = crm_data.phone
        state["verified_address"] = crm_data.address
        
        if customer:
            state["customer_id"] = customer.customer_id
            state["age"] = customer.age
            state["city"] = customer.city
            state["current_loan_details"] = customer.current_loan_details
            state["credit_score"] = customer.credit_score
            state["pre_approved_limit"] = customer.pre_approved_limit
        
        greeting_prompt = f"""You are a friendly loan officer at a bank in India.

Customer Details:
- Name: {crm_data.name}
- City: {state.get('city', 'N/A')}
- Existing loans: {state.get('current_loan_details', 'None')}

Write a warm, professional greeting (2-3 sentences):
1. Welcome them by name
2. Say you can help with personal loans
3. Ask what loan amount they need

Keep it natural and conversational."""
        
        response = llm.invoke([SystemMessage(content=greeting_prompt)])
        
        state["messages"].append(AIMessage(content=response.content))
        state["loan_status"] = "negotiating"
        state["current_agent"] = "sales"
        
        return state
    
    elif state["loan_status"] == "approved":
        success_message = f"""🎉 Congratulations {state['customer_name']}!

Your personal loan has been APPROVED! ✅

Loan Details:
Loan Amount: ₹{state['requested_loan_amount']:,.0f}
Tenure: {state['requested_tenure']} months
Interest Rate: {state['negotiated_interest_rate']}% p.a.
Monthly EMI: ₹{state['calculated_emi']:,.0f}

Your sanction letter is ready for download!

Thank you for choosing our services! 🙏"""
        
        state["messages"].append(AIMessage(content=success_message))
        state["workflow_complete"] = True
        return state
    
    elif state["loan_status"] == "rejected":
        rejection_message = f"""Dear {state['customer_name']},

We regret to inform you that we cannot approve your loan application at this time. ❌

Reason: {state['rejection_reason']}

What you can do:
• Improve your credit score (current: {state.get('credit_score', 'N/A')}/900)
• Apply for a smaller loan amount
• Clear existing loan dues
• Reapply after 3 months

For assistance, contact our support team.

Thank you for your interest."""
        
        state["messages"].append(AIMessage(content=rejection_message))
        state["workflow_complete"] = True
        return state
    
    elif state["loan_status"] == "awaiting_salary_slip":
        salary_message = f"""📄 Document Required

To proceed with your loan of ₹{state['requested_loan_amount']:,.0f}, we need to verify your income.

Please upload your latest salary slip (last 1 month).

Why we need this:
• Your requested loan is {state['requested_loan_amount'] / state['pre_approved_limit']:.1f}x your pre-approved limit
• We need to ensure EMI (₹{state['calculated_emi']:,.0f}) is within 50% of your salary

Accepted formats: PDF, JPG, PNG
Max file size: 5MB

Once uploaded, approval is instant! ⚡"""
        
        state["messages"].append(AIMessage(content=salary_message))
        return state
    
    else:
        return state


__all__ = ["master_agent_node"]