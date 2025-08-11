"""
Chart Embedding for Excel Export
High-resolution chart rendering and embedding for Excel workbooks

This module provides:
- Plotly chart rendering to high-resolution images
- Chart optimization for print and Excel display
- Multiple format support (PNG, JPEG, SVG)
- Chart sizing and layout optimization
- Batch chart processing for multiple visualizations

Repository: https://github.com/LT-aitools/rent-vs-buy-decision-tool
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import tempfile
import io
import base64

# Chart rendering imports
try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    import plotly.io as pio
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    logging.warning("Plotly not available - chart embedding will be limited")

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    logging.warning("Pandas not available - some chart data processing may be limited")

logger = logging.getLogger(__name__)


class ChartEmbedder:
    """
    Professional chart embedding system for Excel export
    
    Handles conversion of interactive Plotly charts to high-resolution
    images suitable for embedding in Excel workbooks.
    """
    
    def __init__(self):
        """Initialize chart embedder with optimal settings"""
        self.default_width = 1200
        self.default_height = 800
        self.default_dpi = 300
        self.supported_formats = ['png', 'jpeg', 'svg', 'pdf']
        
        # Configure Plotly settings for high-quality export
        if PLOTLY_AVAILABLE:
            pio.templates.default = "plotly_white"  # Clean template for professional output
            
        logger.info("ChartEmbedder initialized with high-resolution settings")
    
    async def render_all_charts(
        self, 
        export_data: Dict[str, Any], 
        resolution: int = 300,
        output_dir: Optional[Path] = None
    ) -> Dict[str, Path]:
        """
        Render all charts from export data to image files
        
        Args:
            export_data: Complete export data with analysis results
            resolution: Output resolution in DPI
            output_dir: Directory for output images (temp dir if None)
            
        Returns:
            Dictionary mapping chart names to image file paths
        """
        if not PLOTLY_AVAILABLE:
            logger.warning("Plotly not available - cannot render charts")
            return {}
        
        logger.info(f"Starting chart rendering at {resolution} DPI")
        
        # Set up output directory
        if output_dir is None:
            output_dir = Path(tempfile.mkdtemp()) / "charts"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Extract chart data
        chart_images = {}
        
        try:
            # Render NPV comparison chart
            npv_chart_path = await self.render_npv_comparison_chart(
                export_data, output_dir, resolution
            )
            if npv_chart_path:
                chart_images['npv_comparison'] = npv_chart_path
            
            # Render cash flow charts
            cash_flow_charts = await self.render_cash_flow_charts(
                export_data, output_dir, resolution
            )
            chart_images.update(cash_flow_charts)
            
            # Render financial metrics chart
            metrics_chart_path = await self.render_financial_metrics_chart(
                export_data, output_dir, resolution
            )
            if metrics_chart_path:
                chart_images['financial_metrics'] = metrics_chart_path
            
            # Render assumption sensitivity chart
            sensitivity_chart_path = await self.render_sensitivity_chart(
                export_data, output_dir, resolution
            )
            if sensitivity_chart_path:
                chart_images['sensitivity_analysis'] = sensitivity_chart_path
            
            logger.info(f"Successfully rendered {len(chart_images)} charts")
            
        except Exception as e:
            logger.error(f"Error during chart rendering: {str(e)}")
            raise
        
        return chart_images
    
    async def render_npv_comparison_chart(
        self,
        export_data: Dict[str, Any],
        output_dir: Path,
        resolution: int
    ) -> Optional[Path]:
        """Render NPV comparison bar chart"""
        
        try:
            analysis_results = export_data.get('analysis_results', {})
            
            ownership_npv = analysis_results.get('ownership_npv', 0)
            rental_npv = analysis_results.get('rental_npv', 0)
            
            # Create NPV comparison chart
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=['Ownership', 'Rental'],
                y=[ownership_npv, rental_npv],
                marker_color=['#FF6B6B' if ownership_npv > rental_npv else '#FFA07A', 
                             '#96CEB4' if rental_npv > ownership_npv else '#FECA57'],
                text=[f'${ownership_npv:,.0f}', f'${rental_npv:,.0f}'],
                textposition='auto',
                name='NPV Comparison'
            ))
            
            fig.update_layout(
                title={
                    'text': 'Net Present Value Comparison',
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 24, 'family': 'Arial, sans-serif'}
                },
                xaxis_title='Scenario',
                yaxis_title='Net Present Value ($)',
                yaxis_tickformat='$,.0f',
                font={'size': 14, 'family': 'Arial, sans-serif'},
                plot_bgcolor='white',
                paper_bgcolor='white',
                showlegend=False,
                margin=dict(l=80, r=80, t=100, b=80)
            )
            
            # Add recommendation annotation
            recommendation = analysis_results.get('recommendation', 'UNKNOWN')
            if recommendation != 'UNKNOWN':
                fig.add_annotation(
                    text=f"Recommendation: {recommendation}",
                    xref="paper", yref="paper",
                    x=0.5, y=0.95,
                    showarrow=False,
                    font=dict(size=16, color="darkgreen" if recommendation == "BUY" else "darkorange"),
                    bgcolor="rgba(255,255,255,0.8)",
                    bordercolor="gray",
                    borderwidth=1
                )
            
            # Save chart
            output_path = output_dir / "npv_comparison.png"
            await self._save_chart(fig, output_path, resolution)
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error rendering NPV comparison chart: {str(e)}")
            return None
    
    async def render_cash_flow_charts(
        self,
        export_data: Dict[str, Any],
        output_dir: Path,
        resolution: int
    ) -> Dict[str, Path]:
        """Render cash flow analysis charts"""
        
        chart_paths = {}
        
        try:
            ownership_flows = export_data.get('ownership_flows', {})
            rental_flows = export_data.get('rental_flows', {})
            
            # Handle both list and dict formats for cash flows
            ownership_annual = self._extract_cash_flows(ownership_flows)
            rental_annual = self._extract_cash_flows(rental_flows)
            
            if not ownership_annual or not rental_annual:
                logger.warning("Insufficient cash flow data for chart rendering")
                return chart_paths
            
            # Ensure both arrays are same length
            max_years = max(len(ownership_annual), len(rental_annual))
            years = list(range(1, max_years + 1))
            
            # Annual cash flows comparison
            annual_fig = go.Figure()
            
            annual_fig.add_trace(go.Scatter(
                x=years,
                y=ownership_annual[:max_years],
                mode='lines+markers',
                name='Ownership',
                line=dict(color='#FF6B6B', width=3),
                marker=dict(size=6)
            ))
            
            annual_fig.add_trace(go.Scatter(
                x=years,
                y=rental_annual[:max_years],
                mode='lines+markers',
                name='Rental',
                line=dict(color='#74B9FF', width=3),
                marker=dict(size=6)
            ))
            
            annual_fig.update_layout(
                title={
                    'text': 'Annual Cash Flow Comparison',
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 20, 'family': 'Arial, sans-serif'}
                },
                xaxis_title='Year',
                yaxis_title='Annual Cash Flow ($)',
                yaxis_tickformat='$,.0f',
                font={'size': 12, 'family': 'Arial, sans-serif'},
                plot_bgcolor='white',
                paper_bgcolor='white',
                legend=dict(x=0.02, y=0.98),
                margin=dict(l=80, r=80, t=100, b=80)
            )
            
            # Save annual cash flows chart
            annual_path = output_dir / "annual_cash_flows.png"
            await self._save_chart(annual_fig, annual_path, resolution)
            chart_paths['annual_cash_flows'] = annual_path
            
            # Cumulative cash flows
            ownership_cumulative = [sum(ownership_annual[:i+1]) for i in range(len(ownership_annual))]
            rental_cumulative = [sum(rental_annual[:i+1]) for i in range(len(rental_annual))]
            
            cumulative_fig = go.Figure()
            
            cumulative_fig.add_trace(go.Scatter(
                x=years,
                y=ownership_cumulative[:max_years],
                mode='lines+markers',
                name='Ownership (Cumulative)',
                line=dict(color='#FF6B6B', width=3),
                marker=dict(size=6),
                fill='tonexty' if len(chart_paths) == 0 else None
            ))
            
            cumulative_fig.add_trace(go.Scatter(
                x=years,
                y=rental_cumulative[:max_years],
                mode='lines+markers',
                name='Rental (Cumulative)',
                line=dict(color='#74B9FF', width=3),
                marker=dict(size=6)
            ))
            
            cumulative_fig.update_layout(
                title={
                    'text': 'Cumulative Cash Flow Comparison',
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 20, 'family': 'Arial, sans-serif'}
                },
                xaxis_title='Year',
                yaxis_title='Cumulative Cash Flow ($)',
                yaxis_tickformat='$,.0f',
                font={'size': 12, 'family': 'Arial, sans-serif'},
                plot_bgcolor='white',
                paper_bgcolor='white',
                legend=dict(x=0.02, y=0.98),
                margin=dict(l=80, r=80, t=100, b=80)
            )
            
            # Save cumulative cash flows chart
            cumulative_path = output_dir / "cumulative_cash_flows.png"
            await self._save_chart(cumulative_fig, cumulative_path, resolution)
            chart_paths['cumulative_cash_flows'] = cumulative_path
            
        except Exception as e:
            logger.error(f"Error rendering cash flow charts: {str(e)}")
        
        return chart_paths
    
    async def render_financial_metrics_chart(
        self,
        export_data: Dict[str, Any],
        output_dir: Path,
        resolution: int
    ) -> Optional[Path]:
        """Render key financial metrics comparison chart"""
        
        try:
            analysis_results = export_data.get('analysis_results', {})
            
            # Extract key metrics
            metrics = {
                'NPV': {
                    'Ownership': analysis_results.get('ownership_npv', 0),
                    'Rental': analysis_results.get('rental_npv', 0)
                },
                'Initial Investment': {
                    'Ownership': analysis_results.get('ownership_initial_investment', 0),
                    'Rental': analysis_results.get('rental_initial_investment', 0)
                },
                'IRR': {
                    'Ownership': analysis_results.get('ownership_irr', 0) * 100,  # Convert to percentage
                    'Rental': analysis_results.get('rental_irr', 0) * 100
                }
            }
            
            # Create subplots for different metrics
            fig = make_subplots(
                rows=1, cols=3,
                subplot_titles=('Net Present Value', 'Initial Investment', 'Internal Rate of Return'),
                specs=[[{"secondary_y": False}, {"secondary_y": False}, {"secondary_y": False}]]
            )
            
            # NPV comparison
            fig.add_trace(
                go.Bar(x=['Ownership', 'Rental'], 
                      y=[metrics['NPV']['Ownership'], metrics['NPV']['Rental']],
                      marker_color=['#FF6B6B', '#74B9FF'],
                      name='NPV',
                      showlegend=False),
                row=1, col=1
            )
            
            # Initial Investment comparison
            fig.add_trace(
                go.Bar(x=['Ownership', 'Rental'],
                      y=[metrics['Initial Investment']['Ownership'], metrics['Initial Investment']['Rental']],
                      marker_color=['#FFA07A', '#96CEB4'],
                      name='Investment',
                      showlegend=False),
                row=1, col=2
            )
            
            # IRR comparison
            fig.add_trace(
                go.Bar(x=['Ownership', 'Rental'],
                      y=[metrics['IRR']['Ownership'], metrics['IRR']['Rental']],
                      marker_color=['#FECA57', '#DDA0DD'],
                      name='IRR',
                      showlegend=False),
                row=1, col=3
            )
            
            # Update layout
            fig.update_layout(
                title={
                    'text': 'Key Financial Metrics Comparison',
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 20, 'family': 'Arial, sans-serif'}
                },
                font={'size': 10, 'family': 'Arial, sans-serif'},
                plot_bgcolor='white',
                paper_bgcolor='white',
                margin=dict(l=60, r=60, t=100, b=60),
                height=500
            )
            
            # Update y-axes
            fig.update_yaxes(title_text="Amount ($)", tickformat="$,.0f", row=1, col=1)
            fig.update_yaxes(title_text="Amount ($)", tickformat="$,.0f", row=1, col=2)
            fig.update_yaxes(title_text="Rate (%)", tickformat=".1f", row=1, col=3)
            
            # Save chart
            output_path = output_dir / "financial_metrics.png"
            await self._save_chart(fig, output_path, resolution)
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error rendering financial metrics chart: {str(e)}")
            return None
    
    async def render_sensitivity_chart(
        self,
        export_data: Dict[str, Any],
        output_dir: Path,
        resolution: int
    ) -> Optional[Path]:
        """Render sensitivity analysis chart (placeholder for future implementation)"""
        
        try:
            # For now, create a simple placeholder chart
            # Future implementation would analyze sensitivity to key parameters
            
            analysis_results = export_data.get('analysis_results', {})
            
            # Create a simple tornado chart showing impact of key assumptions
            parameters = ['Interest Rate', 'Rent Growth', 'Property Tax', 'Maintenance Costs', 'Cost of Capital']
            low_impact = [-150000, -75000, -50000, -40000, -100000]  # Placeholder values
            high_impact = [100000, 125000, 60000, 45000, 120000]     # Placeholder values
            
            fig = go.Figure()
            
            # Add bars for negative impact (left side)
            fig.add_trace(go.Bar(
                y=parameters,
                x=low_impact,
                orientation='h',
                name='Downside Impact',
                marker_color='#FF7675',
                text=[f'${abs(x):,.0f}' for x in low_impact],
                textposition='inside'
            ))
            
            # Add bars for positive impact (right side)
            fig.add_trace(go.Bar(
                y=parameters,
                x=high_impact,
                orientation='h',
                name='Upside Impact',
                marker_color='#96CEB4',
                text=[f'${x:,.0f}' for x in high_impact],
                textposition='inside'
            ))
            
            fig.update_layout(
                title={
                    'text': 'NPV Sensitivity to Key Assumptions',
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 20, 'family': 'Arial, sans-serif'}
                },
                xaxis_title='NPV Impact ($)',
                xaxis_tickformat='$,.0f',
                font={'size': 12, 'family': 'Arial, sans-serif'},
                plot_bgcolor='white',
                paper_bgcolor='white',
                barmode='relative',
                legend=dict(x=0.7, y=0.1),
                margin=dict(l=120, r=80, t=100, b=80),
                height=400
            )
            
            # Add vertical line at x=0
            fig.add_vline(x=0, line_dash="dash", line_color="gray")
            
            # Save chart
            output_path = output_dir / "sensitivity_analysis.png"
            await self._save_chart(fig, output_path, resolution)
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error rendering sensitivity chart: {str(e)}")
            return None
    
    async def _save_chart(
        self, 
        fig: go.Figure, 
        output_path: Path, 
        resolution: int,
        format: str = 'png'
    ) -> None:
        """
        Save Plotly figure to file with specified resolution
        
        Args:
            fig: Plotly figure to save
            output_path: Path for output file
            resolution: Resolution in DPI
            format: Output format (png, jpeg, svg, pdf)
        """
        try:
            # Calculate pixel dimensions based on DPI
            # Standard size: 12x8 inches at specified DPI
            width_px = int(12 * resolution)
            height_px = int(8 * resolution)
            
            if format.lower() == 'png':
                fig.write_image(
                    str(output_path),
                    format='png',
                    width=width_px,
                    height=height_px,
                    scale=1  # Don't double-scale since we're setting pixel dimensions
                )
            elif format.lower() == 'jpeg':
                fig.write_image(
                    str(output_path),
                    format='jpeg',
                    width=width_px,
                    height=height_px,
                    scale=1
                )
            elif format.lower() == 'svg':
                fig.write_image(
                    str(output_path),
                    format='svg',
                    width=width_px,
                    height=height_px
                )
            else:
                # Default to PNG
                fig.write_image(
                    str(output_path),
                    format='png',
                    width=width_px,
                    height=height_px,
                    scale=1
                )
            
            logger.debug(f"Chart saved: {output_path}")
            
        except Exception as e:
            logger.error(f"Error saving chart to {output_path}: {str(e)}")
            raise
    
    def get_chart_info(self, chart_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get information about charts that can be generated
        
        Args:
            chart_data: Chart data from export package
            
        Returns:
            Information about available charts
        """
        available_charts = {
            'npv_comparison': {
                'name': 'NPV Comparison',
                'description': 'Bar chart comparing NPV of ownership vs rental',
                'required_data': ['ownership_npv', 'rental_npv'],
                'chart_type': 'bar'
            },
            'annual_cash_flows': {
                'name': 'Annual Cash Flows',
                'description': 'Line chart showing annual cash flows over time',
                'required_data': ['ownership_flows.annual_cash_flows', 'rental_flows.annual_cash_flows'],
                'chart_type': 'line'
            },
            'cumulative_cash_flows': {
                'name': 'Cumulative Cash Flows',
                'description': 'Line chart showing cumulative cash flows over time',
                'required_data': ['ownership_flows.annual_cash_flows', 'rental_flows.annual_cash_flows'],
                'chart_type': 'line'
            },
            'financial_metrics': {
                'name': 'Financial Metrics',
                'description': 'Multi-panel comparison of key financial metrics',
                'required_data': ['ownership_npv', 'rental_npv', 'ownership_irr', 'rental_irr'],
                'chart_type': 'subplot'
            },
            'sensitivity_analysis': {
                'name': 'Sensitivity Analysis',
                'description': 'Tornado chart showing NPV sensitivity to assumptions',
                'required_data': ['analysis_results'],
                'chart_type': 'tornado'
            }
        }
        
        return {
            'available_charts': available_charts,
            'total_charts': len(available_charts),
            'plotly_available': PLOTLY_AVAILABLE,
            'supported_formats': self.supported_formats
        }
    
    def _extract_cash_flows(self, flows_data: Any) -> List[float]:
        """
        Extract cash flow values from either list or dict format
        
        Args:
            flows_data: Either a list of flow dicts or a dict with 'annual_cash_flows' key
            
        Returns:
            List of cash flow values
        """
        if isinstance(flows_data, list):
            # List of flow dictionaries - extract 'net_cash_flow' values
            return [
                flow.get('net_cash_flow', 0) if isinstance(flow, dict) else float(flow)
                for flow in flows_data
            ]
        elif isinstance(flows_data, dict):
            if 'annual_cash_flows' in flows_data:
                # Dictionary format with 'annual_cash_flows' key
                annual_flows = flows_data['annual_cash_flows']
                if isinstance(annual_flows, list):
                    return [float(flow) for flow in annual_flows]
            # If dict doesn't have expected structure, return empty list
            return []
        else:
            # Unsupported format
            return []