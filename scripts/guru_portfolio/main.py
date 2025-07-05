#!/usr/bin/env python3
"""
13F Portfolio Visualization Tool

This script fetches portfolio data from 13f.info and creates interactive visualizations
"""

import argparse
import sys
import os
from datetime import datetime

from modules import DataFetcher, DataProcessor, Visualizer, ReportGenerator


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Fetch and visualize 13F portfolio data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py "Berkshire Hathaway Inc" "Q3 2024"
  python main.py "Bridgewater Associates" "Q2 2024" --output-dir results/
  python main.py "Scion Asset Management" "Q4 2023" --top-n 30
        """
    )
    
    parser.add_argument('company', 
                       help='Company name (e.g., "Berkshire Hathaway Inc")')
    parser.add_argument('quarter', 
                       help='Quarter in format "Q1 2025"')
    parser.add_argument('--output-dir', '-o', 
                       default='output',
                       help='Output directory for results (default: output)')
    parser.add_argument('--top-n', '-n', 
                       type=int, 
                       default=20,
                       help='Number of top holdings to show in bar chart (default: 20)')
    parser.add_argument('--no-visualizations', 
                       action='store_true',
                       help='Skip creating visualizations')
    parser.add_argument('--save-html', 
                       action='store_true',
                       help='Also save visualizations as interactive HTML files')
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    print(f"\n{'='*60}")
    print(f"13F Portfolio Analysis Tool")
    print(f"{'='*60}")
    print(f"Company: {args.company}")
    print(f"Quarter: {args.quarter}")
    print(f"Output Directory: {args.output_dir}")
    print(f"{'='*60}\n")
    
    try:
        # Step 1: Fetch data
        print("📊 Fetching portfolio data from 13f.info...")
        fetcher = DataFetcher()
        raw_data = fetcher.fetch_portfolio_data(args.company, args.quarter)
        print(f"✅ Successfully fetched {len(raw_data)} holdings")
        
        # Step 2: Process data
        print("\n🔄 Processing portfolio data...")
        processor = DataProcessor()
        processed_data = processor.process_portfolio_data(raw_data)
        metrics = processor.calculate_portfolio_metrics(processed_data)
        treemap_data = processor.prepare_treemap_data(processed_data)
        
        print(f"✅ Data processed successfully")
        print(f"   - Total value: ${metrics['total_value']:,.0f}")
        print(f"   - Total positions: {metrics['total_positions']}")
        print(f"   - Top 10 concentration: {metrics['top_10_concentration']:.1f}%")
        
        # Step 3: Create visualizations
        if not args.no_visualizations:
            print("\n📈 Creating visualizations...")
            visualizer = Visualizer()
            
            # Create treemap
            print("   - Creating portfolio treemap...")
            treemap_fig = visualizer.create_treemap(
                treemap_data, 
                f"{args.company} Portfolio - {args.quarter}"
            )
            
            # Create sector pie chart
            print("   - Creating sector allocation chart...")
            sector_fig = visualizer.create_sector_pie_chart(processed_data)
            
            # Create concentration chart
            print("   - Creating top holdings chart...")
            concentration_fig = visualizer.create_concentration_chart(
                processed_data, 
                top_n=args.top_n
            )
            
            # Save visualizations
            figures = {
                'portfolio_treemap': treemap_fig,
                'sector_allocation': sector_fig,
                'top_holdings': concentration_fig
            }
            
            visualizer.save_visualizations(figures, args.output_dir, save_html=args.save_html)
            print("✅ Visualizations saved")
        
        # Step 4: Generate report
        print("\n📝 Generating analysis report...")
        reporter = ReportGenerator()
        report_path = os.path.join(args.output_dir, 'portfolio_analysis.md')
        reporter.generate_report(
            args.company,
            args.quarter,
            processed_data,
            metrics,
            report_path
        )
        print(f"✅ Report saved to: {report_path}")
        
        # Success summary
        print(f"\n{'='*60}")
        print("✨ Analysis completed successfully!")
        print(f"{'='*60}")
        print(f"\nResults saved in: {os.path.abspath(args.output_dir)}/")
        print("\nGenerated files:")
        print("  📄 portfolio_analysis.md - Detailed analysis report")
        if not args.no_visualizations:
            print("  🖼️  portfolio_treemap.png - Portfolio treemap visualization")
            print("  🖼️  sector_allocation.png - Sector breakdown pie chart")
            print("  🖼️  top_holdings.png - Top holdings bar chart")
            if args.save_html:
                print("  🌐 portfolio_treemap.html - Interactive treemap")
                print("  🌐 sector_allocation.html - Interactive sector chart")
                print("  🌐 top_holdings.html - Interactive holdings chart")
        
    except ValueError as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nPlease check that:")
        print("  1. The company name matches exactly (try searching on 13f.info)")
        print("  2. The quarter has been filed (13F reports are filed 45 days after quarter end)")
        
        # Generate error report
        reporter = ReportGenerator()
        error_report = reporter.generate_summary_report(args.company, args.quarter, str(e))
        error_path = os.path.join(args.output_dir, 'error_report.md')
        with open(error_path, 'w') as f:
            f.write(error_report)
        print(f"\n📄 Error report saved to: {error_path}")
        
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 