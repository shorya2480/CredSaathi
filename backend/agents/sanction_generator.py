from langchain_core.messages import AIMessage
from graph.state import AgentState
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from pathlib import Path
from datetime import datetime
import uuid


def generate_sanction_letter_pdf(state: AgentState) -> str:
    """
    Generate a professional loan sanction letter PDF.
    
    Returns:
        Path to generated PDF file
    """
    # Create output directory
    output_dir = Path(__file__).parent.parent / "data" / "sanction_letters"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    filename = f"sanction_letter_{state['customer_id']}_{uuid.uuid4().hex[:8]}.pdf"
    filepath = output_dir / filename
    
    doc = SimpleDocTemplate(str(filepath), pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1a237e'),
        spaceAfter=30,
        alignment=1  # Center
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#1a237e'),
        spaceAfter=12
    )
    
    story.append(Paragraph("LOAN SANCTION LETTER", title_style))
    story.append(Spacer(1, 0.2 * inch))
    
    date_str = datetime.now().strftime("%B %d, %Y")
    ref_number = f"SL/{state['customer_id']}/{datetime.now().strftime('%Y%m%d')}"
    
    story.append(Paragraph(f"<b>Date:</b> {date_str}", styles['Normal']))
    story.append(Paragraph(f"<b>Reference No:</b> {ref_number}", styles['Normal']))
    story.append(Spacer(1, 0.3 * inch))
    
    story.append(Paragraph("BORROWER DETAILS", heading_style))
    customer_data = [
        ['Name:', state['customer_name']],
        ['Address:', state['verified_address']],
        ['Phone:', state['verified_phone']],
        ['Customer ID:', str(state['customer_id'])]
    ]
    
    customer_table = Table(customer_data, colWidths=[2*inch, 4*inch])
    customer_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(customer_table)
    story.append(Spacer(1, 0.3 * inch))
    
    story.append(Paragraph("LOAN DETAILS", heading_style))
    
    total_repayment = state['calculated_emi'] * state['requested_tenure']
    total_interest = total_repayment - state['requested_loan_amount']
    
    loan_data = [
        ['Loan Amount:', f"₹{state['requested_loan_amount']:,.2f}"],
        ['Interest Rate:', f"{state['negotiated_interest_rate']}% per annum"],
        ['Loan Tenure:', f"{state['requested_tenure']} months"],
        ['Monthly EMI:', f"₹{state['calculated_emi']:,.2f}"],
        ['Total Interest:', f"₹{total_interest:,.2f}"],
        ['Total Repayment:', f"₹{total_repayment:,.2f}"],
    ]
    
    loan_table = Table(loan_data, colWidths=[2*inch, 4*inch])
    loan_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f5f5f5')),
    ]))
    story.append(loan_table)
    story.append(Spacer(1, 0.3 * inch))
    
    # Terms and conditions
    story.append(Paragraph("TERMS & CONDITIONS", heading_style))
    
    terms = [
        "This sanction is valid for 30 days from the date of issue.",
        "The loan is subject to verification of all submitted documents.",
        "EMI payments must be made on or before the due date each month.",
        "Prepayment charges: 2% of outstanding principal (if prepaid before 12 months).",
        "Late payment charges: 2% per month on overdue amount.",
        "The bank reserves the right to recall the loan in case of default.",
    ]
    
    for i, term in enumerate(terms, 1):
        story.append(Paragraph(f"{i}. {term}", styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))
    
    story.append(Spacer(1, 0.3 * inch))
    
    congrats_style = ParagraphStyle(
        'Congrats',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#2e7d32'),
        spaceAfter=12
    )
    story.append(Paragraph(
        "Congratulations on your loan approval! We look forward to serving you.",
        congrats_style
    ))
    
    story.append(Spacer(1, 0.3 * inch))
    
    story.append(Paragraph("<b>Authorized Signatory</b>", styles['Normal']))
    story.append(Paragraph("Loan Department", styles['Normal']))
    story.append(Paragraph("CredSaathi Bank", styles['Normal']))
    
    doc.build(story)
    
    return str(filepath)


def sanction_generator_node(state: AgentState) -> AgentState:
    """
    Sanction Letter Generator Agent.
    
    Generates PDF sanction letter for approved loans.
    """
    
    pdf_path = generate_sanction_letter_pdf(state)
    
    state['sanction_letter_generated'] = True
    state['sanction_letter_path'] = pdf_path
    
    # Inform user
    message = f"""Your loan sanction letter has been generated successfully!

 Document: Sanction Letter
 Reference: SL/{state['customer_id']}/{datetime.now().strftime('%Y%m%d')}

You can download your sanction letter from the link below."""
    
    state["messages"].append(AIMessage(content=message))
    
    state['loan_status'] = 'approved'
    state['workflow_complete'] = True
    
    return state


__all__ = ["sanction_generator_node"]