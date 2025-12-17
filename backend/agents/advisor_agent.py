"""
Financial Advisor Agent - Post-Rejection Coaching
Provides personalized financial guidance and recommendations to rejected applicants.
Helps them understand why they were rejected and provides actionable improvement steps.

Features:
1. Personalized financial coaching
2. Debt consolidation suggestions
3. Credit improvement roadmap
4. Alternative loan products
5. Savings & investment tips
"""

from typing import Dict
import os
from dotenv import load_dotenv
from groq import Groq
from langchain_core.messages import AIMessage

# Load environment variables
load_dotenv()


def _get_api_key() -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("Missing GROQ_API_KEY in environment or .env")
    return api_key


class AdvisorAgent:
    """
    Financial Advisor Agent for CredSaathi
    Provides coaching and guidance for rejected loan applicants
    """
    
    def __init__(self) -> None:
        self.client = Groq(api_key=_get_api_key())
    
    def generate_credit_improvement_plan(self, state: Dict) -> str:
        """
        Generate a personalized credit improvement plan based on:
        - Current credit score
        - Rejection reason
        - Financial profile
        """
        credit_score = state.get("credit_score", "unknown")
        rejection_reason = state.get("rejection_reason", "Unknown")
        customer_name = state.get("customer_name", "User")
        requested_amount = state.get("requested_loan_amount", "N/A")
        
        prompt = f"""You are a friendly financial advisor helping someone improve their financial health.

Customer: {customer_name}
Current Credit Score: {credit_score}
Requested Loan: ₹{requested_amount:,.0f}
Rejection Reason: {rejection_reason}

Create a personalized, encouraging 3-step credit improvement roadmap for the next 6-12 months. Focus on:
1. Immediate actions (this month)
2. Medium-term goals (3-6 months)
3. Long-term objectives (6-12 months)

Be empathetic, practical, and specific. Include estimated credit score improvement at each stage."""
        
        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a compassionate and knowledgeable financial advisor. Provide practical, actionable advice to help customers improve their financial health."
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            return "I'll help you create a plan to improve your financial health. Let's focus on credit score improvement first."
    
    def generate_debt_consolidation_advice(self, state: Dict) -> str:
        """
        Generate debt consolidation suggestions if applicant has existing loans
        """
        current_loans = state.get("current_loan_details")
        monthly_salary = state.get("monthly_salary", 0)
        customer_name = state.get("customer_name", "User")
        
        if not current_loans:
            return ""
        
        prompt = f"""You are a financial advisor specializing in debt management.

Customer: {customer_name}
Monthly Salary: ₹{monthly_salary:,.0f}
Current Loan Details: {current_loans}

Provide specific, actionable debt consolidation strategies. Explain:
1. Benefits of consolidating their debt
2. Expected reduction in monthly EMI
3. Recommended consolidation timeline
4. How to approach their current lenders

Be encouraging but realistic about the process."""
        
        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert debt consolidation advisor. Provide practical strategies to reduce financial burden."
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            return ""
    
    def generate_alternative_products(self, state: Dict) -> str:
        """
        Suggest alternative loan products or financial solutions
        """
        requested_amount = state.get("requested_loan_amount", 0)
        credit_score = state.get("credit_score", 0)
        monthly_salary = state.get("monthly_salary", 0)
        customer_name = state.get("customer_name", "User")
        
        prompt = f"""You are a financial product advisor at CredSaathi.

Customer: {customer_name}
Requested Loan Amount: ₹{requested_amount:,.0f}
Credit Score: {credit_score}
Monthly Salary: ₹{monthly_salary:,.0f}

Suggest 2-3 alternative financial products or solutions they might qualify for:
1. Smaller personal loan with lower amount
2. Secured loan options (gold, property-backed)
3. Group lending or peer-to-peer options
4. Government schemes they might be eligible for

For each option, explain:
- Why they might qualify
- Expected interest rates
- Timeline to approval
- How to apply"""
        
        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a knowledgeable financial product advisor. Help customers find alternative solutions that match their profile."
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            return ""
    
    def generate_comprehensive_guidance(self, state: Dict) -> str:
        """
        Generate comprehensive post-rejection guidance combining all advice
        """
        customer_name = state.get("customer_name", "User")
        rejection_reason = state.get("rejection_reason", "Your application did not meet our current lending criteria")
        credit_score = state.get("credit_score", "unknown")
        
        # Build comprehensive guidance
        guidance_parts = []
        
        # Opening with empathy
        opening = f"""Hello {customer_name},

Thank you for applying with CredSaathi. While we couldn't approve your current application (Reason: {rejection_reason}), we believe in your financial potential and want to help you succeed.

Below is a personalized action plan to strengthen your financial profile and make you eligible for credit in the future."""
        
        guidance_parts.append(opening)
        
        # Add credit improvement plan
        credit_plan = self.generate_credit_improvement_plan(state)
        if credit_plan:
            guidance_parts.append("\n📈 YOUR CREDIT IMPROVEMENT ROADMAP\n" + "=" * 50)
            guidance_parts.append(credit_plan)
        
        # Add debt consolidation advice if applicable
        debt_advice = self.generate_debt_consolidation_advice(state)
        if debt_advice:
            guidance_parts.append("\n💰 DEBT CONSOLIDATION OPTIONS\n" + "=" * 50)
            guidance_parts.append(debt_advice)
        
        # Add alternative products
        alternatives = self.generate_alternative_products(state)
        if alternatives:
            guidance_parts.append("\n🎯 ALTERNATIVE LOAN PRODUCTS YOU MAY QUALIFY FOR\n" + "=" * 50)
            guidance_parts.append(alternatives)
        
        # Closing with encouragement
        closing = """
✨ NEXT STEPS
1. Start implementing the credit improvement plan this month
2. Monitor your credit score regularly
3. Revisit your application in 3-6 months
4. Contact our team if you have questions: support@credsaathi.com

We're here to support your financial journey. You've got this! 💪"""
        
        guidance_parts.append(closing)
        
        return "\n".join(guidance_parts)
    
    def process_post_rejection_guidance(self, state: Dict) -> Dict:
        """
        Main advisor process for rejected applicants.
        Generates comprehensive guidance and updates state.
        """
        
        # Only process if application was rejected
        if state.get("loan_status") != "rejected":
            return state
        
        # Generate comprehensive guidance
        guidance = self.generate_comprehensive_guidance(state)
        
        # Add guidance to chat messages
        state["messages"].append(AIMessage(content=guidance))
        
        # Store advisor recommendations in state
        state["advisor_guidance_provided"] = True
        state["advisor_recommendations"] = {
            "credit_improvement_plan": self.generate_credit_improvement_plan(state),
            "debt_consolidation_advice": self.generate_debt_consolidation_advice(state),
            "alternative_products": self.generate_alternative_products(state)
        }
        
        # Set workflow status
        state["current_agent"] = "advisor"
        state["workflow_complete"] = True
        
        return state


# Main advisor agent node for workflow
def advisor_agent_node(state: Dict) -> Dict:
    """
    Financial advisor node for LangGraph workflow.
    Triggers after rejection to provide coaching and guidance.
    """
    agent = AdvisorAgent()
    return agent.process_post_rejection_guidance(state)


# Standalone functions for quick advice
def get_credit_improvement_tips(credit_score: int, months_available: int = 6) -> str:
    """
    Quick tips to improve credit score
    """
    client = Groq(api_key=_get_api_key())
    
    prompt = f"""Provide 5 quick, actionable tips to improve a credit score of {credit_score} within {months_available} months.

Format as a numbered list with:
- Tip description
- Expected impact on credit score
- Timeline to see results

Keep each tip to 2-3 sentences."""
    
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a credit score improvement expert. Provide practical tips."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,
        )
        return response.choices[0].message.content
    except Exception as e:
        return "Focus on: 1) Pay bills on time, 2) Reduce credit utilization, 3) Don't close old accounts, 4) Dispute errors, 5) Avoid multiple applications."


def get_loan_eligibility_timeline(current_score: int, target_score: int = 700) -> str:
    """
    Estimate timeline to reach target credit score
    """
    client = Groq(api_key=_get_api_key())
    
    score_gap = target_score - current_score
    
    prompt = f"""Based on a current credit score of {current_score} and a target of {target_score} (gap of {score_gap} points):

1. Provide a realistic timeline (in months) to reach the target
2. List the main factors that will drive the improvement
3. Suggest monthly milestones
4. Identify potential obstacles and how to overcome them

Keep response concise but actionable."""
    
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a credit improvement timeline expert."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Timeline to improve from {current_score} to {target_score}: Approximately 3-6 months with consistent effort on payment history and credit utilization."
