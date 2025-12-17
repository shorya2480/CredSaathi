"""
Fraud Detection Agent - BFSI Compliance Layer
Detects suspicious patterns, document mismatches, and anomalies in loan applications.
Runs sequentially after Underwriting agent.

Fraud Detection Rules:
1. Salary anomalies: < ₹10K (rejected), missing fields (manual review)
2. Impossible jumps: Previous salary 2L → Current 15L (fraud flag)
3. Document mismatch: KYC name ≠ Salary slip extracted name
4. Duplicate applications: Same phone across multiple rejections
5. Suspicious patterns: Fake address, inconsistent credit history
"""

from typing import Dict
import json
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


# In-memory fraud database (will be replaced with SQLite later)
fraud_database = {
    "rejected_phones": {},  # {phone: count_of_rejections}
    "flagged_applications": [],
    "suspicious_addresses": set()
}


class FraudAgent:
    """
    BFSI Fraud Detection Agent for CredSaathi
    Implements compliance-grade fraud checks for loan applications
    """
    
    def __init__(self) -> None:
        self.client = Groq(api_key=_get_api_key())
        self.fraud_checks = {
            "salary_anomalies": [],
            "document_mismatches": [],
            "duplicate_applications": False,
            "suspicious_patterns": [],
            "risk_score": 0.0,
            "recommendation": "APPROVE"
        }
    
    def detect_salary_anomalies(self, state: Dict) -> Dict:
        """
        Detect salary-related fraud patterns:
        - Salary < ₹10,000 → Reject
        - Missing salary data → Flag for manual review
        - Salary jumps > 100% → Fraud flag
        """
        anomalies = []
        severity = "low"
        
        monthly_salary = state.get("monthly_salary")
        
        # Rule 1: Salary too low (< ₹10,000)
        if monthly_salary and monthly_salary < 10000:
            anomalies.append({
                "type": "low_salary",
                "message": f"Salary ₹{monthly_salary:,.0f} is below minimum threshold of ₹10,000",
                "severity": "high",
                "action": "reject"
            })
            severity = "high"
        
        # Rule 2: Missing salary data when required
        if state.get("salary_slip_required") and not state.get("salary_slip_uploaded"):
            anomalies.append({
                "type": "missing_salary",
                "message": "Salary slip required but not uploaded. Manual review needed.",
                "severity": "medium",
                "action": "manual_review"
            })
            if severity != "high":
                severity = "medium"
        
        # Rule 3: Suspicious salary jump (2L → 15L = 7.5x)
        current_salary = state.get("monthly_salary")
        current_loan_details = state.get("current_loan_details")
        previous_salary = None
        
        if current_loan_details and isinstance(current_loan_details, dict):
            previous_salary = current_loan_details.get("monthly_salary")
        
        if current_salary and previous_salary and previous_salary > 0:
            jump_ratio = current_salary / previous_salary
            # Flag if more than 100% increase (2x) or 50% decrease
            if jump_ratio > 2.0 or jump_ratio < 0.5:
                anomalies.append({
                    "type": "salary_jump",
                    "message": f"Suspicious salary change: ₹{previous_salary:,.0f} → ₹{current_salary:,.0f} ({jump_ratio:.1f}x)",
                    "severity": "high",
                    "action": "manual_review"
                })
                severity = "high"
        
        return {
            "anomalies": anomalies,
            "severity": severity,
            "has_issues": len(anomalies) > 0
        }
    
    def detect_document_mismatches(self, state: Dict) -> Dict:
        """
        Detect mismatches between KYC and uploaded documents:
        - KYC name ≠ Salary slip extracted name
        - Address mismatch
        - Phone number inconsistencies
        """
        mismatches = []
        
        kyc_name = state.get("customer_name", "").lower().strip()
        kyc_phone = state.get("phone", "")
        kyc_address = state.get("verified_address", "").lower().strip()
        
        # Note: In real implementation, we'd extract name from salary slip OCR
        # For now, this is a placeholder structure
        
        return {
            "mismatches": mismatches,
            "has_mismatches": len(mismatches) > 0
        }
    
    def detect_duplicate_applications(self, phone: str, state: Dict) -> Dict:
        """
        Detect if same phone has multiple rejected applications.
        Flags if same phone appears 2+ times in rejection database.
        """
        rejection_count = fraud_database["rejected_phones"].get(phone, 0)
        is_repeat_applicant = rejection_count >= 2
        
        return {
            "is_repeat_applicant": is_repeat_applicant,
            "rejection_count": rejection_count,
            "message": f"Phone {phone} has {rejection_count} previous rejections. Repeat applicant detected." if is_repeat_applicant else None,
            "severity": "high" if is_repeat_applicant else "low"
        }
    
    def detect_suspicious_patterns(self, state: Dict) -> Dict:
        """
        Detect suspicious patterns:
        - Known fake addresses
        - Inconsistent credit history
        - Low credit + high EMI mismatch
        """
        patterns = []
        
        address = state.get("verified_address", "").lower()
        credit_score = state.get("credit_score")
        
        # Check against known suspicious addresses
        if address and address in fraud_database["suspicious_addresses"]:
            patterns.append({
                "type": "suspicious_address",
                "message": "Address flagged as suspicious in fraud database.",
                "severity": "high"
            })
        
        # Check credit score vs EMI ratio inconsistency
        if credit_score and state.get("calculated_emi") and state.get("monthly_salary"):
            monthly_salary = state["monthly_salary"]
            emi = state["calculated_emi"]
            emi_ratio = (emi / monthly_salary) * 100 if monthly_salary > 0 else 0
            
            # Low credit + high EMI = risky profile
            if credit_score < 600 and emi_ratio > 40:
                patterns.append({
                    "type": "risky_profile",
                    "message": f"Low credit score ({credit_score}) with high EMI ratio ({emi_ratio:.1f}%). Risky profile.",
                    "severity": "medium"
                })
        
        return {
            "patterns": patterns,
            "has_patterns": len(patterns) > 0
        }
    
    def calculate_fraud_risk_score(self, state: Dict) -> float:
        """
        Calculate overall fraud risk score (0-100).
        0-30: Low risk ✓
        30-60: Medium risk ⚠️ (manual review)
        60-100: High risk ✗ (reject)
        """
        risk_score = 0.0
        
        # Salary anomalies (40 points max)
        salary_check = self.detect_salary_anomalies(state)
        risk_score += len(salary_check["anomalies"]) * 20
        
        # Document mismatches (20 points max)
        doc_check = self.detect_document_mismatches(state)
        risk_score += len(doc_check["mismatches"]) * 10
        
        # Duplicate applications (20 points max)
        dup_check = self.detect_duplicate_applications(state.get("phone", ""), state)
        if dup_check["is_repeat_applicant"]:
            risk_score += 20
        
        # Suspicious patterns (20 points max)
        pattern_check = self.detect_suspicious_patterns(state)
        risk_score += len(pattern_check["patterns"]) * 10
        
        return min(risk_score, 100.0)
    
    def generate_fraud_alert(self, state: Dict, fraud_flags: list, fraud_risk: float) -> str:
        """
        Generate professional fraud alert using Groq LLM
        """
        fraud_summary = "\n".join([f"- {flag['message']}" for flag in fraud_flags])
        
        prompt = f"""You are a BFSI fraud detection analyst. Review the following fraud flags detected in a loan application and provide a professional fraud alert summary.

Customer: {state.get('customer_name', 'Unknown')}
Phone: {state.get('phone', 'Unknown')}
Fraud Risk Score: {fraud_risk:.0f}/100
Requested Loan: ₹{state.get('requested_loan_amount', 'N/A'):,.0f}
Credit Score: {state.get('credit_score', 'N/A')}

Detected Fraud Flags:
{fraud_summary}

Provide a brief professional summary (3-4 sentences) with:
1. Risk assessment
2. Recommended action (REJECT / MANUAL_REVIEW / APPROVE_WITH_CONDITIONS)
3. Key factors for investigation"""
        
        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a professional BFSI fraud detection analyst."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Fraud alert: Risk score {fraud_risk:.0f}/100. Manual review recommended."
    
    def process_fraud_check(self, state: Dict) -> Dict:
        """
        Main fraud detection process.
        Returns updated state with fraud flags and routing decision.
        """
        # Run all fraud detection checks
        salary_check = self.detect_salary_anomalies(state)
        doc_check = self.detect_document_mismatches(state)
        dup_check = self.detect_duplicate_applications(state.get("phone", ""), state)
        pattern_check = self.detect_suspicious_patterns(state)
        
        # Calculate fraud risk score
        fraud_risk = self.calculate_fraud_risk_score(state)
        
        # Aggregate all fraud findings
        all_fraud_flags = (
            salary_check["anomalies"] +
            doc_check["mismatches"] +
            ([] if not dup_check["is_repeat_applicant"] else [{
                "type": "duplicate_application",
                "message": dup_check["message"],
                "severity": dup_check["severity"],
                "action": "manual_review"
            }]) +
            pattern_check["patterns"]
        )
        
        # Update state with fraud detection results
        state["fraud_risk_score"] = fraud_risk
        state["fraud_flags"] = all_fraud_flags
        state["fraud_detected"] = len(all_fraud_flags) > 0
        
        # Generate fraud alert message using LLM if issues found
        if all_fraud_flags:
            alert_message = self.generate_fraud_alert(state, all_fraud_flags, fraud_risk)
            state["messages"].append(AIMessage(content=alert_message))
        else:
            # No fraud detected - proceed normally
            state["messages"].append(AIMessage(
                content="✓ Fraud check passed. No suspicious patterns detected."
            ))
        
        # Determine routing based on fraud risk and current status
        if fraud_risk >= 70:
            # High risk - reject application
            state["loan_status"] = "rejected"
            state["rejection_reason"] = f"Application rejected due to fraud detection. Risk score: {fraud_risk:.0f}/100"
            state["current_agent"] = "master"
        
        elif fraud_risk >= 40:
            # Medium risk - flag for manual review
            state["loan_status"] = "manual_review_fraud"
            state["current_agent"] = "master"
        
        else:
            # Low risk - continue processing
            if state.get("loan_status") == "approved":
                # If already approved, go to sanction
                state["current_agent"] = "sanction"
            else:
                # Otherwise, return to master for next steps
                state["current_agent"] = "master"
        
        return state


# Main fraud agent node for workflow
def fraud_agent_node(state: Dict) -> Dict:
    """
    Fraud detection node for LangGraph workflow.
    Integrates FraudAgent into the workflow pipeline.
    """
    agent = FraudAgent()
    return agent.process_fraud_check(state)


# Helper functions for fraud database management
def record_rejection(phone: str):
    """
    Record a rejected application for duplicate detection.
    Call this when an application is rejected.
    """
    if phone in fraud_database["rejected_phones"]:
        fraud_database["rejected_phones"][phone] += 1
    else:
        fraud_database["rejected_phones"][phone] = 1


def add_suspicious_address(address: str):
    """
    Add an address to the suspicious addresses list.
    """
    fraud_database["suspicious_addresses"].add(address.lower())


def get_fraud_statistics() -> Dict:
    """
    Get fraud detection statistics for monitoring/dashboard.
    """
    from datetime import datetime
    return {
        "total_flagged_applications": len(fraud_database["flagged_applications"]),
        "repeat_applicants": len(fraud_database["rejected_phones"]),
        "known_suspicious_addresses": len(fraud_database["suspicious_addresses"]),
        "rejection_counts": fraud_database["rejected_phones"],
        "timestamp": datetime.now().isoformat()
    }
