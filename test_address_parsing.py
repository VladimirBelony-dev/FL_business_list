import pandas as pd
import re
from pathlib import Path
from datetime import datetime

def extract_officer_from_line_test(line):
    """Test version of extract_officer_from_line with improved address parsing"""
    
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
    
    # Extract company info
    company_name = line[15:165].strip() if len(line) > 165 else line[15:].strip()
    doc_num = line[0:12].strip() if len(line) > 12 else line[0:].strip()
    
    # Extract address information with improved parsing
    address1 = ""
    address2 = ""
    city = ""
    state = ""
    zip_code = ""
    
    try:
        # Primary address (street address)
        if len(line) > 315:
            address1 = line[165:315].strip()
        
        # Secondary address line - THIS CONTAINS CITY, STATE, ZIP
        if len(line) > 465:
            address2_raw = line[315:465].strip()
            
            # Clean up the raw data - remove extra spaces and normalize
            address2_clean = re.sub(r'\s+', ' ', address2_raw).strip()
            
            # Look for city, state, zip pattern in this section
            # Pattern: CITY FL33304 (no space between state and zip)
            # Example: "FT. LAUDERDALE FL33304"
            csz_pattern = r'([A-Z\s\-\.]+?)\s+([A-Z]{2})(\d{5})'
            csz_match = re.search(csz_pattern, address2_clean)
            
            if csz_match:
                city = csz_match.group(1).strip()
                state = csz_match.group(2).strip()
                zip_code = csz_match.group(3).strip()
                # Set address2 to just the street part (before city)
                address2 = address2_clean[:csz_match.start()].strip()
            else:
                # Try pattern with comma: CITY, FL33304
                csz_pattern_comma = r'([A-Z\s\-\.]+?),\s*([A-Z]{2})(\d{5})'
                csz_match_comma = re.search(csz_pattern_comma, address2_clean)
                if csz_match_comma:
                    city = csz_match_comma.group(1).strip()
                    state = csz_match_comma.group(2).strip()
                    zip_code = csz_match_comma.group(3).strip()
                    address2 = address2_clean[:csz_match_comma.start()].strip()
                else:
                    # Try pattern with space: CITY FL ZIPCODE
                    csz_pattern_space = r'([A-Z\s\-\.]+?)\s+([A-Z]{2})\s+(\d{5})'
                    csz_match_space = re.search(csz_pattern_space, address2_clean)
                    if csz_match_space:
                        city = csz_match_space.group(1).strip()
                        state = csz_match_space.group(2).strip()
                        zip_code = csz_match_space.group(3).strip()
                        address2 = address2_clean[:csz_match_space.start()].strip()
                    else:
                        # Try to extract just city and state without zip
                        city_state_pattern = r'([A-Z\s\-\.]+?)\s+([A-Z]{2})'
                        cs_match = re.search(city_state_pattern, address2_clean)
                        if cs_match:
                            city = cs_match.group(1).strip()
                            state = cs_match.group(2).strip()
                            address2 = address2_clean[:cs_match.start()].strip()
                        else:
                            # Fallback: use the cleaned string as address2
                            address2 = address2_clean
    
    except Exception as e:
        pass
    
    # Combine address fields
    full_address = ' '.join([addr for addr in [address1, address2] if addr])
    city_state_zip = ', '.join([item for item in [city, state, zip_code] if item])
    
    return {
        'doc_number': doc_num,
        'company_name': company_name,
        'officer_role': role,
        'officer_last': last_name,
        'officer_first': first_name,
        'officer_middle': middle,
        'officer_full_name': f"{first_name} {middle} {last_name}".strip(),
        'status': status,
        'address': full_address,
        'city_state_zip': city_state_zip,
        'city': city,
        'state': state,
        'zip_code': zip_code,
        'raw_address2': address2_raw if len(line) > 465 else ""
    }

def test_address_parsing():
    """Test the improved address parsing on a few sample lines"""
    
    print("Testing improved address parsing...")
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
        print(f"  Company: {result['company_name']}")
        print(f"  Doc Number: {result['doc_number']}")
        print(f"  Officer: {result['officer_full_name']}")
        print(f"  Address: {result['address']}")
        print(f"  City: {result['city']}")
        print(f"  State: {result['state']}")
        print(f"  Zip: {result['zip_code']}")
        print(f"  City, State, Zip: {result['city_state_zip']}")
        print(f"  Raw address2: {result['raw_address2'][:50]}...")
        print("-" * 40)

if __name__ == "__main__":
    test_address_parsing()
