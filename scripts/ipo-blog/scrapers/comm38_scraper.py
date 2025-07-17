"""
38 Communications IPO detail scraper
"""
from typing import Dict, Optional, Any, List
import re
import logging
from datetime import datetime
from .base_scraper import BaseScraper
from urllib.parse import urljoin, quote
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class Comm38Scraper(BaseScraper):
    """Scraper for 38 Communications IPO detailed information"""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.38.co.kr"
        self.search_url = f"{self.base_url}/html/fund/index.htm"
    
    def search_company(self, company_name: str) -> Optional[str]:
        """
        Search for a company and return its detail page URL
        
        Args:
            company_name: Company name to search for
            
        Returns:
            Company detail page URL or None if not found
        """
        logger.info(f"Searching for company: {company_name}")
        
        # Search using POST request
        search_url = f"{self.base_url}/html/fund/index.htm"
        
        try:
            # Prepare form data for search
            form_data = {
                'p': 's',
                'o': 'r',
                'string': company_name
            }
            
            # Make POST request
            response = self.session.post(search_url, data=form_data, timeout=10, verify=False)
            response.encoding = 'euc-kr'  # 38 Communications uses EUC-KR encoding
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all tables with IPO data
            tables = soup.find_all('table')
            logger.debug(f"Found {len(tables)} tables on search result page")
            
            # Look for the company in all links on the page
            all_links = soup.find_all('a')
            logger.debug(f"Found {len(all_links)} links on search result page")
            
            for link in all_links:
                if link.get('href'):
                    link_text = link.get_text(strip=True)
                    # Check if this link contains our company name
                    if company_name in link_text:
                        href = link['href']
                        logger.debug(f"Found potential link: {link_text} -> {href}")
                        
                        # Check if this is a fund detail page link (contains o=v parameter and correct path)
                        if 'o=v' in href and 'no=' in href:
                            # Build full URL
                            if href.startswith('./'):
                                # Remove ./ and append to current directory
                                href = href[2:]  # Remove ./
                                detail_url = search_url.rsplit('/', 1)[0] + '/' + href
                            elif href.startswith('/'):
                                detail_url = self.base_url + href
                            elif href.startswith('http'):
                                detail_url = href
                            else:
                                # Relative to current directory
                                detail_url = search_url.rsplit('/', 1)[0] + '/' + href
                            
                            # Only accept URLs with /html/fund/ pattern
                            if '/html/fund/' in detail_url:
                                logger.info(f"Found company detail URL: {detail_url}")
                                return detail_url
                            else:
                                logger.debug(f"Skipping non-fund URL: {detail_url}")
            
            logger.warning(f"Company '{company_name}' not found in search results")
            
        except Exception as e:
            logger.error(f"Error searching for company: {e}")
        
        return None
    
    def _parse_table_data(self, table, key_col_idx: int = 0, value_col_idx: int = 1) -> Dict[str, str]:
        """
        Parse table data into dictionary
        
        Args:
            table: BeautifulSoup table element
            key_col_idx: Index of the key column
            value_col_idx: Index of the value column
            
        Returns:
            Dictionary of parsed data
        """
        data = {}
        if not table:
            return data
        
        for row in table.find_all('tr'):
            cells = row.find_all(['td', 'th'])
            if len(cells) > max(key_col_idx, value_col_idx):
                key = cells[key_col_idx].get_text(strip=True)
                value = cells[value_col_idx].get_text(strip=True)
                if key and value:
                    data[key] = value
        
        return data
    
    def _parse_financial_table(self, table) -> Dict[str, List[float]]:
        """
        Parse financial data table
        
        Args:
            table: BeautifulSoup table element
            
        Returns:
            Dictionary with financial metrics as keys and list of values
        """
        financial_data = {}
        if not table:
            return financial_data
        
        # Get headers (years)
        headers = []
        header_row = table.find('tr')
        if header_row:
            for th in header_row.find_all(['th', 'td'])[1:]:  # Skip first column
                headers.append(th.get_text(strip=True))
        
        # Get data rows
        for row in table.find_all('tr')[1:]:  # Skip header row
            cells = row.find_all(['td', 'th'])
            if len(cells) > 1:
                metric_name = cells[0].get_text(strip=True)
                values = []
                
                for cell in cells[1:]:
                    value_text = cell.get_text(strip=True)
                    # Parse number, handling Korean number formats
                    value = self._parse_korean_number(value_text)
                    values.append(value)
                
                if metric_name and values:
                    financial_data[metric_name] = values
        
        return financial_data
    
    def _parse_korean_number(self, text: str) -> Optional[float]:
        """
        Parse Korean number format to float
        
        Args:
            text: Number text in Korean format (e.g., "1,234억원", "12.34%")
            
        Returns:
            Parsed float value or None
        """
        if not text or text.strip() in ['-', 'N/A', '']:
            return None
        
        try:
            # Remove commas
            text = text.replace(',', '')
            
            # Handle complex Korean units (e.g., "1조 2,345억")
            total = 0
            
            # Process 조 (trillion)
            if '조' in text:
                parts = text.split('조')
                if parts[0].strip():
                    jo_match = re.search(r'[-+]?\d*\.?\d+', parts[0])
                    if jo_match:
                        total += float(jo_match.group()) * 1000000000000
                text = parts[1] if len(parts) > 1 else ''
            
            # Process 억 (hundred million)
            if '억' in text:
                parts = text.split('억')
                if parts[0].strip():
                    eok_match = re.search(r'[-+]?\d*\.?\d+', parts[0])
                    if eok_match:
                        total += float(eok_match.group()) * 100000000
                text = parts[1] if len(parts) > 1 else ''
            
            # Process 만 (ten thousand)
            if '만' in text:
                parts = text.split('만')
                if parts[0].strip():
                    man_match = re.search(r'[-+]?\d*\.?\d+', parts[0])
                    if man_match:
                        total += float(man_match.group()) * 10000
                text = parts[1] if len(parts) > 1 else ''
            
            # Remove currency symbols and percentage signs
            text = re.sub(r'[원%]', '', text)
            
            # If there's still a number left (no units), add it
            if total == 0:
                number_match = re.search(r'[-+]?\d*\.?\d+', text)
                if number_match:
                    total = float(number_match.group())
            else:
                # Add any remaining number
                number_match = re.search(r'[-+]?\d*\.?\d+', text)
                if number_match:
                    total += float(number_match.group())
            
            return total if total != 0 else None
            
        except Exception as e:
            logger.warning(f"Failed to parse number '{text}': {e}")
        
        return None
    
    def get_ipo_detail(self, company_name: str, detail_url: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get detailed IPO information for a company
        
        Args:
            company_name: Company name
            detail_url: Direct URL to company detail page (optional)
            
        Returns:
            Dictionary with IPO details or None if failed
        """
        # If no detail URL provided, search for the company
        if not detail_url:
            detail_url = self.search_company(company_name)
            if not detail_url:
                logger.warning(f"Could not find detail page for {company_name}")
                return None
        
        logger.info(f"Fetching IPO details from: {detail_url}")
        
        soup = self.get_soup(detail_url)
        if not soup:
            logger.error(f"Failed to fetch detail page: {detail_url}")
            return None
        
        ipo_detail = {
            'company_name': company_name,
            'source': '38communications',
            'url': detail_url
        }
        
        try:
            # Extract company overview
            overview_section = soup.find('div', {'class': 'company_info'})
            if not overview_section:
                # Try alternative selectors
                overview_section = soup.find('div', {'class': 'sub_cont'})
            
            if overview_section:
                # Extract basic info table
                info_table = overview_section.find('table')
                if info_table:
                    basic_info = self._parse_table_data(info_table)
                    
                    # Map to standard fields
                    ipo_detail['industry'] = basic_info.get('업종', '')
                    ipo_detail['major_products'] = basic_info.get('주요제품', '')
                    ipo_detail['major_shareholder'] = basic_info.get('최대주주', '')
                    ipo_detail['capital'] = self._parse_korean_number(basic_info.get('자본금', ''))
                    ipo_detail['employees'] = self._parse_korean_number(basic_info.get('종업원수', ''))
            
            # Extract financial data
            financial_section = soup.find('div', {'class': 'financial'})
            if not financial_section:
                # Look for financial tables by content
                for table in soup.find_all('table'):
                    # Check if this is a financial table
                    first_cell = table.find(['td', 'th'])
                    if first_cell and any(keyword in first_cell.get_text() for keyword in ['매출액', '영업이익', '당기순이익']):
                        financial_section = table.parent
                        break
            
            if financial_section:
                financial_table = financial_section.find('table')
                if financial_table:
                    financial_data = self._parse_financial_table(financial_table)
                    ipo_detail['financial_data'] = financial_data
            
            # Extract offering information
            offering_section = soup.find('div', {'class': 'offering'})
            if not offering_section:
                # Look for offering info by keywords
                for section in soup.find_all(['div', 'table']):
                    if any(keyword in section.get_text() for keyword in ['공모가', '청약일', '상장일']):
                        offering_section = section
                        break
            
            if offering_section:
                offering_table = offering_section if offering_section.name == 'table' else offering_section.find('table')
                if offering_table:
                    offering_info = self._parse_table_data(offering_table)
                    
                    # Extract key offering details
                    ipo_detail['offering_price_range'] = offering_info.get('희망공모가', '')
                    ipo_detail['final_offering_price'] = self._parse_korean_number(offering_info.get('확정공모가', ''))
                    ipo_detail['offering_amount'] = self._parse_korean_number(offering_info.get('공모금액', ''))
                    ipo_detail['offering_shares'] = self._parse_korean_number(offering_info.get('공모주식수', ''))
            
            # Extract schedule information
            schedule_section = soup.find('div', {'class': 'schedule'})
            if not schedule_section:
                # Look for schedule table
                for table in soup.find_all('table'):
                    if any(keyword in table.get_text() for keyword in ['수요예측', '청약일', '납입일', '상장일']):
                        schedule_section = table
                        break
            
            if schedule_section:
                schedule_table = schedule_section if schedule_section.name == 'table' else schedule_section.find('table')
                if schedule_table:
                    schedule_info = self._parse_table_data(schedule_table)
                    
                    # Parse dates
                    ipo_detail['demand_forecast_date'] = self._parse_date(schedule_info.get('수요예측일', ''))
                    ipo_detail['subscription_date'] = self._parse_date(schedule_info.get('공모청약일', ''))
                    ipo_detail['payment_date'] = self._parse_date(schedule_info.get('납입일', ''))
                    ipo_detail['refund_date'] = self._parse_date(schedule_info.get('환불일', ''))
                    ipo_detail['listing_date'] = self._parse_date(schedule_info.get('상장일', ''))
            
            # Extract competition rates
            competition_section = soup.find('div', {'class': 'competition'})
            if not competition_section:
                # Look for competition info
                for section in soup.find_all(['div', 'table']):
                    if any(keyword in section.get_text() for keyword in ['경쟁률', '기관경쟁률']):
                        competition_section = section
                        break
            
            if competition_section:
                competition_table = competition_section if competition_section.name == 'table' else competition_section.find('table')
                if competition_table:
                    competition_info = self._parse_table_data(competition_table)
                    
                    ipo_detail['total_competition_rate'] = self._parse_korean_number(competition_info.get('통합경쟁률', ''))
                    ipo_detail['institutional_competition_rate'] = self._parse_korean_number(competition_info.get('기관경쟁률', ''))
            
        except Exception as e:
            logger.error(f"Error parsing IPO details: {e}")
        
        return ipo_detail
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """
        Parse date string to standard format
        
        Args:
            date_str: Date string in various formats
            
        Returns:
            Date in YYYY-MM-DD format or None
        """
        if not date_str or date_str.strip() in ['-', 'N/A', '']:
            return None
        
        try:
            # Remove extra whitespace
            date_str = date_str.strip()
            
            # Try different date formats
            date_formats = [
                '%Y.%m.%d',
                '%Y-%m-%d',
                '%Y/%m/%d',
                '%Y년 %m월 %d일',
                '%Y년%m월%d일',
                '%m.%d',
                '%m/%d',
                '%m월 %d일'
            ]
            
            for fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(date_str, fmt)
                    # If year is missing, use current year
                    if parsed_date.year == 1900:
                        parsed_date = parsed_date.replace(year=datetime.now().year)
                    return parsed_date.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            
            # If date contains ranges (e.g., "12.20~12.21"), take the first date
            if '~' in date_str or '-' in date_str:
                date_parts = re.split(r'[~\-]', date_str)
                if date_parts:
                    return self._parse_date(date_parts[0])
            
        except Exception as e:
            logger.warning(f"Failed to parse date '{date_str}': {e}")
        
        return date_str  # Return original if parsing fails 