import pandas as pd
import re
from pathlib import Path

def extract_officer_from_line(line):
    """Extract officer data from a single line"""
    
    # Officer data is around position 640-750
    # The pattern is: ROLE + STATUS_CHAR + LASTNAME + FIRSTNAME + MIDDLE + ADDRESS
    # Example: "MGR PPAUL                JAMES         C       "
    
    search_section = line[600:900]
    
    # Look for: ROLE (3-5 chars) + STATUS (P/C/M/D) + LASTNAME + FIRSTNAME + MIDDLE_INITIAL
    # The status char appears IMMEDIATELY after the role, then the name
    officer_pattern = r'(AMBR|MGRM|MGR|CEO|CFO|COO|PRES|VP|SEC|DIR|AP|P)\s*([PCMD])([A-Z][A-Z\-\' ]{8,20})\s+([A-Z][A-Z\-\' ]{8,20})\s+([A-Z]?)\s+'
    
    match = re.search(officer_pattern, search_section)
    
    if not match:
        return None
    
    role = match.group(1)
    status = match.group(2)
    last_name = match.group(3).strip()
    first_name = match.group(4).strip()
    middle = match.group(5).strip()
    
    # Company name is at the beginning
    company_name = line[15:165].strip()
    doc_num = line[0:12].strip()
    
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

def test_extraction(file_path, num_lines=100):
    """Test extraction on first N lines"""
    
    print(f"Testing extraction on {file_path}")
    print("="*80)
    
    officers = []
    total_lines = 0
    
    with open(file_path, 'r', encoding='latin-1', errors='ignore') as f:
        for line_num, line in enumerate(f, 1):
            total_lines += 1
            
            if line_num > num_lines:
                break
            
            officer_data = extract_officer_from_line(line)
            
            if officer_data:
                officers.append(officer_data)
                print(f"\nLine {line_num}: {officer_data['company_name'][:50]}")
                print(f"  Role: {officer_data['officer_role']}")
                print(f"  Name: {officer_data['officer_full_name']}")
                print(f"  Status: {officer_data['status']}")
    
    print("\n" + "="*80)
    print(f"Results: Found {len(officers)} officers in {total_lines} lines")
    print(f"Extraction rate: {len(officers)/total_lines*100:.1f}%")
    
    if officers:
        df = pd.DataFrame(officers)
        print("\nRole distribution:")
        print(df['officer_role'].value_counts())
        
        # Show first few examples
        print("\nFirst 5 officers:")
        print(df[['company_name', 'officer_role', 'officer_full_name']].head())
    
    return officers

# TEST WITH YOUR FILE
test_file = 'cordata0.txt'
officers = test_extraction(test_file, num_lines=100)