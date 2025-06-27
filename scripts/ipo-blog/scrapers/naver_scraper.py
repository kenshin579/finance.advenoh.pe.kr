"""
Naver Finance IPO scraper
"""
from typing import List, Dict, Optional, Any
import re
import logging
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class NaverScraper(BaseScraper):
    """Scraper for Naver Finance IPO information"""
    
    # Target underwriters to filter
    TARGET_UNDERWRITERS = [
        '미래에셋',
        '한국투자',
        '신한투자',
        'KB',
        'NH',
        '삼성'
    ]
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://finance.naver.com"
        self.ipo_list_url = f"{self.base_url}/sise/ipo.naver"
    
    def _parse_number(self, text: str) -> Optional[float]:
        """Parse Korean number format to float"""
        if not text or text.strip() == '-':
            return None
        
        # Remove commas and convert
        try:
            # Remove any non-numeric characters except dots and minus
            cleaned = re.sub(r'[^\d.-]', '', text)
            return float(cleaned) if cleaned else None
        except ValueError:
            logger.warning(f"Failed to parse number: {text}")
            return None
    
    def _is_target_underwriter(self, underwriters: str) -> bool:
        """Check if any of the target underwriters are in the underwriter list"""
        if not underwriters:
            return False
        
        for target in self.TARGET_UNDERWRITERS:
            if target in underwriters:
                return True
        return False
    
    def get_ipo_list(self) -> List[Dict[str, Any]]:
        """
        Get IPO list from Naver Finance
        
        Returns:
            List of IPO information dictionaries
        """
        logger.info("Fetching IPO list from Naver Finance")
        
        soup = self.get_soup(self.ipo_list_url)
        if not soup:
            logger.error("Failed to fetch IPO list page")
            return []
        
        ipo_list = []
        
        # Find all IPO items (new div structure)
        ipo_items = soup.find_all('div', {'class': 'item_area'})
        
        if not ipo_items:
            logger.error("No IPO items found")
            return []
        
        logger.info(f"Found {len(ipo_items)} total IPO items")
        
        for item in ipo_items:
            try:
                # Extract company name and stock code
                name_elem = item.find('h4', {'class': 'item_name'})
                if not name_elem:
                    continue
                
                link_elem = name_elem.find('a')
                if not link_elem:
                    continue
                
                company_name = link_elem.text.strip()
                href = link_elem.get('href', '')
                
                # Extract stock code from div id or href
                stock_code = item.get('id')  # The div has stock code as id
                if not stock_code:
                    stock_code_match = re.search(r'/ipo/([A-Z0-9]+)', href)
                    stock_code = stock_code_match.group(1) if stock_code_match else None
                
                if not stock_code:
                    logger.warning(f"Failed to extract stock code for {company_name}")
                    continue
                
                # Extract market type
                market_elem = name_elem.find('span', {'class': 'type'})
                market_type = market_elem.text.strip() if market_elem else ''
                
                # Extract info from list
                info_list = item.find('ul', {'class': 'lst_info'})
                if not info_list:
                    continue
                
                ipo_info = {
                    'company_name': company_name,
                    'stock_code': stock_code,
                    'market_type': market_type
                }
                
                # Parse all info items
                for li in info_list.find_all('li'):
                    title_elem = li.find('em', {'class': 'tit'})
                    if not title_elem:
                        continue
                    
                    title = title_elem.text.strip()
                    
                    # Handle special cases for values
                    if title == '공모가':
                        # Extract price from span if exists
                        price_span = li.find('span', {'class': 'num'})
                        ipo_info['offering_price'] = price_span.text.strip() if price_span else li.text.replace(title, '').strip()
                    elif title == '업종':
                        # Get only direct text content, not from nested elements
                        value = ''.join([str(x) for x in li.contents if isinstance(x, str)])
                        ipo_info['industry'] = value.replace(title, '').strip()
                    elif title == '주관사':
                        # Get only direct text content
                        value = ''.join([str(x) for x in li.contents if isinstance(x, str)])
                        ipo_info['underwriters'] = value.replace(title, '').strip()
                    elif title == '진행상태':
                        # Extract only the direct text, excluding nested elements like buttons or tooltips
                        # Find all direct text nodes
                        texts = []
                        for content in li.contents:
                            if isinstance(content, str):
                                texts.append(content.strip())
                            elif hasattr(content, 'name') and content.name not in ['button', 'div', 'span']:
                                # Get text from non-button/div/span elements
                                if hasattr(content, 'string') and content.string:
                                    texts.append(content.string.strip())
                        
                        status_text = ' '.join(texts).replace(title, '').strip()
                        # Clean up any remaining whitespace
                        status_text = ' '.join(status_text.split())
                        ipo_info['status'] = status_text
                    elif title == '개인청약':
                        # Extract date from span if exists
                        date_span = li.find('span', {'class': 'num'})
                        ipo_info['subscription_date'] = date_span.text.strip() if date_span else li.text.replace(title, '').strip()
                    elif title == '상장일':
                        value = ''.join([str(x) for x in li.contents if isinstance(x, str)])
                        ipo_info['listing_date'] = value.replace(title, '').strip()
                
                # Set default values for missing fields
                ipo_info.setdefault('offering_amount', None)
                ipo_info.setdefault('competition_rate', None)
                ipo_info.setdefault('underwriters', '')
                
                # Filter by target underwriters
                if self._is_target_underwriter(ipo_info['underwriters']):
                    logger.info(f"Found IPO: {company_name} ({stock_code})")
                    logger.info(f"  - Market: {ipo_info.get('market_type', 'N/A')}")
                    logger.info(f"  - Industry: {ipo_info.get('industry', 'N/A')}")
                    logger.info(f"  - Underwriters: {ipo_info['underwriters']}")
                    logger.info(f"  - Status: {ipo_info.get('status', 'N/A')}")
                    logger.info(f"  - Offering Price: {ipo_info.get('offering_price', 'N/A')}")
                    logger.info(f"  - Subscription Date: {ipo_info.get('subscription_date', 'N/A')}")
                    logger.info(f"  - Listing Date: {ipo_info.get('listing_date', 'N/A')}")
                    ipo_list.append(ipo_info)
                else:
                    logger.debug(f"Skipping IPO: {company_name} - Underwriters: {ipo_info['underwriters']}")
                    
            except Exception as e:
                logger.error(f"Error parsing IPO item: {e}")
                continue
        
        logger.info(f"Found {len(ipo_list)} IPOs with target underwriters")
        return ipo_list
    
    def get_ipo_detail(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed IPO information for a specific stock
        
        Args:
            stock_code: Stock code to get details for
            
        Returns:
            Dictionary with detailed IPO information or None if failed
        """
        detail_url = f"{self.base_url}/item/main.naver?code={stock_code}"
        logger.info(f"Fetching IPO details for {stock_code}")
        
        soup = self.get_soup(detail_url)
        if not soup:
            logger.error(f"Failed to fetch detail page for {stock_code}")
            return None
        
        detail_info = {
            'stock_code': stock_code
        }
        
        try:
            # Extract company name from title
            title_elem = soup.find('div', {'class': 'wrap_company'})
            if title_elem:
                company_name_elem = title_elem.find('h2')
                if company_name_elem:
                    detail_info['company_name'] = company_name_elem.text.strip()
            
            # Extract market info
            market_elem = soup.find('img', {'class': 'img_logo'})
            if market_elem and market_elem.get('alt'):
                detail_info['market_type'] = market_elem['alt']
            
            # Extract company type and other basic info from summary
            summary_info = soup.find('div', {'class': 'section_summary'})
            if summary_info:
                # Try to find IPO related information
                ipo_table = summary_info.find('table')
                if ipo_table:
                    for row in ipo_table.find_all('tr'):
                        cells = row.find_all(['th', 'td'])
                        if len(cells) >= 2:
                            key = cells[0].text.strip()
                            value = cells[1].text.strip()
                            
                            if '업종' in key:
                                detail_info['industry'] = value
                            elif '대표' in key or '최대주주' in key:
                                detail_info['major_shareholder'] = value
                            elif '홈페이지' in key:
                                link = cells[1].find('a')
                                if link:
                                    detail_info['homepage'] = link.get('href', '')
            
            # Extract financial information if available
            finance_section = soup.find('div', {'class': 'section_finance'})
            if finance_section:
                finance_table = finance_section.find('table')
                if finance_table:
                    # Extract financial data
                    headers = [th.text.strip() for th in finance_table.find_all('th')]
                    rows = finance_table.find_all('tr')[1:]  # Skip header row
                    
                    for row in rows:
                        cells = row.find_all('td')
                        if cells and cells[0].text.strip() == '매출액':
                            detail_info['revenue'] = [self._parse_number(cell.text) for cell in cells[1:]]
                        elif cells and cells[0].text.strip() == '영업이익':
                            detail_info['operating_profit'] = [self._parse_number(cell.text) for cell in cells[1:]]
                        elif cells and cells[0].text.strip() == '당기순이익':
                            detail_info['net_profit'] = [self._parse_number(cell.text) for cell in cells[1:]]
            
        except Exception as e:
            logger.error(f"Error extracting detail information for {stock_code}: {e}")
        
        return detail_info 