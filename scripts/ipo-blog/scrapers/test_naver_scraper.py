"""
Test script for Naver IPO scraper
"""
import pytest
import logging
from pathlib import Path
import sys

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scrapers.naver_scraper import NaverScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class TestNaverScraper:
    """Test cases for Naver IPO scraper"""
    
    @pytest.fixture
    def scraper(self):
        """Create a scraper instance for testing"""
        return NaverScraper()
    
    def test_scraper_configuration(self, scraper):
        """Test that scraper is properly configured"""
        assert hasattr(scraper, 'ipo_list_url'), "Scraper should have ipo_list_url attribute"
        assert scraper.ipo_list_url == "https://finance.naver.com/sise/ipo.naver", "IPO URL should be correct"
        assert len(scraper.TARGET_UNDERWRITERS) > 0, "Target underwriters list should not be empty"
        assert isinstance(scraper.TARGET_UNDERWRITERS, list), "TARGET_UNDERWRITERS should be a list"
    
    def test_html_fetch(self, scraper):
        """Test that we can fetch and parse the IPO page"""
        soup = scraper.get_soup(scraper.ipo_list_url)
        assert soup is not None, "Should be able to fetch the IPO page"
        
        # Check for expected elements
        items = soup.find_all('div', {'class': 'item_area'})
        assert len(items) > 0, "Should find at least one IPO item on the page"
    
    def test_ipo_list_structure(self, scraper):
        """Test that get_ipo_list returns properly structured data"""
        ipo_list = scraper.get_ipo_list()
        
        # Basic assertions
        assert isinstance(ipo_list, list), "get_ipo_list should return a list"
        
        # If we have IPOs, validate their structure
        if ipo_list:
            first_ipo = ipo_list[0]
            
            # Check required fields
            required_fields = ['company_name', 'stock_code', 'market_type', 'underwriters']
            for field in required_fields:
                assert field in first_ipo, f"IPO data should contain '{field}' field"
                assert first_ipo[field], f"'{field}' should not be empty"
            
            # Validate data types
            assert isinstance(first_ipo['company_name'], str), "company_name should be string"
            assert isinstance(first_ipo['stock_code'], str), "stock_code should be string"
            assert len(first_ipo['stock_code']) > 0, "stock_code should not be empty"
    
    def test_market_type_validation(self, scraper):
        """Test that market types are valid"""
        ipo_list = scraper.get_ipo_list()
        
        if ipo_list:
            valid_markets = ['코스피', '코스닥', '코넥스']
            for ipo in ipo_list:
                assert ipo['market_type'] in valid_markets, \
                    f"Invalid market type: {ipo['market_type']} for {ipo['company_name']}"
    
    def test_underwriter_filtering(self, scraper):
        """Test that all returned IPOs have target underwriters"""
        ipo_list = scraper.get_ipo_list()
        
        for ipo in ipo_list:
            assert any(target in ipo['underwriters'] for target in scraper.TARGET_UNDERWRITERS), \
                f"IPO {ipo['company_name']} should have at least one target underwriter, but has: {ipo['underwriters']}"
    
    def test_parse_number_method(self, scraper):
        """Test the _parse_number helper method"""
        # Test valid numbers
        assert scraper._parse_number('1,234.56') == 1234.56
        assert scraper._parse_number('1234') == 1234.0
        assert scraper._parse_number('-123.45') == -123.45
        
        # Test invalid/empty values
        assert scraper._parse_number('-') is None
        assert scraper._parse_number('') is None
        assert scraper._parse_number(None) is None
        assert scraper._parse_number('abc') is None
    
    def test_is_target_underwriter_method(self, scraper):
        """Test the _is_target_underwriter helper method"""
        # Test positive cases
        assert scraper._is_target_underwriter('미래에셋증권') is True
        assert scraper._is_target_underwriter('한국투자증권, 미래에셋증권') is True
        assert scraper._is_target_underwriter('KB증권') is True
        
        # Test negative cases
        assert scraper._is_target_underwriter('하나증권') is False
        assert scraper._is_target_underwriter('') is False
        assert scraper._is_target_underwriter(None) is False
    
    @pytest.mark.slow
    def test_ipo_detail_fetch(self, scraper):
        """Test fetching detailed IPO information (slow test)"""
        ipo_list = scraper.get_ipo_list()
        
        if ipo_list:
            first_ipo = ipo_list[0]
            detail = scraper.get_ipo_detail(first_ipo['stock_code'])
            
            if detail:
                assert isinstance(detail, dict), "get_ipo_detail should return a dictionary"
                assert 'stock_code' in detail, "Detail should contain stock_code"
                assert detail['stock_code'] == first_ipo['stock_code'], "Stock code should match" 