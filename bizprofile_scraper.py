import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import quote, urljoin
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class BizprofileScraper:
    """Web scraper for Bizprofile.net to find company document numbers"""
    
    def __init__(self):
        self.base_url = "https://www.bizprofile.net"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.results = []
        
    def search_company(self, company_name, state=None):
        """Search for a company on Bizprofile.net"""
        try:
            # Clean company name for search
            search_term = self.clean_search_term(company_name)
            
            # Construct search URL
            search_url = f"{self.base_url}/search"
            params = {
                'q': search_term,
                'type': 'company'
            }
            if state:
                params['state'] = state
                
            print(f"Searching for: {search_term}")
            
            response = self.session.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            
            # Parse the response
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract company information
            companies = self.extract_company_data(soup, company_name)
            
            return companies
            
        except Exception as e:
            print(f"Error searching for {company_name}: {str(e)}")
            return []
    
    def clean_search_term(self, company_name):
        """Clean company name for better search results"""
        # Remove common suffixes
        suffixes = ['LLC', 'INC', 'CORP', 'LTD', 'LP', 'PA', 'PLLC', 'PC']
        cleaned = company_name.upper().strip()
        
        for suffix in suffixes:
            if cleaned.endswith(f' {suffix}'):
                cleaned = cleaned[:-len(f' {suffix}')].strip()
                break
                
        return cleaned
    
    def extract_company_data(self, soup, original_name):
        """Extract company data from search results page"""
        companies = []
        
        # Look for company listings in the search results
        # This is a generic approach - you may need to adjust based on actual HTML structure
        company_cards = soup.find_all(['div', 'article'], class_=re.compile(r'company|business|listing', re.I))
        
        if not company_cards:
            # Try alternative selectors
            company_cards = soup.find_all('div', class_=re.compile(r'result|item', re.I))
        
        for card in company_cards[:5]:  # Limit to first 5 results
            try:
                company_data = self.parse_company_card(card, original_name)
                if company_data:
                    companies.append(company_data)
            except Exception as e:
                print(f"Error parsing company card: {str(e)}")
                continue
                
        return companies
    
    def parse_company_card(self, card, original_name):
        """Parse individual company card to extract information"""
        try:
            # Extract company name
            name_elem = card.find(['h1', 'h2', 'h3', 'a'], class_=re.compile(r'name|title|company', re.I))
            if not name_elem:
                name_elem = card.find('a')
            
            company_name = name_elem.get_text(strip=True) if name_elem else ""
            
            # Extract document number (look for patterns like L123456789 or P123456789)
            doc_number = self.extract_document_number(card)
            
            # Extract other details
            address = self.extract_address(card)
            state = self.extract_state(card)
            
            # Calculate similarity with original name
            similarity = self.calculate_similarity(original_name.upper(), company_name.upper())
            
            return {
                'original_name': original_name,
                'found_name': company_name,
                'document_number': doc_number,
                'address': address,
                'state': state,
                'similarity_score': similarity,
                'source_url': self.extract_company_url(card)
            }
            
        except Exception as e:
            print(f"Error parsing company card: {str(e)}")
            return None
    
    def extract_document_number(self, card):
        """Extract document number from company card"""
        # Look for document number patterns
        text = card.get_text()
        
        # Pattern for Florida document numbers (L followed by 11 digits)
        fl_pattern = r'L\d{11}'
        fl_match = re.search(fl_pattern, text)
        if fl_match:
            return fl_match.group()
        
        # Pattern for other document numbers (P followed by 11 digits)
        p_pattern = r'P\d{11}'
        p_match = re.search(p_pattern, text)
        if p_match:
            return p_match.group()
        
        # Look for any 11-12 digit number
        doc_pattern = r'[A-Z]?\d{11,12}'
        doc_match = re.search(doc_pattern, text)
        if doc_match:
            return doc_match.group()
            
        return ""
    
    def extract_address(self, card):
        """Extract address information"""
        # Look for address patterns
        address_elem = card.find(['div', 'span'], class_=re.compile(r'address|location', re.I))
        if address_elem:
            return address_elem.get_text(strip=True)
        return ""
    
    def extract_state(self, card):
        """Extract state information"""
        text = card.get_text()
        # Look for state abbreviations
        state_pattern = r'\b(FL|CA|NY|TX|WA|IL|PA|OH|GA|NC|MI|NJ|VA|TN|IN|AZ|MA|MD|MO|WI|CO|MN|SC|AL|LA|KY|OR|OK|CT|UT|IA|NV|AR|MS|KS|NM|NE|WV|ID|HI|NH|ME|RI|MT|DE|SD|ND|AK|VT|WY)\b'
        state_match = re.search(state_pattern, text)
        if state_match:
            return state_match.group()
        return ""
    
    def extract_company_url(self, card):
        """Extract company detail page URL"""
        link_elem = card.find('a', href=True)
        if link_elem:
            href = link_elem['href']
            if href.startswith('/'):
                return urljoin(self.base_url, href)
            return href
        return ""
    
    def calculate_similarity(self, str1, str2):
        """Calculate similarity between two strings"""
        if not str1 or not str2:
            return 0
        
        # Simple similarity calculation
        str1_words = set(str1.split())
        str2_words = set(str2.split())
        
        if not str1_words or not str2_words:
            return 0
        
        intersection = str1_words.intersection(str2_words)
        union = str1_words.union(str2_words)
        
        return len(intersection) / len(union) * 100
    
    def search_companies_batch(self, company_list, delay=2):
        """Search for multiple companies with delay between requests"""
        results = []
        
        for i, company in enumerate(company_list):
            print(f"Processing {i+1}/{len(company_list)}: {company}")
            
            companies = self.search_company(company)
            results.extend(companies)
            
            # Add delay to be respectful to the server
            if i < len(company_list) - 1:
                time.sleep(delay)
        
        return results
    
    def save_results(self, filename=None):
        """Save results to Excel file"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'bizprofile_search_results_{timestamp}.xlsx'
        
        if self.results:
            df = pd.DataFrame(self.results)
            df.to_excel(filename, index=False)
            print(f"Results saved to: {filename}")
        else:
            print("No results to save")

def main():
    """Main function to demonstrate usage"""
    scraper = BizprofileScraper()
    
    # Example company names to search
    sample_companies = [
        "ABC Construction LLC",
        "XYZ Corporation",
        "Smith & Associates Inc"
    ]
    
    print("Starting Bizprofile.net search...")
    print("=" * 50)
    
    # Search for companies
    results = scraper.search_companies_batch(sample_companies)
    
    # Display results
    if results:
        print(f"\nFound {len(results)} potential matches:")
        print("-" * 50)
        
        for result in results:
            print(f"Original: {result['original_name']}")
            print(f"Found: {result['found_name']}")
            print(f"Document: {result['document_number']}")
            print(f"Similarity: {result['similarity_score']:.1f}%")
            print(f"State: {result['state']}")
            print("-" * 30)
    else:
        print("No results found")
    
    # Save results
    scraper.results = results
    scraper.save_results()

if __name__ == "__main__":
    main()
