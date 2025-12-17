from langgraph.graph import StateGraph, END
from graph.state import AgentState
from agents.master_agent import master_agent_node
from agents.sales_agent import sales_agent_node
from agents.verification_agent import verification_agent_node
from agents.underwritting_agent import underwriting_agent_node
from agents.sanction_generator import sanction_generator_node


def route_after_master(state: AgentState) -> str:
    """
    Decide where to go after Master Agent.
    
    Routes:
    - If initial greeting, go to sales
    - If approved/rejected/awaiting_salary, end workflow
    - Otherwise, continue to appropriate agent
    """
    status = state['loan_status']
    
    if status == 'negotiating':
        return 'sales'
    elif status in ['approved', 'rejected', 'awaiting_salary_slip']:
        return END
    else:
        return END


def route_after_sales(state: AgentState) -> str:
    """
    After sales, always go to verification if we have complete loan details.
    """
    if state['requested_loan_amount'] and state['requested_tenure']:
        return 'verification'
    else:
        # Still collecting information, stay in sales
        return END


def route_after_verification(state: AgentState) -> str:
    """
    After verification, always go to underwriting.
    """
    return 'underwriting'


def route_after_underwriting(state: AgentState) -> str:
    """
    Route based on underwriting decision.
    
    Routes:
    - If approved, go to sanction letter generation
    - If rejected or needs salary slip, go back to master for final message
    - Otherwise, end
    """
    status = state['loan_status']
    
    if status == 'approved':
        return 'sanction'
    elif status == 'rejected':
        return 'master_final'
    elif status == 'awaiting_salary_slip':
        return 'master_final'
    else:
        return END


def route_after_sanction(state: AgentState) -> str:
    """
    After sanction letter generation, go to master for final congratulations.
    """
    return 'master_final'


def create_loan_workflow():
    """
    Create the complete LangGraph workflow.
    
    Flow:
    START → Master (greet) → Sales (negotiate) → Verification (KYC) 
    → Underwriting (credit check) → Sanction (PDF) → Master (final) → END
    """
    
    workflow = StateGraph(AgentState)
    
    workflow.add_node("master", master_agent_node)
    workflow.add_node("sales", sales_agent_node)
    workflow.add_node("verification", verification_agent_node)
    workflow.add_node("underwriting", underwriting_agent_node)
    workflow.add_node("sanction", sanction_generator_node)
    workflow.add_node("master_final", master_agent_node)  # For final messages
    
    workflow.set_entry_point("master")
    
    workflow.add_conditional_edges(
        "master",
        route_after_master,
        {
            "sales": "sales",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "sales",
        route_after_sales,
        {
            "verification": "verification",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "verification",
        route_after_verification,
        {
            "underwriting": "underwriting"
        }
    )
    
    workflow.add_conditional_edges(
        "underwriting",
        route_after_underwriting,
        {
            "sanction": "sanction",
            "master_final": "master_final",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "sanction",
        route_after_sanction,
        {
            "master_final": "master_final"
        }
    )
    
    workflow.add_edge("master_final", END)
    
    return workflow.compile()


loan_workflow = create_loan_workflow()

__all__ = ["loan_workflow", "create_loan_workflow"]