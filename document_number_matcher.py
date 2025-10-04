import pandas as pd
import numpy as np
from rapidfuzz import fuzz, process
import re
from datetime import datetime
import warnings
from collections import defaultdict
from multiprocessing import Pool, cpu_count
import gc
warnings.filterwarnings('ignore')

class FastDocumentMatcher:
    """Ultra-fast document number matching with intelligent optimization"""
    
    def __init__(self, match_threshold=80):
        self.match_threshold = match_threshold
        self.exact_match_index = {}
        self.prefix_index = defaultdict(list)
        self.token_index = defaultdict(list)
        
    def clean_company_name(self, name):
        """Fast company name standardization"""
        if pd.isna(name) or not name:
            return ""
        
        # Single pass cleaning
        name = str(name).upper().strip()
        # Keep business characters but normalize
        name = re.sub(r'[^\w\s\.&]', ' ', name)
        name = ' '.join(name.split())
        
        return name
    
    def build_indexes(self, officers_df):
        """Build multiple indexes for fast matching"""
        print("Building search indexes...")
        
        for idx, row in officers_df.iterrows():
            clean_name = row['clean_name']
            doc_number = row['doc_number']
            
            if not clean_name:
                continue
            
            # Exact match index
            self.exact_match_index[clean_name] = doc_number
            
            # Prefix index (first 3-5 characters)
            if len(clean_name) >= 3:
                prefix3 = clean_name[:3]
                self.prefix_index[prefix3].append((clean_name, doc_number))
                
                if len(clean_name) >= 5:
                    prefix5 = clean_name[:5]
                    self.prefix_index[prefix5].append((clean_name, doc_number))
            
            # Token index (first meaningful word)
            tokens = clean_name.split()
            if tokens:
                first_token = tokens[0]
                if len(first_token) >= 3:  # Skip very short tokens
                    self.token_index[first_token].append((clean_name, doc_number))
        
        print(f"  [INDEXED] {len(self.exact_match_index):,} exact matches")
        print(f"  [INDEXED] {len(self.prefix_index):,} prefixes")
        print(f"  [INDEXED] {len(self.token_index):,} tokens")
    
    def find_candidates(self, company_name):
        """Find candidate matches using indexes - much faster than checking all"""
        candidates = set()
        
        # Check prefix matches
        if len(company_name) >= 3:
            prefix3 = company_name[:3]
            if prefix3 in self.prefix_index:
                candidates.update(self.prefix_index[prefix3])
            
            if len(company_name) >= 5:
                prefix5 = company_name[:5]
                if prefix5 in self.prefix_index:
                    candidates.update(self.prefix_index[prefix5])
        
        # Check token matches
        tokens = company_name.split()
        if tokens:
            first_token = tokens[0]
            if first_token in self.token_index:
                candidates.update(self.token_index[first_token])
        
        # If no candidates found, check similar prefixes
        if not candidates and len(company_name) >= 3:
            prefix = company_name[:3]
            # Check prefixes that are one character different
            for key in self.prefix_index:
                if len(key) >= 3 and key[:2] == prefix[:2]:
                    candidates.update(self.prefix_index[key][:50])  # Limit to top 50
        
        return list(candidates)
    
    def fast_match_single(self, company_data):
        """Fast matching for a single company"""
        company_name = company_data['clean_name']
        original_name = company_data['original_name']
        
        if not company_name:
            return {
                'original_company': original_name,
                'clean_company': company_name,
                'matched_name': "",
                'document_number': "",
                'similarity_score': 0,
                'match_quality': 'No Match',
                'match_method': 'None'
            }
        
        # Step 1: Check exact match (instant)
        if company_name in self.exact_match_index:
            return {
                'original_company': original_name,
                'clean_company': company_name,
                'matched_name': company_name,
                'document_number': self.exact_match_index[company_name],
                'similarity_score': 100,
                'match_quality': 'Exact',
                'match_method': 'Exact'
            }
        
        # Step 2: Find candidates using indexes (fast)
        candidates = self.find_candidates(company_name)
        
        if not candidates:
            # No candidates found
            return {
                'original_company': original_name,
                'clean_company': company_name,
                'matched_name': "",
                'document_number': "",
                'similarity_score': 0,
                'match_quality': 'No Match',
                'match_method': 'No Candidates'
            }
        
        # Step 3: Score only candidates (much faster than all records)
        best_match = None
        best_score = 0
        
        # Use rapidfuzz for faster fuzzy matching
        candidate_names = [c[0] for c in candidates]
        candidate_docs = {c[0]: c[1] for c in candidates}
        
        # Get best match from candidates
        result = process.extractOne(
            company_name,
            candidate_names,
            scorer=fuzz.ratio,
            score_cutoff=self.match_threshold
        )
        
        if result:
            matched_name, score, _ = result
            return {
                'original_company': original_name,
                'clean_company': company_name,
                'matched_name': matched_name,
                'document_number': candidate_docs[matched_name],
                'similarity_score': score,
                'match_quality': self.get_match_quality(score),
                'match_method': 'Fuzzy'
            }
        
        # No good match found
        return {
            'original_company': original_name,
            'clean_company': company_name,
            'matched_name': "",
            'document_number': "",
            'similarity_score': 0,
            'match_quality': 'No Match',
            'match_method': 'Below Threshold'
        }
    
    def get_match_quality(self, score):
        """Determine match quality"""
        if score == 100:
            return 'Exact'
        elif score >= 95:
            return 'Excellent'
        elif score >= 85:
            return 'Very Good'
        elif score >= 75:
            return 'Good'
        else:
            return 'Fair'
    
    def match_batch(self, batch_data):
        """Process a batch of companies"""
        results = []
        for company_data in batch_data:
            result = self.fast_match_single(company_data)
            results.append(result)
        return results
    
    def match_companies_parallel(self, companies_df, officers_df, n_workers=None):
        """Parallel processing for maximum speed"""
        
        print("\n" + "="*80)
        print("FAST DOCUMENT MATCHING SYSTEM")
        print("="*80)
        
        # Build indexes
        print("\nPhase 1: Building indexes...")
        self.build_indexes(officers_df)
        
        # Prepare company data
        print("\nPhase 2: Preparing company data...")
        company_data = []
        for _, row in companies_df.iterrows():
            company_data.append({
                'original_name': row.get('Company', ''),
                'clean_name': row['clean_name']
            })
        
        print(f"  [PREPARED] {len(company_data):,} companies for matching")
        
        # Process in batches
        print("\nPhase 3: Matching companies...")
        
        # Single-threaded processing (often faster for this type of work)
        results = []
        batch_size = 100
        total_batches = (len(company_data) + batch_size - 1) // batch_size
        
        for i in range(0, len(company_data), batch_size):
            batch = company_data[i:i + batch_size]
            batch_results = self.match_batch(batch)
            results.extend(batch_results)
            
            # Progress update
            current_batch = (i // batch_size) + 1
            if current_batch % 10 == 0 or current_batch == total_batches:
                progress = (i + len(batch)) / len(company_data) * 100
                print(f"  Progress: {progress:.1f}% ({i + len(batch):,}/{len(company_data):,} companies)")
        
        return pd.DataFrame(results)

def load_data_efficiently(csv_file, excel_file):
    """Load data files efficiently"""
    
    # Load officers data
    print(f"Loading officers data from {csv_file}...")
    
    # Read only needed columns to save memory
    try:
        # First, check what columns are available
        sample = pd.read_csv(csv_file, nrows=5)
        
        # Try to find the document number column
        doc_col = None
        company_col = None
        
        for col in sample.columns:
            if 'doc' in col.lower() and 'number' in col.lower():
                doc_col = col
            elif 'doc_number' in col.lower():
                doc_col = col
            
            if 'company' in col.lower() and 'name' in col.lower():
                company_col = col
            elif 'company_name' in col.lower():
                company_col = col
        
        if not doc_col or not company_col:
            print("Could not find required columns. Using defaults...")
            doc_col = 'doc_number'
            company_col = 'company_name'
        
        # Load data
        officers_df = pd.read_csv(csv_file, usecols=[doc_col, company_col])
        officers_df.columns = ['doc_number', 'company_name']
        
    except Exception as e:
        print(f"Error reading CSV, trying all columns: {e}")
        officers_df = pd.read_csv(csv_file)
        # Rename columns if needed
        if 'doc_number' not in officers_df.columns:
            for col in officers_df.columns:
                if 'doc' in col.lower():
                    officers_df.rename(columns={col: 'doc_number'}, inplace=True)
                    break
        if 'company_name' not in officers_df.columns:
            for col in officers_df.columns:
                if 'company' in col.lower():
                    officers_df.rename(columns={col: 'company_name'}, inplace=True)
                    break
    
        print(f"  [LOADED] {len(officers_df):,} officer records")
    
    # Load companies
    print(f"Loading companies from {excel_file}...")
    companies_df = pd.read_excel(excel_file)
    print(f"  [LOADED] {len(companies_df):,} companies")
    
    return officers_df, companies_df

def main():
    """Main execution function"""
    
    start_time = datetime.now()
    print("="*80)
    print("ULTRA-FAST DOCUMENT NUMBER MATCHER")
    print("="*80)
    print(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"CPU cores available: {cpu_count()}")
    
    # File paths
    companies_file = 'Corps 10-2-25.xlsx'
    officers_file = 'new_officer_sheet_20251004_161742.csv'
    
    # Load data efficiently
    try:
        officers_df, companies_df = load_data_efficiently(officers_file, companies_file)
    except Exception as e:
        print(f"Error loading data: {e}")
        return None
    
    # Clean names
    print("\nCleaning company names...")
    matcher = FastDocumentMatcher(match_threshold=80)
    
    officers_df['clean_name'] = officers_df['company_name'].apply(matcher.clean_company_name)
    companies_df['clean_name'] = companies_df['Company'].apply(matcher.clean_company_name)
    
    # Remove duplicates from officers to speed up matching
    print("Removing duplicate entries...")
    officers_df = officers_df.drop_duplicates(subset=['clean_name', 'doc_number'])
    print(f"  [REDUCED] {len(officers_df):,} unique officer records")
    
    # Run matching
    results_df = matcher.match_companies_parallel(companies_df, officers_df)
    
    # Add statistics
    total_companies = len(results_df)
    matched_companies = len(results_df[results_df['document_number'] != ''])
    exact_matches = len(results_df[results_df['match_quality'] == 'Exact'])
    match_rate = (matched_companies / total_companies) * 100 if total_companies > 0 else 0
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f'fast_document_matches_{timestamp}.xlsx'
    
    print("\nSaving results...")
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Main results
        results_df.to_excel(writer, sheet_name='Matches', index=False)
        
        # Summary statistics
        summary = pd.DataFrame({
            'Metric': [
                'Total Companies',
                'Matched Companies',
                'Match Rate',
                'Exact Matches',
                'Fuzzy Matches',
                'Processing Time'
            ],
            'Value': [
                f"{total_companies:,}",
                f"{matched_companies:,}",
                f"{match_rate:.1f}%",
                f"{exact_matches:,}",
                f"{matched_companies - exact_matches:,}",
                str(datetime.now() - start_time).split('.')[0]
            ]
        })
        summary.to_excel(writer, sheet_name='Summary', index=False)
        
        # Format worksheets
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
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
    
    # Print summary
    print("\n" + "="*80)
    print("MATCHING COMPLETE!")
    print("="*80)
    print(f"Total companies: {total_companies:,}")
    print(f"Matched companies: {matched_companies:,} ({match_rate:.1f}%)")
    print(f"Exact matches: {exact_matches:,}")
    print(f"Fuzzy matches: {matched_companies - exact_matches:,}")
    print(f"No matches: {total_companies - matched_companies:,}")
    print(f"\nProcessing time: {datetime.now() - start_time}")
    print(f"Output saved to: {output_file}")
    
    # Show sample results
    print("\nSample matched companies:")
    print("-" * 50)
    sample = results_df[results_df['document_number'] != ''].head(5)
    for _, row in sample.iterrows():
        print(f"{row['original_company'][:40]:<40} -> {row['document_number']} ({row['similarity_score']:.0f}%)")
    
    # Clean up memory
    del officers_df, companies_df
    gc.collect()
    
    return results_df

if __name__ == "__main__":
    # Try to install rapidfuzz if not available
    try:
        from rapidfuzz import fuzz, process
    except ImportError:
        print("Installing rapidfuzz for better performance...")
        import subprocess
        subprocess.check_call(['pip', 'install', 'rapidfuzz'])
        from rapidfuzz import fuzz, process
    
    results = main()