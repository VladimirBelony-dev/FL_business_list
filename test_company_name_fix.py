import pandas as pd
import re
from pathlib import Path
from datetime import datetime

def extract_officer_from_line_test(line):
    """Test version with corrected company name extraction"""
    
    # Check if line is long enough
    if len(line) < 900:
        return None
    
    search_section = line[600:900]
    
    # Pattern: ROLE + STATUS_CHAR + LASTNAME + FIRSTNAME + MIDDLE_INITIAL
    officer_pattern = r'(AMBR|MGRM|MGR|CEO|CFO|COO|PRES|VP|SEC|DIR|AP|P)\s*([PCMD])([A-Z][A-Z\-\' ]{8,20})\s+([A-Z][A-Z\-\' ]{8,20})\s+([A-Z]?)\s+'
    
    match = re.search(officer_pattern, search_section)
    
    if not match:
        return None
    
    role = match.group(1)
    status = match.group(2)
    last_name = match.group(3).strip()
    first_name = match.group(4).strip()
    middle = match.group(5).strip()
    
    # Extract company info - CORRECTED POSITION
    company_name = line[12:165].strip() if len(line) > 165 else line[12:].strip()
    doc_num = line[0:12].strip() if len(line) > 12 else line[0:].strip()
    
    return {
        'doc_number': doc_num,
        'company_name': company_name,
        'officer_role': role,
        'officer_last': last_name,
        'officer_first': first_name,
        'officer_middle': middle,
        'officer_full_name': f"{first_name} {middle} {last_name}".strip(),
        'status': status
    }

def test_company_name_extraction():
    """Test the corrected company name extraction"""
    
    print("Testing corrected company name extraction...")
    print("=" * 60)
    
    # Test with a few lines from cordata0.txt
    test_results = []
    
    with open('cordata0.txt', 'r', encoding='latin-1', errors='ignore') as f:
        for i, line in enumerate(f):
            if i >= 10:  # Test first 10 lines
                break
                
            result = extract_officer_from_line_test(line)
            if result:
                test_results.append(result)
    
    # Display results
    for i, result in enumerate(test_results[:5]):  # Show first 5 results
        print(f"\nResult {i+1}:")
        print(f"  Doc Number: {result['doc_number']}")
        print(f"  Company Name: {result['company_name']}")
        print(f"  Officer: {result['officer_full_name']}")
        print(f"  Role: {result['officer_role']}")
        print("-" * 40)

if __name__ == "__main__":
    test_company_name_extraction()
