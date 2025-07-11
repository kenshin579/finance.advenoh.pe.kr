#!/usr/bin/env python3
"""
13F Portfolio Visualization Tool

This script fetches portfolio data from 13f.info and creates interactive visualizations
"""

import argparse
import sys
import os
from datetime import datetime

from modules import DataFetcher, DataProcessor, Visualizer, ReportGenerator, PerformanceTracker


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
  python main.py "ARK Invest" "Q3 2024" --compare-sp500 --lookback-quarters 4
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
    parser.add_argument('--compare-sp500', 
                       action='store_true',
                       help='Compare portfolio performance with S&P 500')
    parser.add_argument('--lookback-quarters', 
                       type=int, 
                       default=4,
                       help='Number of quarters to look back for performance comparison (default: 4)')
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    print(f"\n{'='*60}")
    print(f"13F Portfolio Analysis Tool")
    print(f"{'='*60}")
    print(f"Company: {args.company}")
    print(f"Quarter: {args.quarter}")
    print(f"Output Directory: {args.output_dir}")
    if args.compare_sp500:
        print(f"Performance Comparison: Enabled (looking back {args.lookback_quarters} quarters)")
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
            figures = {}
            
            # Create treemap
            print("   - Creating portfolio treemap...")
            treemap_fig = visualizer.create_treemap(
                treemap_data, 
                f"{args.company} Portfolio - {args.quarter}"
            )
            figures['portfolio_treemap'] = treemap_fig
            
            # Create sector pie chart
            print("   - Creating sector allocation chart...")
            sector_fig = visualizer.create_sector_pie_chart(processed_data)
            figures['sector_allocation'] = sector_fig
            
            # Create concentration chart
            print("   - Creating top holdings chart...")
            concentration_fig = visualizer.create_concentration_chart(
                processed_data, 
                top_n=args.top_n
            )
            figures['top_holdings'] = concentration_fig
            
            # Step 3.5: Create performance comparison if requested
            if args.compare_sp500:
                print("\n📊 Creating performance comparison with S&P 500...")
                performance_tracker = PerformanceTracker()
                
                # Simulate historical portfolio data (in real scenario, you'd fetch historical 13F data)
                print("   - Simulating historical portfolio values...")
                holdings_history = performance_tracker.simulate_portfolio_from_holdings(
                    processed_data, 
                    lookback_quarters=args.lookback_quarters
                )
                
                # Calculate portfolio performance
                holdings_dfs = [h[1] for h in holdings_history]
                dates = [h[0] for h in holdings_history]
                portfolio_df = performance_tracker.calculate_portfolio_performance(holdings_dfs, dates)
                
                # Compare with S&P 500
                print("   - Fetching S&P 500 data...")
                start_date = dates[0]
                end_date = dates[-1]
                comparison_df = performance_tracker.compare_performance(
                    portfolio_df, 
                    start_date, 
                    end_date
                )
                
                # Calculate risk metrics
                risk_metrics = performance_tracker.calculate_risk_metrics(comparison_df)
                
                # Create comparison charts
                print("   - Creating performance comparison chart...")
                performance_fig = visualizer.create_performance_comparison_chart(
                    comparison_df, 
                    company_name=args.company
                )
                figures['performance_comparison'] = performance_fig
                
                print("   - Creating returns comparison chart...")
                try:
                    returns_fig = visualizer.create_returns_comparison_chart(
                        comparison_df, 
                        company_name=args.company
                    )
                    figures['returns_comparison'] = returns_fig
                except ValueError as e:
                    print(f"   ⚠️  Skipping returns chart: {e}")
                
                print("   - Creating risk metrics chart...")
                risk_fig = visualizer.create_risk_metrics_chart(
                    risk_metrics, 
                    company_name=args.company
                )
                figures['risk_metrics'] = risk_fig
                
                # Print performance summary
                print(f"\n📊 Performance Summary:")
                print(f"   - Portfolio Total Return: {risk_metrics.get('portfolio_total_return', 0):.2f}%")
                print(f"   - S&P 500 Total Return: {risk_metrics.get('sp500_total_return', 0):.2f}%")
                print(f"   - Relative Performance: {risk_metrics.get('relative_performance', 0):+.2f}%")
                if risk_metrics.get('portfolio_beta') is not None:
                    print(f"   - Portfolio Beta: {risk_metrics['portfolio_beta']:.2f}")
            
            # Save visualizations
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
            if args.compare_sp500:
                print("  📈 performance_comparison.png - Performance vs S&P 500")
                if 'returns_comparison' in figures:
                    print("  📊 returns_comparison.png - Quarterly returns comparison")
                print("  📊 risk_metrics.png - Risk-adjusted metrics comparison")
            if args.save_html:
                print("  🌐 portfolio_treemap.html - Interactive treemap")
                print("  🌐 sector_allocation.html - Interactive sector chart")
                print("  🌐 top_holdings.html - Interactive holdings chart")
                if args.compare_sp500:
                    print("  🌐 performance_comparison.html - Interactive performance chart")
                    if 'returns_comparison' in figures:
                        print("  🌐 returns_comparison.html - Interactive returns chart")
                    print("  🌐 risk_metrics.html - Interactive risk metrics chart")
        
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