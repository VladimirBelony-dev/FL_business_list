#!/usr/bin/env python3
"""
Test script for the Document Number Matcher
This script demonstrates how to find document numbers for company names
"""

from document_number_matcher import DocumentNumberMatcher
import pandas as pd

def test_document_matcher():
    """Test the document number matcher with sample data"""
    
    print("TESTING DOCUMENT NUMBER MATCHER")
    print("=" * 50)
    
    # Initialize the matcher
    matcher = DocumentNumberMatcher()
    
    # Test with a small sample first
    print("Testing with sample companies...")
    
    # Create sample companies DataFrame
    sample_companies = pd.DataFrame({
        'Company': [
            'ABC Construction LLC',
            'XYZ Corporation Inc',
            'Smith & Associates',
            'Johnson Enterprises LLC',
            'Test Company Inc'
        ]
    })
    
    # Save sample to Excel for testing
    sample_file = 'sample_companies.xlsx'
    sample_companies.to_excel(sample_file, index=False)
    print(f"Created sample file: {sample_file}")
    
    # Try to load officers data
    officers_file = 'officers_clean_20251004_105517.csv'
    
    try:
        # Test loading officers data (first 1000 rows)
        print(f"Loading officers data from {officers_file}...")
        officers_sample = pd.read_csv(officers_file, nrows=1000)
        officers_sample.to_csv('officers_sample.csv', index=False)
        print(f"Created sample officers file: officers_sample.csv")
        
        # Run the matcher
        results = matcher.match_companies_with_documents(
            companies_file=sample_file,
            officers_file='officers_sample.csv',
            company_column='Company',
            output_file='test_results.xlsx'
        )
        
        print("\nTest completed successfully!")
        return results
        
    except FileNotFoundError:
        print(f"Error: {officers_file} not found")
        print("Please make sure the officers data file exists")
        return None
    except Exception as e:
        print(f"Error during testing: {str(e)}")
        return None

def main():
    """Main function"""
    results = test_document_matcher()
    
    if results is not None:
        print("\nSample results:")
        print("-" * 30)
        print(results[['original_company', 'document_number', 'similarity_score']].head())
    else:
        print("Test failed. Please check your data files.")

if __name__ == "__main__":
    main()
