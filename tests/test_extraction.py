"""
Tests for data extraction functionality
"""

import pytest
import pandas as pd
from pathlib import Path
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extract_officers_full import extract_officer_from_line

class TestDataExtraction:
    """Test cases for data extraction functions"""
    
    def test_company_name_extraction(self):
        """Test company name extraction from line"""
        # Sample line with known company name
        test_line = "L24000326550WOYUNTANG LLC                   123 MAIN ST                    WILMINGTON DE19801                    JOHN DOE CEO"
        
        result = extract_officer_from_line(test_line)
        
        assert result is not None
        assert result['company_name'] == "WOYUNTANG LLC"
        assert result['doc_number'] == "L24000326550"
    
    def test_address_extraction(self):
        """Test address extraction from line"""
        test_line = "L24000326550WOYUNTANG LLC                   123 MAIN ST                    WILMINGTON DE19801                    JOHN DOE CEO"
        
        result = extract_officer_from_line(test_line)
        
        assert result is not None
        assert "123 MAIN ST" in result['address']
        assert result['city'] == "WILMINGTON"
        assert result['state'] == "DE"
        assert result['zip_code'] == "19801"
    
    def test_officer_extraction(self):
        """Test officer information extraction"""
        test_line = "L24000326550WOYUNTANG LLC                   123 MAIN ST                    WILMINGTON DE19801                    JOHN DOE CEO"
        
        result = extract_officer_from_line(test_line)
        
        assert result is not None
        assert "JOHN DOE" in result['officer_full_name']
        assert result['officer_role'] == "CEO"
    
    def test_empty_line_handling(self):
        """Test handling of empty or invalid lines"""
        empty_line = ""
        short_line = "L24000326550"
        
        result1 = extract_officer_from_line(empty_line)
        result2 = extract_officer_from_line(short_line)
        
        assert result1 is None
        assert result2 is None
    
    def test_malformed_line_handling(self):
        """Test handling of malformed lines"""
        malformed_line = "INVALID_LINE_WITHOUT_PROPER_FORMAT"
        
        result = extract_officer_from_line(malformed_line)
        
        # Should return None or handle gracefully
        assert result is None or isinstance(result, dict)

if __name__ == "__main__":
    pytest.main([__file__])

