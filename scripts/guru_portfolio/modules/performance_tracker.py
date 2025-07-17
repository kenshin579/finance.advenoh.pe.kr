"""Performance tracker module for portfolio comparison with benchmarks"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')


class PerformanceTracker:
    """Tracks portfolio performance and compares with benchmarks"""
    
    def __init__(self):
        self.sp500_ticker = "^GSPC"  # S&P 500 index ticker
        
    def fetch_sp500_data(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetch S&P 500 historical data
        
        Args:
            start_date: Start date in format 'YYYY-MM-DD'
            end_date: End date in format 'YYYY-MM-DD'
            
        Returns:
            DataFrame with S&P 500 price data
        """
        try:
            sp500 = yf.download(self.sp500_ticker, start=start_date, end=end_date, progress=False)
            sp500_df = pd.DataFrame({
                'date': sp500.index,
                'sp500_close': sp500['Close'],
                'sp500_return': sp500['Close'].pct_change()
            }).reset_index(drop=True)
            
            return sp500_df
        except Exception as e:
            raise Exception(f"Error fetching S&P 500 data: {str(e)}")
    
    def calculate_portfolio_performance(self, 
                                      holdings_history: List[pd.DataFrame], 
                                      dates: List[str]) -> pd.DataFrame:
        """
        Calculate portfolio performance over time
        
        Args:
            holdings_history: List of DataFrames with portfolio holdings for each quarter
            dates: List of corresponding dates for each holdings snapshot
            
        Returns:
            DataFrame with portfolio performance metrics
        """
        portfolio_values = []
        
        for holdings_df, date in zip(holdings_history, dates):
            total_value = holdings_df['market_value'].sum()
            portfolio_values.append({
                'date': pd.to_datetime(date),
                'portfolio_value': total_value
            })
        
        portfolio_df = pd.DataFrame(portfolio_values)
        portfolio_df = portfolio_df.sort_values('date').reset_index(drop=True)
        
        # Calculate returns
        portfolio_df['portfolio_return'] = portfolio_df['portfolio_value'].pct_change()
        
        return portfolio_df
    
    def compare_performance(self, 
                          portfolio_df: pd.DataFrame,
                          start_date: str,
                          end_date: str) -> pd.DataFrame:
        """
        Compare portfolio performance with S&P 500
        
        Args:
            portfolio_df: DataFrame with portfolio performance data
            start_date: Start date for comparison
            end_date: End date for comparison
            
        Returns:
            Combined DataFrame with portfolio and S&P 500 performance
        """
        # Fetch S&P 500 data
        sp500_df = self.fetch_sp500_data(start_date, end_date)
        
        # Normalize dates for merging
        portfolio_df['date'] = pd.to_datetime(portfolio_df['date'])
        sp500_df['date'] = pd.to_datetime(sp500_df['date'])
        
        # For quarterly portfolio data, we'll match to the nearest S&P 500 date
        combined_data = []
        
        for _, row in portfolio_df.iterrows():
            portfolio_date = row['date']
            
            # Find nearest S&P 500 date
            date_diffs = abs(sp500_df['date'] - portfolio_date)
            nearest_idx = date_diffs.argmin()
            sp500_row = sp500_df.iloc[nearest_idx]
            
            combined_data.append({
                'date': portfolio_date,
                'portfolio_value': row['portfolio_value'],
                'portfolio_return': row.get('portfolio_return', 0),
                'sp500_close': sp500_row['sp500_close'],
                'sp500_return': sp500_row.get('sp500_return', 0)
            })
        
        comparison_df = pd.DataFrame(combined_data)
        
        # Calculate cumulative returns
        comparison_df['portfolio_cum_return'] = (1 + comparison_df['portfolio_return'].fillna(0)).cumprod() - 1
        comparison_df['sp500_cum_return'] = (1 + comparison_df['sp500_return'].fillna(0)).cumprod() - 1
        
        # Calculate normalized values (base 100)
        if len(comparison_df) > 0:
            comparison_df['portfolio_normalized'] = 100 * comparison_df['portfolio_value'] / comparison_df['portfolio_value'].iloc[0]
            comparison_df['sp500_normalized'] = 100 * comparison_df['sp500_close'] / comparison_df['sp500_close'].iloc[0]
        
        return comparison_df
    
    def calculate_risk_metrics(self, comparison_df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate risk-adjusted performance metrics
        
        Args:
            comparison_df: DataFrame with portfolio and benchmark performance
            
        Returns:
            Dictionary with risk metrics
        """
        metrics = {}
        
        # Remove NaN values for calculations
        portfolio_returns = comparison_df['portfolio_return'].dropna()
        sp500_returns = comparison_df['sp500_return'].dropna()
        
        if len(portfolio_returns) > 1:
            # Volatility (annualized)
            metrics['portfolio_volatility'] = portfolio_returns.std() * np.sqrt(4)  # Quarterly to annual
            metrics['sp500_volatility'] = sp500_returns.std() * np.sqrt(4)
            
            # Total return
            metrics['portfolio_total_return'] = comparison_df['portfolio_cum_return'].iloc[-1] * 100
            metrics['sp500_total_return'] = comparison_df['sp500_cum_return'].iloc[-1] * 100
            
            # Relative performance
            metrics['relative_performance'] = metrics['portfolio_total_return'] - metrics['sp500_total_return']
            
            # Sharpe ratio (assuming 0% risk-free rate for simplicity)
            portfolio_avg_return = portfolio_returns.mean() * 4  # Annualized
            sp500_avg_return = sp500_returns.mean() * 4
            
            if metrics['portfolio_volatility'] > 0:
                metrics['portfolio_sharpe'] = portfolio_avg_return / metrics['portfolio_volatility']
            else:
                metrics['portfolio_sharpe'] = 0
                
            if metrics['sp500_volatility'] > 0:
                metrics['sp500_sharpe'] = sp500_avg_return / metrics['sp500_volatility']
            else:
                metrics['sp500_sharpe'] = 0
            
            # Beta (if enough data points)
            if len(portfolio_returns) >= 4:
                covariance = np.cov(portfolio_returns, sp500_returns)[0, 1]
                sp500_variance = np.var(sp500_returns)
                if sp500_variance > 0:
                    metrics['portfolio_beta'] = covariance / sp500_variance
                else:
                    metrics['portfolio_beta'] = 1.0
            else:
                metrics['portfolio_beta'] = None
        
        return metrics
    
    def simulate_portfolio_from_holdings(self, current_holdings: pd.DataFrame, 
                                       lookback_quarters: int = 4) -> List[Tuple[str, pd.DataFrame]]:
        """
        Simulate historical portfolio values based on current holdings
        This is a simplified approach that assumes the same holdings over time
        
        Args:
            current_holdings: Current portfolio holdings
            lookback_quarters: Number of quarters to look back
            
        Returns:
            List of (date, holdings) tuples
        """
        holdings_history = []
        current_date = datetime.now()
        
        # Generate quarterly dates going back
        for i in range(lookback_quarters + 1):
            # Calculate date for each quarter
            months_back = i * 3
            quarter_date = current_date - timedelta(days=months_back * 30)
            date_str = quarter_date.strftime('%Y-%m-%d')
            
            # For simulation, we'll adjust values based on S&P 500 performance
            # This is a simplified approach
            simulated_holdings = current_holdings.copy()
            
            # Adjust market values based on how far back we're looking
            # This is a rough approximation
            adjustment_factor = 1 - (i * 0.02)  # Assume 2% growth per quarter
            simulated_holdings['market_value'] = simulated_holdings['market_value'] * adjustment_factor
            
            holdings_history.append((date_str, simulated_holdings))
        
        # Reverse to have chronological order
        holdings_history.reverse()
        
        return holdings_history 