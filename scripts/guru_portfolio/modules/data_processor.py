"""Data processor module for processing and analyzing portfolio data"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple


class DataProcessor:
    """Processes and analyzes 13F portfolio data"""
    
    def __init__(self):
        self.sector_mapping = self._load_sector_mapping()
    
    def process_portfolio_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process raw portfolio data for visualization
        
        Args:
            df: Raw portfolio DataFrame
            
        Returns:
            Processed DataFrame with additional calculated fields
        """
        # Make a copy to avoid modifying original
        processed_df = df.copy()
        
        # Calculate portfolio weight if not present
        if 'portfolio_weight' not in processed_df.columns or processed_df['portfolio_weight'].isna().all():
            total_value = processed_df['market_value'].sum()
            processed_df['portfolio_weight'] = (processed_df['market_value'] / total_value * 100)
        
        # Add sector information (simplified - in real world would use external data)
        processed_df['sector'] = processed_df['security_name'].apply(self._guess_sector)
        
        # Calculate value in millions for better readability
        processed_df['value_millions'] = processed_df['market_value'] / 1_000_000
        
        # Add display labels
        processed_df['display_label'] = processed_df.apply(
            lambda row: f"{row['security_name']}<br>"
                       f"${row['value_millions']:.1f}M ({row['portfolio_weight']:.1f}%)",
            axis=1
        )
        
        # Sort by market value descending
        processed_df = processed_df.sort_values('market_value', ascending=False)
        
        # Add rank
        processed_df['rank'] = range(1, len(processed_df) + 1)
        
        return processed_df
    
    def calculate_portfolio_metrics(self, df: pd.DataFrame) -> Dict:
        """
        Calculate key portfolio metrics
        
        Args:
            df: Processed portfolio DataFrame
            
        Returns:
            Dictionary with portfolio metrics
        """
        metrics = {
            'total_value': df['market_value'].sum(),
            'total_positions': len(df),
            'top_10_concentration': df.head(10)['portfolio_weight'].sum(),
            'largest_position': {
                'name': df.iloc[0]['security_name'],
                'weight': df.iloc[0]['portfolio_weight'],
                'value': df.iloc[0]['market_value']
            },
            'sector_breakdown': self._calculate_sector_breakdown(df),
            'concentration_metrics': self._calculate_concentration_metrics(df)
        }
        
        return metrics
    
    def prepare_treemap_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare data specifically for treemap visualization
        
        Args:
            df: Processed portfolio DataFrame
            
        Returns:
            DataFrame formatted for treemap
        """
        treemap_df = df.copy()
        
        # Filter out very small positions for clarity (optional)
        # treemap_df = treemap_df[treemap_df['portfolio_weight'] >= 0.1]
        
        # Ensure all required columns exist
        required_columns = ['security_name', 'sector', 'market_value', 
                          'portfolio_weight', 'display_label']
        
        for col in required_columns:
            if col not in treemap_df.columns:
                if col == 'sector':
                    treemap_df[col] = 'Unknown'
                else:
                    treemap_df[col] = ''
        
        return treemap_df
    
    def _load_sector_mapping(self) -> Dict[str, str]:
        """Load sector mapping for common stocks"""
        # Enhanced sector mapping - covers more companies
        return {
            # Technology
            'apple': 'Technology',
            'microsoft': 'Technology',
            'google': 'Technology',
            'alphabet': 'Technology',
            'meta': 'Technology',
            'facebook': 'Technology',
            'verisign': 'Technology',
            'amazon': 'Consumer Discretionary',  # Amazon is classified as Consumer Discretionary
            
            # Financials
            'berkshire': 'Financials',
            'bank of america': 'Financials',
            'bank amer': 'Financials',
            'wells': 'Financials',
            'jpmorgan': 'Financials',
            'chase': 'Financials',
            'american express': 'Financials',
            'visa': 'Financials',
            'mastercard': 'Financials',
            'capital one': 'Financials',
            'moody': 'Financials',
            'moodys': 'Financials',
            'aon': 'Financials',
            'chubb': 'Financials',
            'insurance': 'Financials',
            
            # Energy
            'chevron': 'Energy',
            'exxon': 'Energy',
            'occidental': 'Energy',
            'petroleum': 'Energy',
            'conocophillips': 'Energy',
            
            # Consumer Staples
            'coca cola': 'Consumer Staples',
            'coca-cola': 'Consumer Staples',
            'pepsi': 'Consumer Staples',
            'kraft': 'Consumer Staples',
            'heinz': 'Consumer Staples',
            'kroger': 'Consumer Staples',
            'constellation brands': 'Consumer Staples',
            'procter': 'Consumer Staples',
            'p&g': 'Consumer Staples',
            'walmart': 'Consumer Staples',
            'costco': 'Consumer Staples',
            
            # Healthcare
            'johnson': 'Healthcare',
            'pfizer': 'Healthcare',
            'merck': 'Healthcare',
            'davita': 'Healthcare',
            'unitedhealth': 'Healthcare',
            'abbvie': 'Healthcare',
            'abbott': 'Healthcare',
            'eli lilly': 'Healthcare',
            'bristol': 'Healthcare',
            'cvs': 'Healthcare',
            
            # Consumer Discretionary
            'dominos': 'Consumer Discretionary',
            'pizza': 'Consumer Discretionary',
            'mcdonald': 'Consumer Discretionary',
            'starbucks': 'Consumer Discretionary',
            'nike': 'Consumer Discretionary',
            'home depot': 'Consumer Discretionary',
            'tesla': 'Consumer Discretionary',
            
            # Communication Services
            'sirius': 'Communication Services',
            'comcast': 'Communication Services',
            'disney': 'Communication Services',
            'netflix': 'Communication Services',
            'verizon': 'Communication Services',
            'at&t': 'Communication Services',
            't-mobile': 'Communication Services',
            
            # Industrials
            'boeing': 'Industrials',
            'caterpillar': 'Industrials',
            'general electric': 'Industrials',
            'honeywell': 'Industrials',
            '3m': 'Industrials',
            'ups': 'Industrials',
            'fedex': 'Industrials',
        }
    
    def _guess_sector(self, security_name: str) -> str:
        """Guess sector based on security name"""
        name_lower = security_name.lower()
        
        for keyword, sector in self.sector_mapping.items():
            if keyword in name_lower:
                return sector
        
        # Default sectors based on common patterns
        if any(word in name_lower for word in ['reit', 'property', 'real estate']):
            return 'Real Estate'
        elif any(word in name_lower for word in ['utility', 'electric', 'gas']):
            return 'Utilities'
        elif any(word in name_lower for word in ['telecom', 'communications']):
            return 'Communication Services'
        elif any(word in name_lower for word in ['materials', 'chemical', 'mining']):
            return 'Materials'
        elif any(word in name_lower for word in ['industrial', 'aerospace', 'defense']):
            return 'Industrials'
        
        return 'Other'
    
    def _calculate_sector_breakdown(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate portfolio weight by sector"""
        sector_weights = df.groupby('sector')['portfolio_weight'].sum().to_dict()
        return dict(sorted(sector_weights.items(), key=lambda x: x[1], reverse=True))
    
    def _calculate_concentration_metrics(self, df: pd.DataFrame) -> Dict:
        """Calculate portfolio concentration metrics"""
        weights = df['portfolio_weight'].values
        
        # Herfindahl-Hirschman Index (HHI)
        hhi = np.sum(weights ** 2)
        
        # Effective number of positions
        effective_n = 1 / hhi if hhi > 0 else 0
        
        # Gini coefficient
        gini = self._calculate_gini(weights)
        
        return {
            'hhi': hhi,
            'effective_positions': effective_n,
            'gini_coefficient': gini,
            'top_5_weight': df.head(5)['portfolio_weight'].sum(),
            'top_20_weight': df.head(20)['portfolio_weight'].sum()
        }
    
    def _calculate_gini(self, weights: np.ndarray) -> float:
        """Calculate Gini coefficient for concentration"""
        # Sort weights
        sorted_weights = np.sort(weights)
        n = len(sorted_weights)
        
        # Calculate Gini
        cumsum = np.cumsum(sorted_weights)
        return (2 * np.sum((np.arange(1, n + 1) * sorted_weights))) / (n * cumsum[-1]) - (n + 1) / n 