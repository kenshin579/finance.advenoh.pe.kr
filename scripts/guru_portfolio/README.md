# 13F Portfolio Visualization Tool

A Python tool for fetching and visualizing institutional investor portfolio data from 13F filings via [13f.info](https://13f.info).

## Features

- 📊 **Data Extraction**: Automatically fetches portfolio data from 13f.info
- 📈 **Interactive Visualizations**: 
  - Treemap visualization of portfolio holdings
  - Sector allocation pie chart
  - Top holdings bar chart
- 📝 **Comprehensive Reports**: Generates detailed markdown reports with portfolio metrics
- 🔍 **Portfolio Analysis**: 
  - Concentration metrics (HHI, Gini coefficient)
  - Sector breakdown
  - Top holdings analysis

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
```

### Command Line Options

- `company`: Company name (must match exactly as shown on 13f.info)
- `quarter`: Quarter in format "Q1 2025"
- `--output-dir`, `-o`: Output directory for results (default: `output`)
- `--top-n`, `-n`: Number of top holdings to show in bar chart (default: 20)
- `--no-visualizations`: Skip creating visualizations (only generate report)
- `--save-html`: Also save visualizations as interactive HTML files

## Output

The tool generates the following files in the output directory:

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

Optionally (with `--save-html` flag):
- Interactive HTML versions of all visualizations

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

## Dependencies

- pandas: Data manipulation and analysis
- plotly: Interactive visualizations
- requests: HTTP requests for web scraping
- beautifulsoup4: HTML parsing
- lxml: XML/HTML parser
- numpy: Numerical computations
- kaleido: Static image export for plotly

## License

[Your License Here]

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 