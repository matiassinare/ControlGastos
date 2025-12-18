import re
from datetime import datetime
from typing import Optional

def parse_amount(amount_str: str) -> float:
    """
    Parse a currency string like "$ 1.234,56" or "USD 12.34" to a float.
    Handles both ARS (comma decimal) and USD (dot decimal) formats if needed,
    but primarily focuses on Argentine format: 1.234,56
    """
    if not amount_str:
        return 0.0
    
    # Remove currency symbols and whitespace
    cleaned = amount_str.replace('$', '').replace('USD', '').replace('ARS', '').strip()
    
    # Handle negative numbers (parentheses or minus sign)
    is_negative = '-' in cleaned or ('(' in cleaned and ')' in cleaned)
    cleaned = cleaned.replace('-', '').replace('(', '').replace(')', '')
    
    # Heuristic for format:
    # If ',' is the last separator and index > index of '.', it's likely 1.234,56
    # If there are no dots but a comma, it's 1234,56
    
    if ',' in cleaned and '.' in cleaned:
        if cleaned.rfind(',') > cleaned.rfind('.'):
             # Format 1.234,56 -> remove dots, replace comma with dot
            cleaned = cleaned.replace('.', '').replace(',', '.')
        else:
            # Format 1,234.56 -> remove commas
            cleaned = cleaned.replace(',', '')
    elif ',' in cleaned:
        # Format 1234,56 -> replace comma with dot
        cleaned = cleaned.replace(',', '.')
    
    # If it was just 1.234 (no decimal) it might be ambiguous, 
    # but usually currency has decimals. 
    # If strictly integer like 1.234, it could be 1234.
    
    try:
        val = float(cleaned)
        return -val if is_negative else val
    except ValueError:
        return 0.0

def parse_date(date_str: str, format: str = "%d/%m/%Y") -> Optional[str]:
    """
    Parse a date string and return it in ISO format YYYY-MM-DD.
    Returns None if parsing fails.
    """
    try:
        dt = datetime.strptime(date_str.strip(), format)
        return dt.date().isoformat()
    except ValueError:
        return None
