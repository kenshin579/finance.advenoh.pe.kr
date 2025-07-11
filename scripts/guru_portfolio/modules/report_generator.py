"""Report generator module for creating portfolio analysis reports"""

import pandas as pd
from datetime import datetime
from typing import Dict, Any
import os


class ReportGenerator:
    """Generates markdown reports for portfolio analysis"""
    
    def __init__(self):
        self.report_template = """# 13F Portfolio Analysis Report

**Company**: {company}  
**Quarter**: {quarter}  
**Generated**: {generated_date}

---

## Executive Summary

- **Total Portfolio Value**: ${total_value:,.0f}
- **Number of Positions**: {total_positions}
- **Top 10 Concentration**: {top_10_concentration:.1f}%
- **Largest Position**: {largest_position_name} ({largest_position_weight:.1f}%)

## Portfolio Metrics

### Concentration Analysis
- **Top 5 Holdings Weight**: {top_5_weight:.1f}%
- **Top 20 Holdings Weight**: {top_20_weight:.1f}%
- **Herfindahl-Hirschman Index (HHI)**: {hhi:.4f}
- **Effective Number of Positions**: {effective_positions:.1f}
- **Gini Coefficient**: {gini:.3f}

### Sector Allocation

{sector_table}

## Top 20 Holdings

{holdings_table}

## Visualizations

The following visualizations have been generated:

1. **Portfolio Treemap** (`portfolio_treemap.png`): Treemap showing all holdings sized by market value
2. **Sector Allocation Pie Chart** (`sector_allocation.png`): Breakdown of portfolio by sector
3. **Top Holdings Bar Chart** (`top_holdings.png`): Bar chart of top 20 holdings by weight

### Portfolio Treemap
![Portfolio Treemap](portfolio_treemap.png)

### Sector Allocation
![Sector Allocation](sector_allocation.png)

### Top Holdings
![Top Holdings](top_holdings.png)

## Analysis Notes

{analysis_notes}

---

*This report was automatically generated from 13F filing data available at [13f.info](https://13f.info)*
"""
    
    def generate_report(self, 
                       company: str,
                       quarter: str,
                       processed_df: pd.DataFrame,
                       metrics: Dict[str, Any],
                       output_path: str = "portfolio_analysis.md") -> str:
        """
        Generate a comprehensive markdown report
        
        Args:
            company: Company name
            quarter: Quarter (e.g., "Q1 2025")
            processed_df: Processed portfolio DataFrame
            metrics: Portfolio metrics dictionary
            output_path: Path to save the report
            
        Returns:
            Path to the generated report
        """
        # Generate sector table
        sector_table = self._generate_sector_table(metrics['sector_breakdown'])
        
        # Generate holdings table
        holdings_table = self._generate_holdings_table(processed_df.head(20))
        
        # Generate analysis notes
        analysis_notes = self._generate_analysis_notes(metrics, processed_df)
        
        # Format the report
        report_content = self.report_template.format(
            company=company,
            quarter=quarter,
            generated_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            total_value=metrics['total_value'],
            total_positions=metrics['total_positions'],
            top_10_concentration=metrics['top_10_concentration'],
            largest_position_name=metrics['largest_position']['name'],
            largest_position_weight=metrics['largest_position']['weight'],
            top_5_weight=metrics['concentration_metrics']['top_5_weight'],
            top_20_weight=metrics['concentration_metrics']['top_20_weight'],
            hhi=metrics['concentration_metrics']['hhi'],
            effective_positions=metrics['concentration_metrics']['effective_positions'],
            gini=metrics['concentration_metrics']['gini_coefficient'],
            sector_table=sector_table,
            holdings_table=holdings_table,
            analysis_notes=analysis_notes
        )
        
        # Save the report
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return output_path
    
    def _generate_sector_table(self, sector_breakdown: Dict[str, float]) -> str:
        """Generate markdown table for sector breakdown"""
        table = "| Sector | Weight (%) |\n"
        table += "|--------|------------|\n"
        
        for sector, weight in sector_breakdown.items():
            table += f"| {sector} | {weight:.2f}% |\n"
        
        return table
    
    def _generate_holdings_table(self, top_holdings: pd.DataFrame) -> str:
        """Generate markdown table for top holdings"""
        table = "| Rank | Security | Shares | Value | Weight (%) |\n"
        table += "|------|----------|--------|-------|------------|\n"
        
        for _, row in top_holdings.iterrows():
            table += (f"| {row['rank']} | {row['security_name']} | "
                     f"{row['shares']:,.0f} | ${row['value_millions']:.1f}M | "
                     f"{row['portfolio_weight']:.2f}% |\n")
        
        return table
    
    def _generate_analysis_notes(self, metrics: Dict[str, Any], df: pd.DataFrame) -> str:
        """Generate analytical insights"""
        notes = []
        
        # Concentration analysis
        hhi = metrics['concentration_metrics']['hhi']
        if hhi > 0.15:
            notes.append("- **High Concentration**: The portfolio shows high concentration "
                        f"(HHI = {hhi:.3f}), indicating significant weight in top positions.")
        elif hhi < 0.05:
            notes.append("- **Well Diversified**: The portfolio is well-diversified "
                        f"(HHI = {hhi:.3f}), with no single position dominating.")
        
        # Sector concentration
        top_sector = max(metrics['sector_breakdown'].items(), key=lambda x: x[1])
        if top_sector[1] > 40:
            notes.append(f"- **Sector Concentration**: {top_sector[0]} sector represents "
                        f"{top_sector[1]:.1f}% of the portfolio, showing significant sector bet.")
        
        # Position count analysis
        if metrics['total_positions'] < 20:
            notes.append("- **Focused Portfolio**: With fewer than 20 positions, this is "
                        "a highly focused investment strategy.")
        elif metrics['total_positions'] > 100:
            notes.append("- **Broad Diversification**: The portfolio contains over 100 positions, "
                        "indicating a broadly diversified approach.")
        
        # Top holding analysis
        if metrics['largest_position']['weight'] > 20:
            notes.append(f"- **Dominant Position**: {metrics['largest_position']['name']} "
                        f"represents {metrics['largest_position']['weight']:.1f}% of the portfolio.")
        
        return "\n".join(notes) if notes else "No significant concentration issues identified."
    
    def generate_summary_report(self, 
                              company: str,
                              quarter: str,
                              error_message: str = None) -> str:
        """
        Generate a simple error report if data fetching fails
        
        Args:
            company: Company name
            quarter: Quarter
            error_message: Error message to include
            
        Returns:
            Error report content
        """
        report = f"""# 13F Portfolio Analysis Report - Error

**Company**: {company}  
**Quarter**: {quarter}  
**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## Error

Unable to fetch portfolio data for the specified company and quarter.

**Error Details**: {error_message}

## Possible Reasons

1. The company name might not exactly match the name in the 13F database
2. The specified quarter might not have been filed yet
3. The company might not be required to file 13F reports
4. Network connection issues

## Suggestions

- Try searching for the company on [13f.info](https://13f.info) to find the exact name
- Verify that the quarter has been filed (13F reports are filed 45 days after quarter end)
- Check if the company is an institutional investment manager with >$100M AUM

---

*This report was automatically generated*
"""
        return report 