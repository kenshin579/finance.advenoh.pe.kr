# 13F Portfolio Visualization Tool

A Python tool for fetching and visualizing institutional investor portfolio data from 13F filings via [13f.info](https://13f.info).

## Features

- 📊 **Data Extraction**: Automatically fetches portfolio data from 13f.info
- 📈 **Interactive Visualizations**: 
  - Treemap visualization of portfolio holdings
  - Sector allocation pie chart
  - Top holdings bar chart
  - Performance comparison with S&P 500 benchmark
  - Quarterly returns comparison
  - Risk-adjusted metrics visualization
- 📝 **Comprehensive Reports**: Generates detailed markdown reports with portfolio metrics
- 🔍 **Portfolio Analysis**: 
  - Concentration metrics (HHI, Gini coefficient)
  - Sector breakdown
  - Top holdings analysis
  - Performance vs S&P 500 benchmark
  - Risk metrics (Sharpe ratio, beta, volatility)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd guru_portfolio
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

Or using the pyproject.toml:
```bash
pip install -e .
```

## Usage

Basic usage:
```bash
python main.py "Company Name" "Quarter"
```

### Examples

```bash
# Berkshire Hathaway Q3 2024
python main.py "Berkshire Hathaway Inc" "Q3 2024"

# Bridgewater Associates Q2 2024 with custom output directory
python main.py "Bridgewater Associates" "Q2 2024" --output-dir results/

# Scion Asset Management with top 30 holdings
python main.py "Scion Asset Management" "Q4 2023" --top-n 30

# ARK Invest with S&P 500 performance comparison (4 quarters lookback)
python main.py "ARK Invest" "Q3 2024" --compare-sp500 --lookback-quarters 4

# Berkshire Hathaway with extended performance history (8 quarters)
python main.py "Berkshire Hathaway Inc" "Q3 2024" --compare-sp500 --lookback-quarters 8 --save-html
```

### Command Line Options

- `company`: Company name (must match exactly as shown on 13f.info)
- `quarter`: Quarter in format "Q1 2025"
- `--output-dir`, `-o`: Output directory for results (default: `output`)
- `--top-n`, `-n`: Number of top holdings to show in bar chart (default: 20)
- `--no-visualizations`: Skip creating visualizations (only generate report)
- `--save-html`: Also save visualizations as interactive HTML files
- `--compare-sp500`: Enable performance comparison with S&P 500 benchmark
- `--lookback-quarters`: Number of quarters to look back for performance comparison (default: 4)

## Output

The tool generates the following files in the output directory:

### Standard Output Files

1. **portfolio_analysis.md**: Comprehensive markdown report including:
   - Executive summary
   - Portfolio metrics and concentration analysis
   - Sector breakdown
   - Top 20 holdings table
   - Analysis notes
   - Embedded PNG visualizations

2. **portfolio_treemap.png**: High-resolution treemap visualization showing all holdings sized by market value

3. **sector_allocation.png**: Pie chart showing portfolio allocation by sector

4. **top_holdings.png**: Bar chart of top N holdings by portfolio weight

### Performance Comparison Files (with `--compare-sp500`)

5. **performance_comparison.png**: Line chart comparing portfolio performance vs S&P 500 over time

6. **returns_comparison.png**: Bar chart showing quarterly returns comparison

7. **risk_metrics.png**: Bar chart comparing risk-adjusted metrics:
   - Total return
   - Volatility (annualized)
   - Sharpe ratio
   - Beta (if sufficient data)

### Interactive HTML Files (with `--save-html`)
- Interactive HTML versions of all visualizations for enhanced exploration

## Performance Comparison Feature

When using `--compare-sp500`, the tool:

1. **Simulates Historical Portfolio Values**: Creates a simplified historical view based on current holdings
2. **Fetches S&P 500 Data**: Downloads benchmark data from Yahoo Finance
3. **Calculates Performance Metrics**:
   - Total return over the period
   - Quarterly returns
   - Cumulative returns
   - Risk-adjusted performance (Sharpe ratio)
   - Portfolio beta vs market
4. **Generates Comparison Visualizations**: Creates clear charts showing relative performance

### Performance Metrics Explained

- **Total Return**: Percentage change from start to end of period
- **Volatility**: Standard deviation of returns (annualized)
- **Sharpe Ratio**: Risk-adjusted return metric (higher is better)
- **Beta**: Measure of portfolio's volatility relative to S&P 500
- **Relative Performance**: Difference between portfolio and S&P 500 returns

## Testing

Run the test script to see the performance comparison feature in action:

```bash
python test_performance_comparison.py
```

This will test the feature with multiple well-known investment firms and generate sample outputs.

## Example Report

The generated markdown report includes:

- Total portfolio value and number of positions
- Concentration metrics (HHI, Gini coefficient, top holdings concentration)
- Sector allocation breakdown
- Detailed holdings table with shares, value, and weights
- Analytical insights based on portfolio characteristics

## Notes

- Company names must match exactly as they appear on 13f.info
- 13F reports are typically filed 45 days after quarter end
- Only institutional investment managers with >$100M AUM are required to file 13F reports
- The tool uses web scraping, so it may need updates if the website structure changes
- Performance comparison uses simplified assumptions and should not be used for actual investment decisions

## Dependencies

- pandas: Data manipulation and analysis
- plotly: Interactive visualizations
- requests: HTTP requests for web scraping
- beautifulsoup4: HTML parsing
- lxml: XML/HTML parser
- numpy: Numerical computations
- kaleido: Static image export for plotly
- yfinance: Yahoo Finance data for S&P 500 benchmark

## License

[Your License Here]

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 