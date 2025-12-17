from langgraph.graph import StateGraph, END
from graph.state import AgentState
from agents.master_agent import master_agent_node
from agents.sales_agent import sales_agent_node
from agents.verification_agent import verification_agent_node
from agents.underwriting_agent import underwriting_agent_node
from agents.fraud_agent import fraud_agent_node
from agents.advisor_agent import advisor_agent_node
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
    After underwriting, ALWAYS go to fraud detection (sequential as per requirements).
    
    Routes:
    - Always → fraud (sequential fraud detection after underwriting)
    """
    return 'fraud'


def route_after_fraud(state: AgentState) -> str:
    """
    Route based on fraud detection results.
    
    Routes:
    - If high risk (fraud detected), reject → master_final
    - If medium risk (manual review), flag → master_final
    - If low risk and approved, go to sanction
    - If low risk but not approved, go to master_final
    """
    fraud_risk = state.get('fraud_risk_score', 0)
    status = state.get('loan_status', 'unknown')
    
    if fraud_risk >= 70 or status == 'rejected':
        # High risk fraud or already rejected
        return 'advisor'
    elif fraud_risk >= 40:
        # Medium risk - manual review
        return 'master_final'
    elif status == 'approved':
        # Low fraud risk and approved
        return 'sanction'
    else:
        # Other status (awaiting_salary_slip, etc)
        return 'master_final'


def route_after_sanction(state: AgentState) -> str:
    """
    After sanction letter generation, go to master for final congratulations.
    """
    return 'master_final'


def route_after_advisor(state: AgentState) -> str:
    """
    After advisor guidance (post-rejection coaching), end workflow.
    """
    return END


def create_loan_workflow():
    """
    Create the complete LangGraph workflow with Fraud & Advisor agents.
    
    Flow:
    START → Master (greet) → Sales (negotiate) → Verification (KYC) 
    → Underwriting (credit check) → Fraud (compliance check)
    → Sanction (PDF) / Advisor (coaching) → Master (final) → END
    
    New: Fraud agent runs sequentially after underwriting
    New: Advisor agent provides post-rejection guidance
    """
    
    workflow = StateGraph(AgentState)
    
    # Add all nodes
    workflow.add_node("master", master_agent_node)
    workflow.add_node("sales", sales_agent_node)
    workflow.add_node("verification", verification_agent_node)
    workflow.add_node("underwriting", underwriting_agent_node)
    workflow.add_node("fraud", fraud_agent_node)
    workflow.add_node("sanction", sanction_generator_node)
    workflow.add_node("advisor", advisor_agent_node)
    workflow.add_node("master_final", master_agent_node)  # For final messages
    
    workflow.set_entry_point("master")
    
    # Master → Sales/End
    workflow.add_conditional_edges(
        "master",
        route_after_master,
        {
            "sales": "sales",
            END: END
        }
    )
    
    # Sales → Verification/End
    workflow.add_conditional_edges(
        "sales",
        route_after_sales,
        {
            "verification": "verification",
            END: END
        }
    )
    
    # Verification → Underwriting
    workflow.add_conditional_edges(
        "verification",
        route_after_verification,
        {
            "underwriting": "underwriting"
        }
    )
    
    # Underwriting → Fraud (sequential)
    workflow.add_conditional_edges(
        "underwriting",
        route_after_underwriting,
        {
            "fraud": "fraud"
        }
    )
    
    # Fraud → Sanction/Advisor/Master
    workflow.add_conditional_edges(
        "fraud",
        route_after_fraud,
        {
            "sanction": "sanction",
            "advisor": "advisor",
            "master_final": "master_final",
            END: END
        }
    )
    
    # Sanction → Master Final
    workflow.add_conditional_edges(
        "sanction",
        route_after_sanction,
        {
            "master_final": "master_final"
        }
    )
    
    # Advisor → End
    workflow.add_conditional_edges(
        "advisor",
        route_after_advisor,
        {
            END: END
        }
    )
    
    # Master Final → End
    workflow.add_edge("master_final", END)
    
    return workflow.compile()


loan_workflow = create_loan_workflow()

__all__ = ["loan_workflow", "create_loan_workflow"]