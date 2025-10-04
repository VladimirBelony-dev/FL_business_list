import pandas as pd
import re
from pathlib import Path
from datetime import datetime

def extract_officer_from_line(line):
    """Extract officer and address data from a single line"""
    
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
    # Company name starts at position 12, not 15 (was missing first 3 letters)
    company_name = line[12:165].strip() if len(line) > 165 else line[12:].strip()
    doc_num = line[0:12].strip() if len(line) > 12 else line[0:].strip()
    
    # Extract address information with corrected parsing
    # Based on actual cordata file structure analysis:
    # Address1: Position 165-315 (first part of street address)
    # Address2: Position 315-465 (contains city, state, zip - this is the key section!)
    # Additional: Position 565+ (may contain additional address info)
    
    address1 = ""
    address2 = ""
    city = ""
    state = ""
    zip_code = ""
    
    try:
        # Primary address (first part of street address)
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
        # If parsing fails, continue with what we have
        pass
    
    # Combine address fields
    full_address = ' '.join([addr for addr in [address1, address2] if addr])
    city_state_zip = ', '.join([item for item in [city, state, zip_code] if item])
    
    # Get current timestamp
    extraction_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
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
        'extraction_timestamp': extraction_timestamp
    }

def process_file_in_chunks(file_path, chunk_size=50000):
    """Process a file in chunks to manage memory"""
    
    print(f"\nProcessing: {file_path.name}")
    print("-" * 60)
    
    all_officers = []
    total_lines = 0
    chunk_num = 0
    
    with open(file_path, 'r', encoding='latin-1', errors='ignore') as f:
        chunk = []
        
        for line_num, line in enumerate(f, 1):
            total_lines += 1
            
            officer_data = extract_officer_from_line(line)
            
            if officer_data:
                officer_data['source_file'] = file_path.name
                officer_data['line_number'] = line_num
                chunk.append(officer_data)
            
            # Process chunk when it reaches chunk_size
            if len(chunk) >= chunk_size:
                chunk_num += 1
                all_officers.extend(chunk)
                print(f"  Chunk {chunk_num}: Processed {total_lines:,} lines, found {len(all_officers):,} officers")
                chunk = []
        
        # Process remaining items
        if chunk:
            all_officers.extend(chunk)
    
    print(f"  Complete: {len(all_officers):,} officers from {total_lines:,} lines ({len(all_officers)/total_lines*100:.1f}%)")
    
    return all_officers

def analyze_file_structure(file_path, num_lines=10):
    """Analyze the structure of the data file to help identify field positions"""
    
    print(f"\nAnalyzing file structure: {file_path.name}")
    print("=" * 80)
    
    with open(file_path, 'r', encoding='latin-1', errors='ignore') as f:
        for i, line in enumerate(f):
            if i >= num_lines:
                break
            
            print(f"\nLine {i+1} Length: {len(line)}")
            print("-" * 40)
            
            # Show key sections
            sections = [
                ("Doc Number [0:12]", 0, 12),
                ("Company Name [15:165]", 15, 165),
                ("Address1 [165:315]", 165, 315),
                ("Address2 [315:465]", 315, 465),
                ("City/State/Zip [465:565]", 465, 565),
                ("Officer Section [600:900]", 600, 900)
            ]
            
            for name, start, end in sections:
                if len(line) > start:
                    content = line[start:min(end, len(line))].strip()
                    if content:
                        print(f"{name}: '{content[:50]}{'...' if len(content) > 50 else ''}'")

def main():
    """Main processing function"""
    
    print("="*80)
    print("FLORIDA CORPORATION OFFICER DATA EXTRACTION (ENHANCED)")
    print("="*80)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Optional: Analyze file structure first (uncomment to use)
    # sample_files = list(Path('.').glob('cordata*.txt'))[:1]
    # if sample_files:
    #     analyze_file_structure(sample_files[0], num_lines=5)
    #     input("\nPress Enter to continue with extraction...")
    
    all_officers = []
    
    # Process ALL cordata files (corporations) - cordata0.txt through cordata9.txt
    print("\n[1/2] Processing ALL CORPORATION files (cordata0.txt - cordata9.txt)")
    print("="*80)
    cordata_files = []
    for i in range(10):  # cordata0.txt through cordata9.txt
        file_path = Path(f'cordata{i}.txt')
        if file_path.exists():
            cordata_files.append(file_path)
    
    print(f"Found {len(cordata_files)} cordata files:")
    for f in cordata_files:
        print(f"  • {f.name}")
    
    for file_path in cordata_files:
        officers = process_file_in_chunks(file_path)
        all_officers.extend(officers)
    
    # Process ALL npcordata files (non-profits) - npcordata0.txt through npcordata9.txt
    print("\n[2/2] Processing ALL NON-PROFIT files (npcordata0.txt - npcordata9.txt)")
    print("="*80)
    npcordata_files = []
    for i in range(10):  # npcordata0.txt through npcordata9.txt
        file_path = Path(f'npcordata{i}.txt')
        if file_path.exists():
            npcordata_files.append(file_path)
    
    print(f"Found {len(npcordata_files)} npcordata files:")
    for f in npcordata_files:
        print(f"  • {f.name}")
    
    for file_path in npcordata_files:
        officers = process_file_in_chunks(file_path)
        all_officers.extend(officers)
    
    # Convert to DataFrame
    print("\n" + "="*80)
    print("CREATING NEW OFFICER SHEET")
    print("="*80)
    
    df = pd.DataFrame(all_officers)
    
    # Add batch processing timestamp
    batch_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Save to CSV with timestamp in filename
    csv_file = f'new_officer_sheet_{batch_timestamp}.csv'
    print(f"\nSaving CSV: {csv_file}")
    df.to_csv(csv_file, index=False, encoding='utf-8-sig')
    print(f"  [SAVED] {len(df):,} records")
    
    # Check if data is too large for Excel (max 1,048,576 rows)
    if len(df) > 1048576:
        print(f"\nData too large for Excel (8,142,243 records > 1,048,576 max)")
        print("Creating sample Excel file with first 1,000,000 records...")
        
        # Create sample Excel file with first 1M records
        excel_file = f'new_officer_sheet_sample_{batch_timestamp}.xlsx'
        sample_df = df.head(1000000)
        
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            sample_df.to_excel(writer, sheet_name='New Officer Sheet Sample', index=False)
            
            # Auto-adjust column widths
            worksheet = writer.sheets['New Officer Sheet Sample']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        print(f"  [SAVED] Sample Excel: {len(sample_df):,} records")
        print(f"  [NOTE] Full data available in CSV: {csv_file}")
    else:
        # Save to Excel with "New Officer Sheet" as the sheet name
        excel_file = f'new_officer_sheet_{batch_timestamp}.xlsx'
        print(f"\nSaving Excel: {excel_file}")
        
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='New Officer Sheet', index=False)
            
            # Auto-adjust column widths
            worksheet = writer.sheets['New Officer Sheet']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        print(f"  [SAVED] {len(df):,} records")
    
    # Summary statistics
    print("\n" + "="*80)
    print("EXTRACTION SUMMARY")
    print("="*80)
    print(f"Total officers extracted: {len(df):,}")
    print(f"Unique companies: {df['company_name'].nunique():,}")
    print(f"Unique document numbers: {df['doc_number'].nunique():,}")
    
    print(f"\nRole distribution:")
    print(df['officer_role'].value_counts().head(15))
    
    print(f"\nStatus distribution:")
    print(df['status'].value_counts())
    
    print(f"\nState distribution (top 10):")
    state_counts = df['state'].value_counts().head(10)
    if not state_counts.empty:
        print(state_counts)
    else:
        print("  No state data extracted")
    
    print(f"\nRecords with complete address data:")
    complete_addresses = df[(df['address'].notna() & df['address'] != '') & 
                           (df['city'].notna() & df['city'] != '')].shape[0]
    print(f"  {complete_addresses:,} ({complete_addresses/len(df)*100:.1f}%)")
    
    print(f"\nSource files:")
    print(df['source_file'].value_counts())
    
    print("\n" + "="*80)
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    print(f"\nNEW OFFICER SHEET FILES CREATED:")
    print(f"  • {csv_file}")
    print(f"  • {excel_file}")
    print("\nColumns in New Officer Sheet:")
    print(f"  • {', '.join(df.columns.tolist())}")
    print("\nKey Data Extracted:")
    print(f"  • Document Numbers: {df['doc_number'].nunique():,} unique")
    print(f"  • Company Names: {df['company_name'].nunique():,} unique")
    print(f"  • Officers: {len(df):,} total records")
    print(f"  • Complete Addresses: {len(df[(df['address'].notna() & df['address'] != '') & (df['city'].notna() & df['city'] != '')]):,}")
    print("\nReady for Document Number Matching!")

if __name__ == "__main__":
    main()