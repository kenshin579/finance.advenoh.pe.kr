#!/usr/bin/env python3
"""
IPO Blog Automation System - Main Entry Point
"""
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import os

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from scrapers.naver_scraper import NaverScraper
from scrapers.comm38_scraper import Comm38Scraper

# Initial logging configuration (console only)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class IPOBlogAutomation:
    """Main class for IPO blog automation system"""
    
    def __init__(self):
        """IPO 블로그 자동화 시스템 초기화"""
        self.base_dir = Path(__file__).parent
        self.output_dir = self.base_dir / "output"
        self.logs_dir = self.base_dir / "logs"
        
        # 디렉토리 생성
        self.output_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        
        # 로깅 설정
        self._setup_logging()
        
        # 스크레이퍼 초기화
        self.naver_scraper = NaverScraper()
        self.comm38_scraper = Comm38Scraper()
        
        logger.info("IPO Blog Automation System initialized")
    
    def _setup_logging(self):
        """로깅 설정 - 날짜와 시간을 포함한 로그 파일 생성"""
        # 날짜와 시간을 포함한 로그 파일명
        log_filename = f"ipo_blog_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        log_filepath = self.logs_dir / log_filename
        
        # 기존 로거의 핸들러 가져오기
        root_logger = logging.getLogger()
        
        # 파일 핸들러 추가
        file_handler = logging.FileHandler(log_filepath, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        
        # 루트 로거에 파일 핸들러 추가
        root_logger.addHandler(file_handler)
        
        logger.info(f"Logging to file: {log_filepath}")
    
    def collect_ipo_data(self) -> List[Dict[str, Any]]:
        """
        Collect IPO data from various sources
        
        Returns:
            List of IPO information
        """
        logger.info("Starting IPO data collection...")
        
        # 1. Get IPO list from Naver
        ipo_list = self.naver_scraper.get_ipo_list()
        logger.info(f"Found {len(ipo_list)} IPOs from target underwriters")
        
        # 2. Get detailed information for each IPO
        enriched_ipos = []
        for idx, ipo in enumerate(ipo_list, 1):
            logger.info(f"\nProcessing {idx}/{len(ipo_list)}: {ipo['company_name']} ({ipo['stock_code']})")
            logger.info(f"  - Market: {ipo.get('market_type', 'N/A')}")
            logger.info(f"  - Underwriters: {ipo.get('underwriters', 'N/A')}")
            logger.info(f"  - Status: {ipo.get('status', 'N/A')}")
            
            # Get detailed info from Naver
            detail = self.naver_scraper.get_ipo_detail(ipo['stock_code'])
            
            # Merge basic and detailed info
            if detail:
                ipo.update(detail)
                logger.info(f"  ✓ Collected detailed information from Naver")
                if 'industry' in detail:
                    logger.info(f"    - Industry: {detail['industry']}")
                if 'homepage' in detail:
                    logger.info(f"    - Homepage: {detail['homepage']}")
            else:
                logger.warning(f"  ⚠ Failed to get detailed information from Naver")
            
            # Get detailed info from 38 Communications
            logger.info(f"  → Searching on 38 Communications...")
            comm38_detail = self.comm38_scraper.get_ipo_detail(ipo['company_name'])
            
            if comm38_detail:
                # Merge data, prioritizing comm38 for financial data
                for key, value in comm38_detail.items():
                    if key == 'financial_data' or (key not in ipo and value):
                        ipo[key] = value
                logger.info(f"  ✓ Collected detailed information from 38 Communications")
                if 'financial_data' in comm38_detail:
                    logger.info(f"    - Financial data collected")
                if 'offering_amount' in comm38_detail:
                    logger.info(f"    - Offering amount: {comm38_detail['offering_amount']}")
                if 'institutional_competition_rate' in comm38_detail:
                    logger.info(f"    - Institutional competition rate: {comm38_detail['institutional_competition_rate']}")
            else:
                logger.warning(f"  ⚠ Failed to get information from 38 Communications")
            
            # TODO: Add news scraper when implemented
            
            enriched_ipos.append(ipo)
        
        return enriched_ipos
    
    def save_ipo_data(self, ipo_list: List[Dict[str, Any]]):
        """
        Save IPO data to JSON file
        
        Args:
            ipo_list: List of IPO information
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save all IPO data to a single file with timestamp
        data_file = self.output_dir / f'ipo_data_{timestamp}.json'
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(ipo_list, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved IPO data to {data_file}")
        logger.info(f"Total {len(ipo_list)} IPOs saved")
    
    def generate_summary_report(self, ipo_list: List[Dict[str, Any]]):
        """
        Generate a summary report of collected IPOs
        
        Args:
            ipo_list: List of IPO information
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        report_file = self.output_dir / f'summary_report_{datetime.now().strftime("%Y%m%d")}.md'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"# IPO Summary Report\n\n")
            f.write(f"Generated: {timestamp}\n\n")
            f.write(f"## Overview\n\n")
            f.write(f"Total IPOs found: {len(ipo_list)}\n\n")
            
            # Calculate statistics
            market_stats = {}
            status_stats = {}
            underwriter_stats = {}
            
            for ipo in ipo_list:
                # Market statistics
                market = ipo.get('market_type', 'Unknown')
                market_stats[market] = market_stats.get(market, 0) + 1
                
                # Status statistics
                status = ipo.get('status', 'Unknown')
                status_stats[status] = status_stats.get(status, 0) + 1
                
                # Underwriter statistics
                underwriter = ipo.get('underwriters', 'Unknown')
                if underwriter not in underwriter_stats:
                    underwriter_stats[underwriter] = []
                underwriter_stats[underwriter].append(ipo)
            
            # Write statistics
            f.write("### By Market\n\n")
            for market, count in market_stats.items():
                f.write(f"- **{market}**: {count} IPOs\n")
            
            f.write("\n### By Status\n\n")
            for status, count in status_stats.items():
                f.write(f"- **{status}**: {count} IPOs\n")
            
            f.write("\n### By Underwriter\n\n")
            for underwriter, ipos in underwriter_stats.items():
                f.write(f"- **{underwriter}**: {len(ipos)} IPOs\n")
            
            f.write("\n## IPO List\n\n")
            f.write("| Company | Stock Code | Market | Industry | Underwriters | Status | Price | Subscription Date | Listing Date |\n")
            f.write("|---------|------------|--------|----------|--------------|--------|-------|-------------------|-------------|\n")
            
            for ipo in ipo_list:
                f.write(f"| {ipo.get('company_name', 'N/A')} ")
                f.write(f"| {ipo.get('stock_code', 'N/A')} ")
                f.write(f"| {ipo.get('market_type', 'N/A')} ")
                f.write(f"| {ipo.get('industry', 'N/A')[:30] + '...' if len(ipo.get('industry', '')) > 30 else ipo.get('industry', 'N/A')} ")
                f.write(f"| {ipo.get('underwriters', 'N/A')} ")
                f.write(f"| {ipo.get('status', 'N/A')} ")
                f.write(f"| {ipo.get('offering_price', 'N/A')} ")
                f.write(f"| {ipo.get('subscription_date', 'N/A')} ")
                f.write(f"| {ipo.get('listing_date', 'N/A')} |\n")
        
        logger.info(f"Generated summary report: {report_file}")
    
    def run(self):
        """Main execution flow"""
        try:
            logger.info("=" * 50)
            logger.info("Starting IPO Blog Automation System")
            logger.info("=" * 50)
            
            # Step 1: Collect IPO data
            ipo_list = self.collect_ipo_data()
            
            if not ipo_list:
                logger.warning("No IPOs found. Exiting.")
                return
            
            # Step 2: Save collected data
            self.save_ipo_data(ipo_list)
            
            # Step 3: Generate summary report
            self.generate_summary_report(ipo_list)
            
            # TODO: Add data validation when processor module is ready
            # TODO: Add content generation when generator module is ready
            # TODO: Add chart generation when implemented
            # TODO: Add database storage when DB module is ready
            
            logger.info("=" * 50)
            logger.info(f"IPO Blog Automation completed successfully!")
            logger.info(f"Processed {len(ipo_list)} IPOs")
            logger.info(f"Check output directory for results: {self.output_dir}")
            logger.info("=" * 50)
            
        except KeyboardInterrupt:
            logger.info("\nProcess interrupted by user")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)
            sys.exit(1)


def main():
    """Main entry point"""
    automation = IPOBlogAutomation()
    automation.run()


if __name__ == "__main__":
    main()
