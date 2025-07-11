# 13F Portfolio Visualization Tool - Demo Output

This demonstrates what the tool produces when you run:

```bash
python main.py "Berkshire Hathaway Inc" "Q3 2024"
```

## Console Output

```
============================================================
13F Portfolio Analysis Tool
============================================================
Company: Berkshire Hathaway Inc
Quarter: Q3 2024
Output Directory: output
============================================================

📊 Fetching portfolio data from 13f.info...
✅ Successfully fetched 45 holdings

🔄 Processing portfolio data...
✅ Data processed successfully
   - Total value: $313,259,486,000
   - Total positions: 45
   - Top 10 concentration: 87.5%

📈 Creating visualizations...
   - Creating portfolio treemap...
   - Creating sector allocation chart...
   - Creating top holdings chart...
✅ Saved portfolio_treemap.png
✅ Saved sector_allocation.png
✅ Saved top_holdings.png
✅ Visualizations saved

📝 Generating analysis report...
✅ Report saved to: output/portfolio_analysis.md

============================================================
✨ Analysis completed successfully!
============================================================

Results saved in: /Users/user/WebstormProjects/finance-guru/scripts/guru_portfolio/output/

Generated files:
  📄 portfolio_analysis.md - Detailed analysis report
  🖼️  portfolio_treemap.png - Portfolio treemap visualization
  🖼️  sector_allocation.png - Sector breakdown pie chart
  🖼️  top_holdings.png - Top holdings bar chart
```

## Generated Files

### 1. portfolio_analysis.md (Sample)

```markdown
# 13F Portfolio Analysis Report

**Company**: Berkshire Hathaway Inc  
**Quarter**: Q3 2024  
**Generated**: 2024-12-31 10:30:00

---

## Executive Summary

- **Total Portfolio Value**: $313,259,486,000
- **Number of Positions**: 45
- **Top 10 Concentration**: 87.5%
- **Largest Position**: Apple Inc (30.1%)

## Portfolio Metrics

### Concentration Analysis
- **Top 5 Holdings Weight**: 70.2%
- **Top 20 Holdings Weight**: 95.8%
- **Herfindahl-Hirschman Index (HHI)**: 0.1234
- **Effective Number of Positions**: 8.1
- **Gini Coefficient**: 0.823

### Sector Allocation

| Sector | Weight (%) |
|--------|------------|
| Technology | 45.3% |
| Financials | 28.7% |
| Consumer Staples | 12.4% |
| Energy | 8.9% |
| Healthcare | 2.8% |
| Other | 1.9% |

## Top 20 Holdings

| Rank | Security | Shares | Value | Weight (%) |
|------|----------|--------|-------|------------|
| 1 | Apple Inc | 915,560,382 | $94,345.2M | 30.12% |
| 2 | Bank of America Corp | 1,032,852,006 | $41,099.3M | 13.12% |
| 3 | American Express Co | 151,610,700 | $35,987.5M | 11.49% |
| 4 | Coca-Cola Co | 400,000,000 | $28,700.0M | 9.16% |
| 5 | Chevron Corp | 123,080,996 | $18,607.8M | 5.94% |
...
```

### 2. portfolio_treemap.png
- High-resolution treemap showing all holdings
- Hierarchical view: Portfolio → Sector → Individual stocks
- Color-coded by portfolio weight
- Size represents market value

### 3. sector_allocation.png
- Pie chart showing sector breakdown
- Clear percentage labels
- Color-coded sectors

### 4. top_holdings.png
- Horizontal bar chart of top 20 holdings
- Sorted by portfolio weight
- Shows both percentage and dollar values

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

...
```

## Key Features Demonstrated

1. **Data Extraction**: Automatically fetches data from 13f.info
2. **Portfolio Metrics**: Calculates concentration metrics, HHI, Gini coefficient
3. **Sector Analysis**: Automatically categorizes holdings by sector
4. **Interactive Visualizations**: Creates plotly-based interactive charts
5. **Comprehensive Reporting**: Generates detailed markdown reports

## Error Handling

If the company or quarter is not found, the tool generates an error report with suggestions:

```markdown
# 13F Portfolio Analysis Report - Error

**Company**: XYZ Company  
**Quarter**: Q5 2024  
**Generated**: 2024-12-31 10:30:00

---

## Error

Unable to fetch portfolio data for the specified company and quarter.

**Error Details**: Company 'XYZ Company' not found

## Possible Reasons

1. The company name might not exactly match the name in the 13F database
2. The specified quarter might not have been filed yet
3. The company might not be required to file 13F reports
4. Network connection issues

## Suggestions

- Try searching for the company on [13f.info](https://13f.info) to find the exact name
- Verify that the quarter has been filed (13F reports are filed 45 days after quarter end)
- Check if the company is an institutional investment manager with >$100M AUM
``` 