"""
Debug IPO list page to find 대한조선
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.base_scraper import BaseScraper
from bs4 import BeautifulSoup
import re

def debug_ipo_list():
    """Debug IPO list page structure"""
    scraper = BaseScraper()
    
    # Get IPO list page
    ipo_list_url = "https://www.38.co.kr/html/fund/index.htm?o=r"
    
    print("1. Fetching IPO list page...")
    soup = scraper.get_soup(ipo_list_url)
    if not soup:
        print("Failed to fetch page")
        return
    
    # Save the page for analysis
    with open('ipo_list_page.html', 'w', encoding='utf-8') as f:
        f.write(soup.prettify())
    print("   Saved to ipo_list_page.html")
    
    # Find all tables
    tables = soup.find_all('table')
    print(f"\n2. Found {len(tables)} tables")
    
    # Look for 대한조선
    print("\n3. Looking for '대한조선'...")
    found = False
    
    for idx, table in enumerate(tables):
        if '대한조선' in table.get_text():
            print(f"\n   Found '대한조선' in table {idx}")
            found = True
            
            # Check if this is an IPO table
            table_text = table.get_text()
            if any(keyword in table_text for keyword in ['수요예측일', '희망공모가', '공모금액', '주간사']):
                print("   This is an IPO table!")
                
                # Find the specific row
                for row_idx, row in enumerate(table.find_all('tr')):
                    if '대한조선' in row.get_text():
                        print(f"\n   Found in row {row_idx}")
                        
                        # Print row HTML
                        print("   Row HTML:")
                        print("   " + "-"*60)
                        print(row.prettify()[:1000])
                        print("   " + "-"*60)
                        
                        # Check all cells
                        cells = row.find_all(['td', 'th'])
                        for cell_idx, cell in enumerate(cells):
                            cell_text = cell.get_text(strip=True)
                            print(f"\n   Cell {cell_idx}: {cell_text[:50]}...")
                            
                            # Check for onclick
                            if cell.get('onclick'):
                                print(f"     onclick: {cell.get('onclick')}")
                            
                            # Check for links
                            links = cell.find_all('a')
                            for link in links:
                                print(f"     link href: {link.get('href')}")
                                print(f"     link text: {link.get_text(strip=True)}")
                        
                        # Check parent elements for onclick
                        parent = row.parent
                        if parent and parent.name == 'tbody':
                            parent = parent.parent
                        if parent and parent.name == 'table':
                            print("\n   Checking table for onclick handlers...")
                            # Check if table has any JavaScript handlers
    
    if not found:
        print("\n   '대한조선' not found in any table")
    
    # Look for JavaScript that might handle clicks
    print("\n4. Looking for JavaScript patterns...")
    scripts = soup.find_all('script')
    for script in scripts:
        if script.string and ('대한조선' in script.string or 'location.href' in script.string):
            print(f"\n   Found relevant script:")
            print(script.string[:500])


if __name__ == "__main__":
    debug_ipo_list() 