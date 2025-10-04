import re

def parse_address_improved(line):
    """Improved address parsing for cordata files"""
    
    # Extract the key sections
    address1 = line[165:315].strip() if len(line) > 315 else ""
    address2 = line[315:465].strip() if len(line) > 465 else ""
    address3 = line[565:665].strip() if len(line) > 665 else ""
    
    print(f"Address1 (165-315): {repr(address1)}")
    print(f"Address2 (315-465): {repr(address2)}")
    print(f"Address3 (565-665): {repr(address3)}")
    
    # Look for city, state, zip patterns in all sections
    city = ""
    state = ""
    zip_code = ""
    
    # Pattern: CITY FL ZIPCODE (more flexible)
    csz_pattern = r'([A-Z][A-Z\s\-\.]+?)\s+([A-Z]{2})\s+(\d{5})'
    
    for section_name, section in [("Address1", address1), ("Address2", address2), ("Address3", address3)]:
        if not section:
            continue
            
        # Clean the section
        clean_section = re.sub(r'\s+', ' ', section).strip()
        
        # Look for the pattern
        matches = list(re.finditer(csz_pattern, clean_section))
        
        if matches:
            print(f"Found {len(matches)} matches in {section_name}")
            for i, match in enumerate(matches):
                print(f"  Match {i+1}: City='{match.group(1)}', State='{match.group(2)}', Zip='{match.group(3)}'")
            
            # Use the first good match
            if matches:
                city = matches[0].group(1).strip()
                state = matches[0].group(2).strip()
                zip_code = matches[0].group(3).strip()
                print(f"Selected: {city}, {state} {zip_code}")
                break
    
    return city, state, zip_code

# Test with a few lines
print("Testing improved address parsing...")
print("=" * 60)

with open('cordata0.txt', 'r', encoding='latin-1', errors='ignore') as f:
    for i, line in enumerate(f):
        if i >= 3:  # Test first 3 lines
            break
            
        print(f"\nLine {i+1}:")
        print(f"Company: {line[15:165].strip()}")
        print(f"Doc: {line[0:12].strip()}")
        
        city, state, zip_code = parse_address_improved(line)
        print(f"Result: {city}, {state} {zip_code}")
        print("-" * 40)
