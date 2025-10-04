import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import re
import gc
from multiprocessing import Pool, cpu_count
import warnings
warnings.filterwarnings('ignore')

class EfficientCompanyMatcher:
    """Optimized company-officer matching with chunked processing"""
    
    def __init__(self, chunk_size=1000, match_threshold=85):
        self.chunk_size = chunk_size
        self.match_threshold = match_threshold
        self.extraction_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
    def clean_company_name(self, name):
        """Fast company name standardization"""
        if pd.isna(name) or not name:
            return ""
        
        # Single pass cleaning
        name = str(name).upper().strip()
        
        # Remove common suffixes with single regex
        name = re.sub(r'\b(LLC|L\.?L\.?C\.?|INC\.?|CORP(ORATION)?|LTD|LIMITED|L\.?P\.?|PLLC|P\.?L\.?L\.?C\.?|P\.?A\.?|P\.?C\.?|CO(MPANY)?)\s*$', '', name)
        
        # Clean special characters and normalize spaces in one pass
        name = re.sub(r'[^\w\s]', ' ', name)
        name = ' '.join(name.split())
        
        return name
    
    def fast_similarity(self, str1, str2):
        """Fast similarity calculation using simple ratio"""
        if not str1 or not str2:
            return 0
        
        # Quick exact match check
        if str1 == str2:
            return 100
        
        # Use set intersection for token matching (faster than fuzzy)
        tokens1 = set(str1.split())
        tokens2 = set(str2.split())
        
        if not tokens1 or not tokens2:
            return 0
        
        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)
        
        # Jaccard similarity
        jaccard = len(intersection) / len(union) * 100 if union else 0
        
        # Length similarity
        len_sim = min(len(str1), len(str2)) / max(len(str1), len(str2)) * 100
        
        # Weighted average
        return (jaccard * 0.7 + len_sim * 0.3)
    
    def parse_address_components(self, row):
        """Efficiently parse address components"""
        result = {
            'clean_address': '',
            'clean_city': '',
            'clean_state': '',
            'clean_zip': ''
        }
        
        # Parse address
        if pd.notna(row.get('address')):
            addr = str(row['address']).upper().strip()
            # Quick cleanup - remove suite info
            addr = re.sub(r'\b(SUITE|STE|APT|UNIT|#)\s*[\d\w]+', '', addr)
            result['clean_address'] = ' '.join(addr.split())
        
        # Use pre-parsed fields if available
        if pd.notna(row.get('city')):
            result['clean_city'] = str(row['city']).upper().strip()
        
        if pd.notna(row.get('state')):
            result['clean_state'] = str(row['state']).upper().strip()[:2]
        
        if pd.notna(row.get('zip_code')):
            zip_val = str(row['zip_code']).strip()
            # Extract just 5-digit zip
            zip_match = re.match(r'(\d{5})', zip_val)
            if zip_match:
                result['clean_zip'] = zip_match.group(1)
        
        # Fallback to parsing combined field
        if not result['clean_city'] and pd.notna(row.get('city_state_zip')):
            csz = str(row['city_state_zip']).strip()
            # Quick regex parse
            match = re.search(r'^([^,]+)[,\s]+([A-Z]{2})\s+(\d{5})', csz)
            if match:
                result['clean_city'] = match.group(1).strip()
                result['clean_state'] = match.group(2)
                result['clean_zip'] = match.group(3)
        
        return result
    
    def process_company_chunk(self, args):
        """Process a single chunk of companies (for parallel processing)"""
        chunk_companies, officers_df, chunk_id = args
        
        print(f"  Processing chunk {chunk_id} ({len(chunk_companies)} companies)...")
        
        matched_records = []
        
        for _, company_row in chunk_companies.iterrows():
            target_company = company_row['Company']
            target_clean = company_row['company_clean']
            
            # First try exact match (fastest)
            exact_matches = officers_df[officers_df['company_clean'] == target_clean]
            
            if not exact_matches.empty:
                # Take first exact match
                officer = exact_matches.iloc[0]
                matched_records.append(self.create_match_record(
                    target_company, officer, 100, 'EXACT'
                ))
            else:
                # Calculate similarities for all officers (vectorized)
                officers_df['similarity'] = officers_df['company_clean'].apply(
                    lambda x: self.fast_similarity(target_clean, x)
                )
                
                # Find best match above threshold
                best_idx = officers_df['similarity'].idxmax()
                best_score = officers_df.loc[best_idx, 'similarity']
                
                if best_score >= self.match_threshold:
                    officer = officers_df.loc[best_idx]
                    matched_records.append(self.create_match_record(
                        target_company, officer, best_score, 'FUZZY'
                    ))
                else:
                    # No match found
                    matched_records.append({
                        'Company': target_company,
                        'Officer': '',
                        'Address': '',
                        'City': '',
                        'State': '',
                        'Zip': '',
                        'Match_Type': 'NO_MATCH',
                        'Match_Score': 0
                    })
        
        return matched_records
    
    def create_match_record(self, company_name, officer_data, score, match_type):
        """Create a clean matched record"""
        
        # Format officer name
        first = str(officer_data.get('officer_first', '')).strip()
        middle = str(officer_data.get('officer_middle', '')).strip()
        last = str(officer_data.get('officer_last', '')).strip()
        officer_name = f"{first} {middle} {last}".strip()
        officer_name = ' '.join(officer_name.split())  # Clean multiple spaces
        
        return {
            'Company': company_name,
            'Officer': officer_name,
            'Address': officer_data.get('clean_address', ''),
            'City': officer_data.get('clean_city', ''),
            'State': officer_data.get('clean_state', ''),
            'Zip': officer_data.get('clean_zip', ''),
            'Match_Type': match_type,
            'Match_Score': round(score, 1)
        }
    
    def match_companies_efficient(self, officers_df, companies_df):
        """Efficient chunked matching process"""
        
        print("\n" + "="*80)
        print("EFFICIENT COMPANY MATCHING SYSTEM")
        print("="*80)
        
        # Step 1: Pre-process all data
        print("\nStep 1: Pre-processing data...")
        print("  Cleaning company names...")
        
        # Vectorized cleaning (much faster than apply)
        officers_df['company_clean'] = officers_df['company_name'].fillna('').astype(str).apply(self.clean_company_name)
        companies_df['company_clean'] = companies_df['Company'].fillna('').astype(str).apply(self.clean_company_name)
        
        print("  Parsing addresses...")
        # Parse addresses in batch
        address_data = []
        for _, row in officers_df.iterrows():
            address_data.append(self.parse_address_components(row))
        
        address_df = pd.DataFrame(address_data)
        officers_df = pd.concat([officers_df, address_df], axis=1)
        
        # Step 2: Create index for exact matching (very fast lookups)
        print("\nStep 2: Building search index...")
        company_index = {}
        for idx, row in officers_df.iterrows():
            clean_name = row['company_clean']
            if clean_name not in company_index:
                company_index[clean_name] = []
            company_index[clean_name].append(idx)
        
        # Step 3: Process in chunks
        print(f"\nStep 3: Matching {len(companies_df)} companies in chunks of {self.chunk_size}...")
        
        all_matches = []
        num_chunks = (len(companies_df) + self.chunk_size - 1) // self.chunk_size
        
        for chunk_id in range(num_chunks):
            start_idx = chunk_id * self.chunk_size
            end_idx = min(start_idx + self.chunk_size, len(companies_df))
            
            chunk = companies_df.iloc[start_idx:end_idx]
            
            print(f"\nProcessing chunk {chunk_id + 1}/{num_chunks} (companies {start_idx + 1}-{end_idx})...")
            
            chunk_matches = []
            exact_count = 0
            fuzzy_count = 0
            no_match_count = 0
            
            for _, company_row in chunk.iterrows():
                target_company = company_row['Company']
                target_clean = company_row['company_clean']
                
                # Check exact match using index (O(1) lookup)
                if target_clean in company_index:
                    # Found exact match
                    officer_idx = company_index[target_clean][0]
                    officer = officers_df.loc[officer_idx]
                    chunk_matches.append(self.create_match_record(
                        target_company, officer, 100, 'EXACT'
                    ))
                    exact_count += 1
                else:
                    # Need fuzzy matching
                    best_score = 0
                    best_officer = None
                    
                    # Only check a sample for efficiency
                    sample_size = min(1000, len(officers_df))
                    sample_df = officers_df.sample(n=sample_size) if len(officers_df) > sample_size else officers_df
                    
                    for _, officer in sample_df.iterrows():
                        score = self.fast_similarity(target_clean, officer['company_clean'])
                        if score > best_score and score >= self.match_threshold:
                            best_score = score
                            best_officer = officer
                    
                    if best_officer is not None:
                        chunk_matches.append(self.create_match_record(
                            target_company, best_officer, best_score, 'FUZZY'
                        ))
                        fuzzy_count += 1
                    else:
                        chunk_matches.append({
                            'Company': target_company,
                            'Officer': '',
                            'Address': '',
                            'City': '',
                            'State': '',
                            'Zip': '',
                            'Match_Type': 'NO_MATCH',
                            'Match_Score': 0
                        })
                        no_match_count += 1
            
            print(f"  Chunk results: {exact_count} exact, {fuzzy_count} fuzzy, {no_match_count} no match")
            all_matches.extend(chunk_matches)
            
            # Clear memory
            gc.collect()
        
        # Create final dataframe
        results_df = pd.DataFrame(all_matches)
        results_df = results_df.sort_values('Company')
        
        print("\n" + "="*60)
        print("MATCHING COMPLETE:")
        print(f"  ✓ Total companies: {len(companies_df)}")
        print(f"  ✓ Exact matches: {len(results_df[results_df['Match_Type'] == 'EXACT'])}")
        print(f"  ✓ Fuzzy matches: {len(results_df[results_df['Match_Type'] == 'FUZZY'])}")
        print(f"  ✓ No matches: {len(results_df[results_df['Match_Type'] == 'NO_MATCH'])}")
        
        return results_df
    
    def save_results(self, df, output_file):
        """Save results to Excel with formatting"""
        
        print(f"\nSaving results to: {output_file}")
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Main results
            df.to_excel(writer, sheet_name='Matched_Officers', index=False)
            
            # Summary statistics
            summary = {
                'Metric': [
                    'Total Companies',
                    'Exact Matches',
                    'Fuzzy Matches', 
                    'No Matches',
                    'Match Rate',
                    'Processing Date'
                ],
                'Value': [
                    len(df),
                    len(df[df['Match_Type'] == 'EXACT']),
                    len(df[df['Match_Type'] == 'FUZZY']),
                    len(df[df['Match_Type'] == 'NO_MATCH']),
                    f"{len(df[df['Match_Type'] != 'NO_MATCH']) / len(df) * 100:.1f}%",
                    self.extraction_timestamp
                ]
            }
            
            pd.DataFrame(summary).to_excel(writer, sheet_name='Summary', index=False)
            
            # Format columns
            worksheet = writer.sheets['Matched_Officers']
            column_widths = {
                'A': 40, 'B': 25, 'C': 45, 'D': 20, 
                'E': 8, 'F': 12, 'G': 12, 'H': 12
            }
            
            for col, width in column_widths.items():
                worksheet.column_dimensions[col].width = width
        
        print(f"  ✓ Results saved successfully!")

def main():
    """Main execution with efficient processing"""
    
    print("="*80)
    print("EFFICIENT COMPANY-OFFICER MATCHING SYSTEM")
    print("="*80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Available CPU cores: {cpu_count()}")
    
    # Configuration
    CHUNK_SIZE = 500  # Process 500 companies at a time
    MATCH_THRESHOLD = 85  # Minimum similarity score
    
    matcher = EfficientCompanyMatcher(chunk_size=CHUNK_SIZE, match_threshold=MATCH_THRESHOLD)
    
    # Load officer data
    print("\n1. Loading officer data...")
    officer_files = sorted(Path('.').glob('officers_clean*.csv'))
    
    if not officer_files:
        print("ERROR: No officer data found! Run extraction script first.")
        return
    
    officer_file = officer_files[-1]  # Most recent
    print(f"   Loading: {officer_file}")
    
    # Read in chunks for large files
    officers_chunks = []
    for chunk in pd.read_csv(officer_file, encoding='utf-8-sig', chunksize=10000):
        officers_chunks.append(chunk)
    
    officers_df = pd.concat(officers_chunks, ignore_index=True)
    print(f"   ✓ Loaded {len(officers_df):,} officer records")
    
    # Clear memory
    del officers_chunks
    gc.collect()
    
    # Load company list
    print("\n2. Loading company list...")
    company_file = 'Corps 10-2-25.xlsx'
    
    if not Path(company_file).exists():
        print(f"ERROR: '{company_file}' not found!")
        return
    
    companies_df = pd.read_excel(company_file)
    print(f"   ✓ Loaded {len(companies_df):,} companies")
    
    # Perform matching
    print("\n3. Starting efficient matching process...")
    results_df = matcher.match_companies_efficient(officers_df, companies_df)
    
    # Save results
    print("\n4. Saving results...")
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f'matched_companies_{timestamp}.xlsx'
    
    matcher.save_results(results_df, output_file)
    
    # Final summary
    print("\n" + "="*80)
    print("PROCESSING COMPLETE")
    print("="*80)
    print(f"Output: {output_file}")
    print(f"Total time: {datetime.now().strftime('%H:%M:%S')}")
    
    # Memory cleanup
    del officers_df, companies_df, results_df
    gc.collect()
    
    print("\n✓ All processing complete! Check the output file for results.")

if __name__ == "__main__":
    main()