import pandas as pd
import numpy as np
from fuzzywuzzy import fuzz, process
import re
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class QuickDocumentMatcher:
    """Quick document number matcher with progress tracking"""
    
    def __init__(self):
        self.match_threshold = 80  # Minimum similarity score for matching
        self.results = []
        
    def clean_company_name(self, name):
        """Standardize company names for better matching - case insensitive but keep full names"""
        if pd.isna(name):
            return ""
        
        # Convert to uppercase for case-insensitive matching
        name = str(name).upper().strip()
        
        # Only normalize spaces and special characters, keep all suffixes and full names
        # Remove extra special characters but keep common business characters
        name = re.sub(r'[^\w\s\.&]', ' ', name)
        # Normalize multiple spaces to single space
        name = ' '.join(name.split())
        
        return name
    
    def load_sample_data(self, companies_file, officers_file, sample_size=100):
        """Load a sample of data for quick testing"""
        print(f"Loading sample of {sample_size} companies...")
        
        # Load sample companies
        companies_df = pd.read_excel(companies_file, nrows=sample_size)
        companies_df['clean_name'] = companies_df['Company'].apply(self.clean_company_name)
        
        print(f"Loading sample officers data...")
        # Load sample officers data
        officers_df = pd.read_csv(officers_file, nrows=10000)  # Load 10k officers for matching
        officers_df['clean_name'] = officers_df['company_name'].apply(self.clean_company_name)
        
        return companies_df, officers_df
    
    def find_matches_quick(self, companies_df, officers_df):
        """Quick matching with progress tracking"""
        matches = []
        total = len(companies_df)
        
        print(f"Processing {total} companies...")
        print("=" * 50)
        
        # Create a lookup dictionary for faster matching
        officer_lookup = {}
        for _, row in officers_df.iterrows():
            clean_name = row['clean_name']
            if clean_name not in officer_lookup:
                officer_lookup[clean_name] = []
            officer_lookup[clean_name].append({
                'doc_number': row['doc_number'],
                'company_name': row['company_name']
            })
        
        for idx, company_row in companies_df.iterrows():
            if idx % 10 == 0:  # Show progress every 10 companies
                print(f"Progress: {idx+1}/{total} ({(idx+1)/total*100:.1f}%)")
            
            company_name = company_row['clean_name']
            original_name = company_row['Company']
            
            if not company_name:
                matches.append({
                    'original_company': original_name,
                    'document_number': '',
                    'similarity_score': 0,
                    'match_quality': 'No Match'
                })
                continue
            
            # Try exact match first
            if company_name in officer_lookup:
                best_match = officer_lookup[company_name][0]
                matches.append({
                    'original_company': original_name,
                    'matched_company': best_match['company_name'],
                    'document_number': best_match['doc_number'],
                    'similarity_score': 100,
                    'match_quality': 'Exact Match'
                })
                continue
            
            # Try fuzzy matching with a subset of officers
            # Sample officers for fuzzy matching to speed up
            sample_officers = officers_df.sample(min(1000, len(officers_df)))
            officer_names = sample_officers['clean_name'].tolist()
            
            # Get best fuzzy match
            best_match = process.extractOne(
                company_name, 
                officer_names, 
                scorer=fuzz.ratio
            )
            
            if best_match and best_match[1] >= self.match_threshold:
                # Find the document number for the best match
                matched_officer = sample_officers[
                    sample_officers['clean_name'] == best_match[0]
                ].iloc[0]
                
                matches.append({
                    'original_company': original_name,
                    'matched_company': matched_officer['company_name'],
                    'document_number': matched_officer['doc_number'],
                    'similarity_score': best_match[1],
                    'match_quality': self.get_match_quality(best_match[1])
                })
            else:
                matches.append({
                    'original_company': original_name,
                    'matched_company': '',
                    'document_number': '',
                    'similarity_score': 0,
                    'match_quality': 'No Match'
                })
        
        return matches
    
    def get_match_quality(self, score):
        """Determine match quality based on score"""
        if score >= 95:
            return 'Excellent'
        elif score >= 85:
            return 'Very Good'
        elif score >= 75:
            return 'Good'
        elif score >= 65:
            return 'Fair'
        else:
            return 'Poor'
    
    def run_quick_match(self, companies_file, officers_file, sample_size=100):
        """Run quick matching with sample data"""
        print("QUICK DOCUMENT NUMBER MATCHER")
        print("=" * 50)
        print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Load sample data
        companies_df, officers_df = self.load_sample_data(
            companies_file, officers_file, sample_size
        )
        
        # Find matches
        matches = self.find_matches_quick(companies_df, officers_df)
        
        # Create results DataFrame
        results_df = pd.DataFrame(matches)
        
        # Statistics
        total_companies = len(results_df)
        matched_companies = len(results_df[results_df['document_number'] != ''])
        match_rate = (matched_companies / total_companies) * 100 if total_companies > 0 else 0
        
        print("\n" + "=" * 50)
        print("QUICK MATCHING RESULTS")
        print("=" * 50)
        print(f"Sample size: {total_companies:,}")
        print(f"Matched companies: {matched_companies:,}")
        print(f"Match rate: {match_rate:.1f}%")
        print()
        
        # Quality breakdown
        quality_counts = results_df['match_quality'].value_counts()
        print("Match Quality Breakdown:")
        for quality, count in quality_counts.items():
            print(f"  {quality}: {count:,}")
        print()
        
        # Save results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f'quick_document_matches_{timestamp}.xlsx'
        results_df.to_excel(output_file, index=False)
        print(f"Results saved to: {output_file}")
        
        # Show sample results
        print("\nSample Results:")
        print("-" * 50)
        sample_results = results_df[results_df['document_number'] != ''].head(10)
        for _, row in sample_results.iterrows():
            print(f"{row['original_company']} -> {row['document_number']} ({row['similarity_score']}%)")
        
        return results_df

def main():
    """Main function for quick testing"""
    matcher = QuickDocumentMatcher()
    
    # File paths
    companies_file = 'Corps 10-2-25.xlsx'
    officers_file = 'officers_clean_20251004_105517.csv'
    
    # Run quick matching with first 100 companies
    results = matcher.run_quick_match(
        companies_file=companies_file,
        officers_file=officers_file,
        sample_size=100
    )
    
    return results

if __name__ == "__main__":
    main()
