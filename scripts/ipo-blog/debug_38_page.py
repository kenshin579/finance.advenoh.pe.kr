#!/usr/bin/env python3
"""
Debug script to analyze 38 Communications IPO page structure
"""
import requests
from bs4 import BeautifulSoup
import logging
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def analyze_38_page(url):
    """Download and analyze 38 Communications page"""
    
    # Test URL - 뉴엔에이아이
    if not url:
        url = "https://www.38.co.kr/html/fund/?o=v&no=2192"
    
    print(f"\n=== Analyzing 38 Communications Page ===")
    print(f"URL: {url}\n")
    
    # Download page
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    try:
        response = session.get(url, verify=False, timeout=10)
        response.encoding = 'euc-kr'
        
        # Save HTML for inspection
        with open('38comm_debug.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("✓ Saved HTML to 38comm_debug.html")
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all tables
        tables = soup.find_all('table')
        print(f"\n✓ Found {len(tables)} tables")
        
        # Analyze each table
        for idx, table in enumerate(tables):
            print(f"\n--- Table {idx + 1} ---")
            
            # Get table headers
            headers = []
            header_row = table.find('tr')
            if header_row:
                for th in header_row.find_all(['th', 'td']):
                    headers.append(th.get_text(strip=True))
            
            if headers:
                print(f"Headers: {headers}")
            
            # Get first few rows to understand structure
            rows = table.find_all('tr')[1:4]  # Get first 3 data rows
            for row_idx, row in enumerate(rows):
                cells = [cell.get_text(strip=True) for cell in row.find_all(['td', 'th'])]
                if cells:
                    print(f"Row {row_idx + 1}: {cells}")
        
        # Look for specific keywords
        print("\n=== Searching for Key Information ===")
        
        keywords = [
            "희망공모가", "확정공모가", "공모금액", "공모주식수",
            "수요예측", "기관경쟁률", "통합경쟁률",
            "주간사", "대표주관", "청약일", "상장일",
            "매출액", "영업이익", "당기순이익", "자본금",
            "업종", "주요제품", "최대주주"
        ]
        
        for keyword in keywords:
            elements = soup.find_all(text=lambda text: keyword in text if text else False)
            if elements:
                print(f"\n✓ Found '{keyword}' in {len(elements)} places:")
                for elem in elements[:2]:  # Show first 2 occurrences
                    parent = elem.parent
                    if parent:
                        # Try to get the associated value
                        next_sibling = parent.find_next_sibling()
                        if next_sibling:
                            value = next_sibling.get_text(strip=True)
                            print(f"  - {elem.strip()} → {value}")
                        else:
                            # Check if value is in the same row
                            row = parent.find_parent('tr')
                            if row:
                                cells = row.find_all(['td', 'th'])
                                cell_texts = [c.get_text(strip=True) for c in cells]
                                print(f"  - Row: {cell_texts}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Test with 뉴엔에이아이
    analyze_38_page("https://www.38.co.kr/html/fund/?o=v&no=2192") 