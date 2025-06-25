"""
Test script for Naver IPO scraper
"""
import logging
import json
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scrapers.naver_scraper import NaverScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_naver_scraper():
    """Test the Naver scraper functionality"""
    print("=" * 50)
    print("Testing Naver IPO Scraper")
    print("=" * 50)
    
    # Create scraper instance
    scraper = NaverScraper()
    
    # Debug: Check HTML structure
    print("\n0. Debugging HTML structure...")
    soup = scraper.get_soup(scraper.ipo_list_url)
    if soup:
        # Save HTML to file for inspection
        with open('ipo_page.html', 'w', encoding='utf-8') as f:
            f.write(str(soup.prettify()))
        print("HTML saved to ipo_page.html")
        
        # Check for tables
        tables = soup.find_all('table')
        print(f"Found {len(tables)} tables")
        for i, table in enumerate(tables):
            classes = table.get('class', [])
            print(f"  Table {i}: classes={classes}")
    
    # Test 1: Get IPO list
    print("\n1. Fetching IPO list...")
    ipo_list = scraper.get_ipo_list()
    
    if not ipo_list:
        print("No IPOs found with target underwriters.")
        return
    
    print(f"\nFound {len(ipo_list)} IPOs with target underwriters:")
    for i, ipo in enumerate(ipo_list, 1):
        print(f"\n{i}. {ipo['company_name']} ({ipo['stock_code']})")
        print(f"   - Market: {ipo['market_type']}")
        print(f"   - Industry: {ipo['industry']}")
        print(f"   - Underwriters: {ipo['underwriters']}")
        print(f"   - Offering Amount: {ipo['offering_amount']}억원")
        print(f"   - Competition Rate: {ipo['competition_rate']}")
        print(f"   - Subscription Date: {ipo['subscription_date']}")
        print(f"   - Listing Date: {ipo['listing_date']}")
    
    # Test 2: Get detail for first IPO
    if ipo_list:
        print("\n" + "=" * 50)
        print("2. Testing IPO detail fetch...")
        first_ipo = ipo_list[0]
        print(f"\nFetching details for: {first_ipo['company_name']} ({first_ipo['stock_code']})")
        
        detail = scraper.get_ipo_detail(first_ipo['stock_code'])
        
        if detail:
            print("\nDetailed Information:")
            print(json.dumps(detail, indent=2, ensure_ascii=False))
        else:
            print("Failed to fetch detail information.")
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    test_naver_scraper() 