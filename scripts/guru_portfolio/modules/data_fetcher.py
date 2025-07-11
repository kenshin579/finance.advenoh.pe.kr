"""Data fetcher module for extracting 13F filing data from 13f.info"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from typing import Dict, List, Optional
import time
from urllib.parse import quote
import json


class DataFetcher:
    """Fetches 13F filing data from 13f.info website"""
    
    BASE_URL = "https://13f.info"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_portfolio_data(self, company: str, quarter: str) -> pd.DataFrame:
        """
        Fetch portfolio data for a specific company and quarter
        
        Args:
            company: Company name (e.g., "Berkshire Hathaway Inc")
            quarter: Quarter in format "Q1 2025"
            
        Returns:
            DataFrame with portfolio holdings data
        """
        # First, search for the company to get the correct URL
        search_url = f"{self.BASE_URL}/search"
        search_params = {'q': company}
        
        try:
            # Search for the company
            response = self.session.get(search_url, params=search_params)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Find the company link
            company_link = self._find_company_link(soup, company)
            if not company_link:
                raise ValueError(f"Company '{company}' not found")
            
            # Get the company's filings page
            company_url = f"{self.BASE_URL}{company_link}"
            response = self.session.get(company_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Find the specific quarter filing
            filing_link = self._find_quarter_link(soup, quarter)
            if not filing_link:
                raise ValueError(f"Quarter '{quarter}' not found for {company}")
            
            # Get the filing data
            filing_url = f"{self.BASE_URL}{filing_link}"
            response = self.session.get(filing_url)
            response.raise_for_status()
            
            # Parse the holdings data
            holdings_df = self._parse_holdings(response.text)
            
            # Add metadata
            holdings_df['company'] = company
            holdings_df['quarter'] = quarter
            
            return holdings_df
            
        except requests.RequestException as e:
            raise Exception(f"Error fetching data: {str(e)}")
    
    def _find_company_link(self, soup: BeautifulSoup, company: str) -> Optional[str]:
        """Find the link to the company's page from search results"""
        # Look for exact match first
        links = soup.find_all('a', href=re.compile(r'/manager/'))
        
        for link in links:
            if company.lower() in link.text.lower():
                return link['href']
        
        return None
    
    def _find_quarter_link(self, soup: BeautifulSoup, quarter: str) -> Optional[str]:
        """Find the link to a specific quarter filing"""
        # Look for table with filing data
        tables = soup.find_all('table')
        
        for table in tables:
            # Check if this is the filings table by looking at headers
            headers = table.find_all('th')
            if headers:
                header_text = [h.text.strip().lower() for h in headers]
                # Check if this looks like a filings table
                if any('quarter' in h for h in header_text):
                    # This is likely the filings table
                    rows = table.find_all('tr')[1:]  # Skip header row
                    
                    for row in rows:
                        cells = row.find_all('td')
                        if cells and len(cells) > 0:
                            # First cell usually contains the quarter
                            quarter_cell = cells[0].text.strip()
                            
                            # Check if this row matches our quarter
                            if quarter.upper() == quarter_cell.upper():
                                # Find the link in this row
                                link = row.find('a', href=True)
                                if link:
                                    return link['href']
        
        # Fallback: look for links with quarter text
        links = soup.find_all('a', href=re.compile(r'/13f/'))
        
        for link in links:
            if quarter.upper() in link.text.strip().upper():
                return link['href']
        
        return None
    
    def _parse_holdings(self, html: str) -> pd.DataFrame:
        """Parse the holdings table from the filing page"""
        # Extract filing ID from the HTML to construct API endpoint
        filing_id_match = re.search(r'/data/13f/(\d+)', html)
        if not filing_id_match:
            # Fallback: try to extract from URL in the page
            filing_id_match = re.search(r'000095012\d+', html)
            if not filing_id_match:
                raise ValueError("Could not find filing ID for data endpoint")
        
        filing_id = filing_id_match.group(1) if filing_id_match.group(0).startswith('/data') else filing_id_match.group(0)
        
        # Fetch data from JSON endpoint
        data_url = f"{self.BASE_URL}/data/13f/{filing_id}"
        
        # Add necessary headers for API request
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': self.session.headers.get('Referer', self.BASE_URL)
        }
        
        response = self.session.get(data_url, headers=headers)
        response.raise_for_status()
        
        try:
            json_data = response.json()
            holdings_data = json_data.get('data', [])
            
            if not holdings_data:
                raise ValueError("No holdings data found in API response")
            
            # Convert array data to DataFrame
            # Format: [symbol, name, class, cusip, value, percentage, shares, principal, option_type]
            columns = ['symbol', 'security_name', 'class', 'cusip', 'market_value', 
                      'portfolio_weight', 'shares', 'principal', 'option_type']
            
            df = pd.DataFrame(holdings_data, columns=columns[:len(holdings_data[0])] if holdings_data else columns)
            
            # Convert numeric columns
            numeric_columns = ['market_value', 'portfolio_weight', 'shares']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Market value is in thousands, so multiply by 1000
            if 'market_value' in df.columns:
                df['market_value'] = df['market_value'] * 1000
            
            return df
            
        except (json.JSONDecodeError, KeyError) as e:
            # Fallback to HTML parsing if JSON fails
            print(f"JSON parsing failed: {e}, falling back to HTML parsing")
            return self._parse_holdings_html(html)
    
    def _parse_holdings_html(self, html: str) -> pd.DataFrame:
        """Fallback HTML parsing method"""
        soup = BeautifulSoup(html, 'lxml')
        
        # Find the holdings table
        table = soup.find('table', {'class': re.compile('holdings|portfolio', re.I)})
        if not table:
            # Try alternative selectors
            table = soup.find('table')
        
        if not table:
            raise ValueError("Holdings table not found")
        
        # Extract headers
        headers = []
        header_row = table.find('thead')
        if header_row:
            headers = [th.text.strip() for th in header_row.find_all('th')]
        else:
            # Try to find headers in first row
            first_row = table.find('tr')
            if first_row:
                headers = [td.text.strip() for td in first_row.find_all(['th', 'td'])]
        
        # Extract data rows
        rows = []
        tbody = table.find('tbody') or table
        for tr in tbody.find_all('tr')[1:]:  # Skip header row if in tbody
            row_data = []
            for td in tr.find_all('td'):
                text = td.text.strip()
                # Clean up numeric values
                text = text.replace('$', '').replace(',', '').replace('%', '')
                row_data.append(text)
            
            if row_data:  # Skip empty rows
                rows.append(row_data)
        
        # Create DataFrame
        if not headers:
            # Default headers if none found
            headers = ['Security', 'Shares', 'Value', 'Weight', 'Change']
        
        # Ensure we have the right number of columns
        max_cols = max(len(row) for row in rows) if rows else len(headers)
        headers = headers[:max_cols]
        
        # Pad headers if necessary
        while len(headers) < max_cols:
            headers.append(f'Column{len(headers)+1}')
        
        df = pd.DataFrame(rows, columns=headers[:len(rows[0])] if rows else headers)
        
        # Standardize column names
        df = self._standardize_columns(df)
        
        return df
    
    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names and data types"""
        # If we already have standardized columns from JSON parsing, just ensure data types
        if 'security_name' in df.columns and 'symbol' in df.columns:
            # Already standardized from JSON
            return df
        
        # Common column name mappings for HTML parsing
        column_mapping = {
            'company': 'security_name',
            'name': 'security_name',
            'security': 'security_name',
            'issuer': 'security_name',
            'stock': 'security_name',
            'shares': 'shares',
            'quantity': 'shares',
            'value': 'market_value',
            'market value': 'market_value',
            'mkt val': 'market_value',
            'weight': 'portfolio_weight',
            'percent': 'portfolio_weight',
            '%': 'portfolio_weight',
            'change': 'change_percent',
            'chg': 'change_percent',
            'sym': 'symbol',
            'ticker': 'symbol'
        }
        
        # Rename columns
        df.columns = [column_mapping.get(col.lower(), col.lower()) for col in df.columns]
        
        # Convert numeric columns
        numeric_columns = ['shares', 'market_value', 'portfolio_weight', 'change_percent']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Ensure required columns exist
        required_columns = ['security_name', 'shares', 'market_value']
        for col in required_columns:
            if col not in df.columns:
                df[col] = None
        
        return df 