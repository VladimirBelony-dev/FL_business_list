"""
Tests for document matching functionality
"""

import pytest
import pandas as pd
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from document_number_matcher import FastDocumentMatcher

class TestDocumentMatching:
    """Test cases for document matching functions"""
    
    def setup_method(self):
        """Set up test data"""
        self.matcher = FastDocumentMatcher(match_threshold=80)
        
        # Create sample officer data
        self.officers_data = {
            'company_name': ['WOYUNTANG LLC', 'ACME CORP', 'TEST INC'],
            'doc_number': ['L24000326550', 'L24000326551', 'L24000326552']
        }
        self.officers_df = pd.DataFrame(self.officers_data)
        self.officers_df['clean_name'] = self.officers_df['company_name'].apply(self.matcher.clean_company_name)
        
        # Create sample company data
        self.companies_data = {
            'Company': ['WOYUNTANG LLC', 'ACME CORPORATION', 'TEST INCORPORATED']
        }
        self.companies_df = pd.DataFrame(self.companies_data)
        self.companies_df['clean_name'] = self.companies_df['Company'].apply(self.matcher.clean_company_name)
    
    def test_clean_company_name(self):
        """Test company name cleaning function"""
        test_cases = [
            ("WOYUNTANG LLC", "WOYUNTANG LLC"),
            ("acme corp", "ACME CORP"),
            ("Test, Inc.", "TEST INC"),
            ("A & B Company", "A & B COMPANY"),
            ("", ""),
            (None, "")
        ]
        
        for input_name, expected in test_cases:
            result = self.matcher.clean_company_name(input_name)
            assert result == expected, f"Failed for input: {input_name}"
    
    def test_exact_match(self):
        """Test exact matching functionality"""
        # Build indexes
        self.matcher.build_indexes(self.officers_df)
        
        # Test exact match
        company_data = {
            'original_name': 'WOYUNTANG LLC',
            'clean_name': 'WOYUNTANG LLC'
        }
        
        result = self.matcher.fast_match_single(company_data)
        
        assert result['match_quality'] == 'Exact'
        assert result['similarity_score'] == 100
        assert result['document_number'] == 'L24000326550'
    
    def test_fuzzy_match(self):
        """Test fuzzy matching functionality"""
        # Build indexes
        self.matcher.build_indexes(self.officers_df)
        
        # Test fuzzy match
        company_data = {
            'original_name': 'ACME CORPORATION',
            'clean_name': 'ACME CORPORATION'
        }
        
        result = self.matcher.fast_match_single(company_data)
        
        # Should find a match with ACME CORP
        assert result['match_quality'] in ['Exact', 'Excellent', 'Very Good', 'Good', 'Fair']
        assert result['similarity_score'] >= 80
    
    def test_no_match(self):
        """Test handling of no match scenarios"""
        # Build indexes
        self.matcher.build_indexes(self.officers_df)
        
        # Test no match
        company_data = {
            'original_name': 'NONEXISTENT COMPANY',
            'clean_name': 'NONEXISTENT COMPANY'
        }
        
        result = self.matcher.fast_match_single(company_data)
        
        assert result['match_quality'] == 'No Match'
        assert result['similarity_score'] == 0
        assert result['document_number'] == ""
    
    def test_index_building(self):
        """Test index building functionality"""
        self.matcher.build_indexes(self.officers_df)
        
        # Check that indexes were built
        assert len(self.matcher.exact_match_index) > 0
        assert len(self.matcher.prefix_index) > 0
        assert len(self.matcher.token_index) > 0
        
        # Check specific entries
        assert 'WOYUNTANG LLC' in self.matcher.exact_match_index
        assert 'WOY' in self.matcher.prefix_index
        assert 'WOYUNTANG' in self.token_index
    
    def test_candidate_finding(self):
        """Test candidate finding functionality"""
        self.matcher.build_indexes(self.officers_df)
        
        # Test finding candidates
        candidates = self.matcher.find_candidates('WOYUNTANG LLC')
        
        assert len(candidates) > 0
        assert any('WOYUNTANG' in candidate[0] for candidate in candidates)

if __name__ == "__main__":
    pytest.main([__file__])

