"""
Salary Slip Scanner Module
Handles extraction of salary information from various salary slip formats.
Supports PDF and image-based salary slips with OCR fallback.
"""

import re
from pathlib import Path
from typing import Optional, Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_salary_from_pdf(pdf_path: Path) -> Optional[Dict[str, any]]:
    """
    Extract salary information from PDF salary slip.
    
    Args:
        pdf_path: Path to PDF file
    
    Returns:
        Dictionary with extracted salary data or None if extraction fails
    """
    try:
        import pdfplumber
        
        salary_data = {
            "source": "pdf",
            "raw_text": "",
            "salary": None,
            "confidence": 0.0
        }
        
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                salary_data["raw_text"] += (page.extract_text() or "") + "\n"
        
        return salary_data
        
    except Exception as e:
        logger.error(f"Error reading PDF {pdf_path}: {str(e)}")
        return None


def extract_salary_from_image(image_path: Path) -> Optional[Dict[str, any]]:
    """
    Extract salary information from image-based salary slip using OCR.
    
    Args:
        image_path: Path to image file (JPG, PNG)
    
    Returns:
        Dictionary with extracted salary data or None if extraction fails
    """
    try:
        from PIL import Image
        import pytesseract
        
        salary_data = {
            "source": "image",
            "raw_text": "",
            "salary": None,
            "confidence": 0.0
        }
        
        image = Image.open(image_path)
        salary_data["raw_text"] = pytesseract.image_to_string(image)
        
        return salary_data
        
    except Exception as e:
        logger.error(f"Error reading image {image_path}: {str(e)}")
        return None


def parse_salary_from_text(text: str, keywords: List[str] = None) -> Optional[float]:
    """
    Parse salary amount from extracted text using keyword matching and regex patterns.
    
    Supports multiple salary slip formats:
    - Standard format: "Monthly Salary: ₹50,000"
    - CTC format: "CTC: Rs. 600000"
    - Take-home format: "Net Pay: 45000"
    
    Args:
        text: Extracted text from salary slip
        keywords: Optional list of keywords to search for (default: common salary keywords)
    
    Returns:
        Salary amount as float or None if not found
    """
    if not text:
        return None
    
    if keywords is None:
        keywords = [
            "salary", "net pay", "take home", "take-home", 
            "ctc", "gross", "net salary", "monthly salary",
            "basic salary", "fixed salary"
        ]
    
    # Normalize text
    text_lower = text.lower()
    cleaned_text = text.replace(",", "").replace("₹", "").replace("Rs", "").replace("Rs.", "")
    
    # Search for salary after keywords
    for keyword in keywords:
        pattern = rf"{keyword}\s*:?\s*[Rs.₹\s]*(\d{{5,7}})"
        matches = re.findall(pattern, text_lower)
        if matches:
            for match in matches:
                salary = int(match)
                if 10000 <= salary <= 10000000:  # Valid range
                    logger.info(f"Found salary {salary} with keyword '{keyword}'")
                    return float(salary)
    
    # Fallback: extract all large numbers and filter by range
    all_numbers = re.findall(r"\b\d{5,7}\b", cleaned_text)
    valid_salaries = [int(n) for n in all_numbers if 10000 <= int(n) <= 10000000]
    
    if valid_salaries:
        salary = float(max(valid_salaries))
        logger.info(f"Found salary {salary} via fallback number extraction")
        return salary
    
    logger.warning("Could not extract salary from text")
    return None


def extract_salary(file_path: Path) -> Optional[float]:
    """
    Main extraction function - supports PDF and image files.
    
    Workflow:
    1. Determine file type
    2. Extract text (native parsing for PDF, OCR for images)
    3. Parse salary from text
    4. Validate result
    
    Args:
        file_path: Path to salary slip file
    
    Returns:
        Extracted salary amount or None if extraction fails
    """
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return None
    
    suffix = file_path.suffix.lower()
    salary_data = None
    
    # Step 1: Extract text based on file type
    if suffix == ".pdf":
        salary_data = extract_salary_from_pdf(file_path)
    elif suffix in [".jpg", ".jpeg", ".png"]:
        salary_data = extract_salary_from_image(file_path)
    else:
        logger.error(f"Unsupported file format: {suffix}")
        return None
    
    if not salary_data:
        return None
    
    # Step 2: Parse salary from extracted text
    salary = parse_salary_from_text(salary_data["raw_text"])
    
    if salary:
        logger.info(f"Successfully extracted salary ₹{salary:,.0f} from {file_path.name}")
        return salary
    else:
        logger.warning(f"Could not extract valid salary from {file_path.name}")
        return None


def validate_salary_slip(file_path: Path) -> Dict[str, any]:
    """
    Validate a salary slip file and return validation results.
    
    Returns:
        Dictionary with validation status and extracted data
    """
    result = {
        "file": file_path.name,
        "valid": False,
        "salary": None,
        "errors": []
    }
    
    # Check file exists
    if not file_path.exists():
        result["errors"].append(f"File not found: {file_path}")
        return result
    
    # Check file type
    if file_path.suffix.lower() not in [".pdf", ".jpg", ".jpeg", ".png"]:
        result["errors"].append(f"Unsupported file format: {file_path.suffix}")
        return result
    
    # Try to extract salary
    try:
        salary = extract_salary(file_path)
        if salary:
            result["salary"] = salary
            result["valid"] = True
        else:
            result["errors"].append("Could not extract valid salary from file")
    except Exception as e:
        result["errors"].append(f"Error processing file: {str(e)}")
    
    return result
