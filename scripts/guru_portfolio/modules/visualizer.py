"""Visualizer module for creating portfolio visualizations"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, Optional
import plotly.io as pio


class Visualizer:
    """Creates visualizations for portfolio data"""
    
    def __init__(self):
        # Set default theme
        pio.templates.default = "plotly_white"
        
        # Color scheme for sectors
        self.sector_colors = {
            'Technology': '#1f77b4',
            'Financials': '#ff7f0e',
            'Healthcare': '#2ca02c',
            'Consumer Discretionary': '#d62728',
            'Consumer Staples': '#9467bd',
            'Energy': '#8c564b',
            'Industrials': '#e377c2',
            'Materials': '#7f7f7f',
            'Real Estate': '#bcbd22',
            'Utilities': '#17becf',
            'Communication Services': '#ff9896',
            'Other': '#aec7e8',
            'Other (<1% each)': '#aec7e8'
        }
    
    def create_treemap(self, df: pd.DataFrame, title: str = "Portfolio Holdings Treemap") -> go.Figure:
        """
        Create an interactive treemap visualization of portfolio holdings
        
        Args:
            df: Processed portfolio DataFrame
            title: Chart title
            
        Returns:
            Plotly Figure object
        """
        # Prepare data for treemap
        df_treemap = df.copy()
        
        # Sort by market value for better visualization
        df_treemap = df_treemap.sort_values('market_value', ascending=False)
        
        # Create color scale based on sector
        unique_sectors = df_treemap['sector'].unique()
        sector_color_map = {sector: self.sector_colors.get(sector, '#999999') 
                           for sector in unique_sectors}
        
        # Assign colors based on sector
        colors = [sector_color_map[sector] for sector in df_treemap['sector']]
        
        fig = go.Figure(go.Treemap(
            labels=df_treemap['security_name'].tolist(),
            parents=[''] * len(df_treemap),  # No hierarchy, all at root level
            values=df_treemap['market_value'].tolist(),
            text=[f"{row['security_name']}<br>"
                  f"{row['sector']}<br>"
                  f"${row['value_millions']:.1f}M<br>"
                  f"{row['portfolio_weight']:.2f}%"
                  for _, row in df_treemap.iterrows()],
            textinfo="text",
            hovertemplate='<b>%{label}</b><br>' +
                         'Sector: %{customdata}<br>' +
                         'Value: $%{value:,.0f}<br>' +
                         'Weight: %{text}%<br>' +
                         '<extra></extra>',
            customdata=df_treemap['sector'].tolist(),
            marker=dict(
                colors=colors,
                line=dict(width=2, color='white')
            ),
            # Add portfolio weight as hover text
            hovertext=[f"{weight:.2f}" for weight in df_treemap['portfolio_weight']]
        ))
        
        # Update layout
        fig.update_layout(
            title={
                'text': title,
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 24}
            },
            margin=dict(t=80, l=10, r=10, b=10),
            height=800,
            width=1200
        )
        
        return fig
    
    def create_sector_pie_chart(self, df: pd.DataFrame) -> go.Figure:
        """
        Create a pie chart showing sector allocation
        
        Args:
            df: Processed portfolio DataFrame
            
        Returns:
            Plotly Figure object
        """
        # Aggregate by sector
        sector_data = df.groupby('sector').agg({
            'market_value': 'sum',
            'portfolio_weight': 'sum'
        }).reset_index()
        
        # Sort by weight
        sector_data = sector_data.sort_values('portfolio_weight', ascending=False)
        
        # Group sectors with less than 1% into "Other"
        other_threshold = 1.0  # 1% threshold
        
        # Separate major and minor sectors
        major_sectors = sector_data[sector_data['portfolio_weight'] >= other_threshold].copy()
        minor_sectors = sector_data[sector_data['portfolio_weight'] < other_threshold]
        
        # If there are minor sectors, combine them into "Other"
        if len(minor_sectors) > 0:
            other_row = pd.DataFrame({
                'sector': ['Other (<1% each)'],
                'market_value': [minor_sectors['market_value'].sum()],
                'portfolio_weight': [minor_sectors['portfolio_weight'].sum()]
            })
            sector_data = pd.concat([major_sectors, other_row], ignore_index=True)
        else:
            sector_data = major_sectors
        
        # Sort again by weight
        sector_data = sector_data.sort_values('portfolio_weight', ascending=False)
        
        # Create colors list
        colors = [self.sector_colors.get(sector, '#999999') for sector in sector_data['sector']]
        
        fig = go.Figure(data=[go.Pie(
            labels=sector_data['sector'],
            values=sector_data['market_value'],
            text=[f"{sector}<br>{weight:.1f}%" 
                  for sector, weight in zip(sector_data['sector'], sector_data['portfolio_weight'])],
            textposition='inside',
            textinfo='text',
            insidetextorientation='radial',
            marker=dict(colors=colors, line=dict(color='white', width=2)),
            hovertemplate='<b>%{label}</b><br>' +
                         'Value: $%{value:,.0f}<br>' +
                         'Weight: %{percent}<br>' +
                         '<extra></extra>'
        )])
        
        fig.update_layout(
            title={
                'text': 'Portfolio Allocation by Sector',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20}
            },
            height=600,
            width=800,
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.05
            ),
            font=dict(size=14)
        )
        
        return fig
    
    def create_concentration_chart(self, df: pd.DataFrame, top_n: int = 20) -> go.Figure:
        """
        Create a bar chart showing top holdings
        
        Args:
            df: Processed portfolio DataFrame
            top_n: Number of top holdings to show
            
        Returns:
            Plotly Figure object
        """
        # Get top N holdings
        top_holdings = df.head(top_n).copy()
        
        # Reverse order for better visualization
        top_holdings = top_holdings.iloc[::-1]
        
        fig = go.Figure()
        
        # Add bar trace
        fig.add_trace(go.Bar(
            x=top_holdings['portfolio_weight'],
            y=top_holdings['security_name'],
            orientation='h',
            text=[f"{weight:.2f}%" for weight in top_holdings['portfolio_weight']],
            textposition='outside',
            marker=dict(
                color=top_holdings['portfolio_weight'],
                colorscale='Blues',
                showscale=False
            ),
            hovertemplate='<b>%{y}</b><br>' +
                         'Weight: %{x:.2f}%<br>' +
                         'Value: $%{customdata:,.0f}<br>' +
                         '<extra></extra>',
            customdata=top_holdings['market_value']
        ))
        
        # Update layout
        fig.update_layout(
            title={
                'text': f'Top {top_n} Holdings by Weight',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20}
            },
            xaxis=dict(
                title='Portfolio Weight (%)',
                tickformat='.1f',
                range=[0, max(top_holdings['portfolio_weight']) * 1.1]
            ),
            yaxis=dict(
                title='',
                tickmode='linear'
            ),
            height=max(600, top_n * 30),
            width=1000,
            margin=dict(l=200, r=50, t=80, b=50)
        )
        
        return fig
    
    def save_visualizations(self, figures: Dict[str, go.Figure], output_dir: str = ".", save_html: bool = False):
        """
        Save all figures as PNG images (and optionally as HTML)
        
        Args:
            figures: Dictionary of figure names and Figure objects
            output_dir: Directory to save outputs
            save_html: Whether to also save as interactive HTML (default: False)
        """
        import os
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        for name, fig in figures.items():
            # Save as PNG (primary format)
            png_path = os.path.join(output_dir, f"{name}.png")
            try:
                # High quality PNG export
                fig.write_image(
                    png_path, 
                    width=1200, 
                    height=800, 
                    scale=2,  # 2x resolution for better quality
                    engine='kaleido'
                )
                print(f"✅ Saved {name}.png")
            except Exception as e:
                print(f"❌ Error saving {name}.png: {e}")
                print("Make sure kaleido is installed: pip install kaleido")
            
            # Optionally save as interactive HTML
            if save_html:
                html_path = os.path.join(output_dir, f"{name}.html")
                fig.write_html(html_path)
                print(f"✅ Saved {name}.html")
    
    def create_performance_comparison_chart(self, comparison_df: pd.DataFrame, 
                                          company_name: str = "Portfolio") -> go.Figure:
        """
        Create a line chart comparing portfolio performance with S&P 500
        
        Args:
            comparison_df: DataFrame with portfolio and S&P 500 performance data
            company_name: Name of the company/portfolio
            
        Returns:
            Plotly Figure object
        """
        fig = go.Figure()
        
        # Add portfolio line
        fig.add_trace(go.Scatter(
            x=comparison_df['date'],
            y=comparison_df['portfolio_normalized'],
            mode='lines+markers',
            name=company_name,
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=8),
            hovertemplate='<b>%{fullData.name}</b><br>' +
                         'Date: %{x}<br>' +
                         'Value: %{y:.2f}<br>' +
                         '<extra></extra>'
        ))
        
        # Add S&P 500 line
        fig.add_trace(go.Scatter(
            x=comparison_df['date'],
            y=comparison_df['sp500_normalized'],
            mode='lines+markers',
            name='S&P 500',
            line=dict(color='#ff7f0e', width=3),
            marker=dict(size=8),
            hovertemplate='<b>%{fullData.name}</b><br>' +
                         'Date: %{x}<br>' +
                         'Value: %{y:.2f}<br>' +
                         '<extra></extra>'
        ))
        
        # Update layout
        fig.update_layout(
            title={
                'text': f'{company_name} vs S&P 500 Performance Comparison',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20}
            },
            xaxis=dict(
                title='Date',
                tickformat='%Y-%m-%d',
                showgrid=True,
                gridwidth=1,
                gridcolor='lightgray'
            ),
            yaxis=dict(
                title='Normalized Value (Base 100)',
                showgrid=True,
                gridwidth=1,
                gridcolor='lightgray'
            ),
            hovermode='x unified',
            showlegend=True,
            legend=dict(
                x=0.02,
                y=0.98,
                xanchor='left',
                yanchor='top',
                bgcolor='rgba(255, 255, 255, 0.8)',
                bordercolor='black',
                borderwidth=1
            ),
            plot_bgcolor='white',
            height=600,
            width=1000
        )
        
        # Add annotation for final values
        if len(comparison_df) > 0:
            last_row = comparison_df.iloc[-1]
            portfolio_final = last_row['portfolio_normalized']
            sp500_final = last_row['sp500_normalized']
            
            # Determine which performed better
            if portfolio_final > sp500_final:
                annotation_text = f"{company_name} outperformed S&P 500 by {portfolio_final - sp500_final:.1f}%"
                annotation_color = 'green'
            else:
                annotation_text = f"S&P 500 outperformed {company_name} by {sp500_final - portfolio_final:.1f}%"
                annotation_color = 'red'
            
            fig.add_annotation(
                x=0.5,
                y=1.1,
                xref='paper',
                yref='paper',
                text=annotation_text,
                showarrow=False,
                font=dict(size=14, color=annotation_color),
                xanchor='center'
            )
        
        return fig
    
    def create_returns_comparison_chart(self, comparison_df: pd.DataFrame,
                                      company_name: str = "Portfolio") -> go.Figure:
        """
        Create a bar chart comparing quarterly returns
        
        Args:
            comparison_df: DataFrame with portfolio and S&P 500 performance data
            company_name: Name of the company/portfolio
            
        Returns:
            Plotly Figure object
        """
        # Filter out the first row (no return data)
        returns_df = comparison_df[comparison_df['portfolio_return'].notna()].copy()
        
        if len(returns_df) == 0:
            raise ValueError("Not enough data to create returns comparison")
        
        fig = go.Figure()
        
        # Add portfolio returns bars
        fig.add_trace(go.Bar(
            x=returns_df['date'],
            y=returns_df['portfolio_return'] * 100,
            name=company_name,
            marker_color='#1f77b4',
            opacity=0.8,
            hovertemplate='<b>%{fullData.name}</b><br>' +
                         'Date: %{x}<br>' +
                         'Return: %{y:.2f}%<br>' +
                         '<extra></extra>'
        ))
        
        # Add S&P 500 returns bars
        fig.add_trace(go.Bar(
            x=returns_df['date'],
            y=returns_df['sp500_return'] * 100,
            name='S&P 500',
            marker_color='#ff7f0e',
            opacity=0.8,
            hovertemplate='<b>%{fullData.name}</b><br>' +
                         'Date: %{x}<br>' +
                         'Return: %{y:.2f}%<br>' +
                         '<extra></extra>'
        ))
        
        # Update layout
        fig.update_layout(
            title={
                'text': 'Quarterly Returns Comparison',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20}
            },
            xaxis=dict(
                title='Quarter',
                tickformat='%Y-%m-%d'
            ),
            yaxis=dict(
                title='Return (%)',
                tickformat='.1f'
            ),
            barmode='group',
            showlegend=True,
            legend=dict(
                x=0.02,
                y=0.98,
                xanchor='left',
                yanchor='top'
            ),
            height=500,
            width=1000
        )
        
        # Add zero line
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
        
        return fig
    
    def create_risk_metrics_chart(self, metrics: Dict[str, float],
                                company_name: str = "Portfolio") -> go.Figure:
        """
        Create a comparison chart for risk metrics
        
        Args:
            metrics: Dictionary with risk metrics
            company_name: Name of the company/portfolio
            
        Returns:
            Plotly Figure object
        """
        # Prepare data for visualization
        metric_names = ['Total Return (%)', 'Volatility (%)', 'Sharpe Ratio']
        portfolio_values = [
            metrics.get('portfolio_total_return', 0),
            metrics.get('portfolio_volatility', 0) * 100,
            metrics.get('portfolio_sharpe', 0)
        ]
        sp500_values = [
            metrics.get('sp500_total_return', 0),
            metrics.get('sp500_volatility', 0) * 100,
            metrics.get('sp500_sharpe', 0)
        ]
        
        fig = go.Figure()
        
        # Add portfolio metrics
        fig.add_trace(go.Bar(
            x=metric_names,
            y=portfolio_values,
            name=company_name,
            marker_color='#1f77b4',
            text=[f'{v:.2f}' for v in portfolio_values],
            textposition='outside'
        ))
        
        # Add S&P 500 metrics
        fig.add_trace(go.Bar(
            x=metric_names,
            y=sp500_values,
            name='S&P 500',
            marker_color='#ff7f0e',
            text=[f'{v:.2f}' for v in sp500_values],
            textposition='outside'
        ))
        
        # Update layout
        fig.update_layout(
            title={
                'text': 'Risk-Adjusted Performance Metrics',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20}
            },
            xaxis=dict(title=''),
            yaxis=dict(title='Value'),
            barmode='group',
            showlegend=True,
            legend=dict(
                x=0.02,
                y=0.98,
                xanchor='left',
                yanchor='top'
            ),
            height=500,
            width=800
        )
        
        # Add beta as annotation if available
        if metrics.get('portfolio_beta') is not None:
            fig.add_annotation(
                x=0.5,
                y=1.05,
                xref='paper',
                yref='paper',
                text=f"Portfolio Beta: {metrics['portfolio_beta']:.2f}",
                showarrow=False,
                font=dict(size=14),
                xanchor='center'
            )
        
        return fig 