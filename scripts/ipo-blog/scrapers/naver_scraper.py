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
        
        # Find the IPO table
        table = soup.find('table', {'class': 'type_1'})
        if not table:
            logger.error("IPO table not found")
            return []
        
        # Get all rows except header
        rows = table.find_all('tr')
        
        for row in rows:
            # Skip empty rows or header rows
            if not row.find('td') or row.find('th'):
                continue
            
            cells = row.find_all('td')
            if len(cells) < 10:  # Make sure we have enough columns
                continue
            
            try:
                # Extract basic information
                company_cell = cells[0]
                company_link = company_cell.find('a')
                if not company_link:
                    continue
                
                # Extract company name and stock code
                company_name = company_link.text.strip()
                href = company_link.get('href', '')
                stock_code_match = re.search(r'code=(\d+)', href)
                stock_code = stock_code_match.group(1) if stock_code_match else None
                
                if not stock_code:
                    logger.warning(f"Failed to extract stock code for {company_name}")
                    continue
                
                # Extract other information
                ipo_info = {
                    'company_name': company_name,
                    'stock_code': stock_code,
                    'market_type': cells[1].text.strip(),  # 시장구분
                    'industry': cells[2].text.strip(),  # 업종
                    'underwriters': cells[3].text.strip(),  # 주간사
                    'offering_amount': self._parse_number(cells[4].text.strip()),  # 공모금액(억)
                    'competition_rate': self._parse_number(cells[5].text.strip()),  # 경쟁률
                    'desired_price': cells[6].text.strip(),  # 희망공모가
                    'subscription_date': cells[7].text.strip(),  # 공모청약일
                    'listing_date': cells[8].text.strip(),  # 상장일
                    'detail_url': f"{self.base_url}{href}" if href.startswith('/') else href
                }
                
                # Filter by target underwriters
                if self._is_target_underwriter(ipo_info['underwriters']):
                    logger.info(f"Found IPO: {company_name} ({stock_code}) - Underwriters: {ipo_info['underwriters']}")
                    ipo_list.append(ipo_info)
                else:
                    logger.debug(f"Skipping IPO: {company_name} - Underwriters: {ipo_info['underwriters']}")
                    
            except Exception as e:
                logger.error(f"Error parsing IPO row: {e}")
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