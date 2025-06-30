#!/usr/bin/env python3
"""
Test subscription date filtering in Naver scraper
"""
import logging
from scrapers.naver_scraper import NaverScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_subscription_filter():
    """Test the subscription date filtering"""
    scraper = NaverScraper()
    
    print("\n=== Testing Naver IPO List with Subscription Date Filter ===\n")
    
    # Get filtered IPO list
    ipo_list = scraper.get_ipo_list()
    
    print(f"\nTotal IPOs found with target underwriters AND subscription dates: {len(ipo_list)}")
    
    if ipo_list:
        print("\nIPOs with subscription dates:")
        for idx, ipo in enumerate(ipo_list, 1):
            print(f"\n{idx}. {ipo['company_name']} ({ipo['stock_code']})")
            print(f"   - Market: {ipo.get('market_type', 'N/A')}")
            print(f"   - Underwriters: {ipo.get('underwriters', 'N/A')}")
            print(f"   - Status: {ipo.get('status', 'N/A')}")
            print(f"   - Subscription Date: {ipo.get('subscription_date', 'N/A')}")
            print(f"   - Offering Price: {ipo.get('offering_price', 'N/A')}")
    else:
        print("\nNo IPOs found with both target underwriters and subscription dates.")

if __name__ == "__main__":
    test_subscription_filter() 