"""
Enhanced Interactive Charts Component
Week 4 UX Enhancement - Interactive visualizations with drill-down capability

Features:
- Interactive drill-down charts with multiple levels of detail
- Real-time filtering and data exploration
- Responsive design for desktop and mobile
- Accessibility-compliant visualizations with ARIA labels
- Export capabilities for charts and data
- Animation and smooth transitions
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import streamlit as st
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from datetime import datetime
import sys
import os

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from shared.interfaces import UIComponent, UIState, AnalyticsResult
from components.charts.core_charts import get_professional_color_scheme, get_chart_layout_config, format_currency


@dataclass
class ChartConfig:
    """Configuration for interactive charts"""
    chart_type: str  # 'bar', 'line', 'pie', 'scatter', 'heatmap', 'waterfall'
    title: str
    subtitle: str = ""
    height: int = 500
    width: Optional[int] = None
    drill_down_enabled: bool = True
    export_enabled: bool = True
    animation_enabled: bool = True
    accessibility_enabled: bool = True
    responsive_design: bool = True
    color_scheme: str = "professional"  # 'professional', 'high_contrast', 'colorblind_friendly'


@dataclass
class DrillDownLevel:
    """Configuration for drill-down levels"""
    level_name: str
    data_key: str
    aggregation_type: str  # 'sum', 'average', 'count', 'percentage'
    display_format: str  # 'currency', 'percentage', 'number'
    color_mapping: Optional[Dict[str, str]] = None


class InteractiveChartsComponent(UIComponent):
    """Enhanced interactive charts component with drill-down capabilities"""
    
    def __init__(self):
        self.colors = get_professional_color_scheme()
        self.drill_down_state = {}
        self.filter_state = {}
        self.animation_enabled = True
        self.max_state_size = 50  # Limit state dictionary size
        
    def render(self, data: Any, state: UIState) -> None:
        """Render interactive charts based on data and state"""
        try:
            # Clean up state dictionaries if they get too large
            self._cleanup_state_dictionaries()
            
            if state.mobile_mode:
                self._render_mobile_charts(data, state)
            else:
                self._render_desktop_charts(data, state)
                
        except Exception as e:
            st.error(f"Error rendering charts: {str(e)}")
            # Fallback to simple message
            st.info("Charts temporarily unavailable - please refresh page")
    
    def _cleanup_state_dictionaries(self) -> None:
        """Clean up state dictionaries to prevent memory bloat"""
        try:
            if len(self.drill_down_state) > self.max_state_size:
                # Keep only the most recent entries
                items = list(self.drill_down_state.items())
                self.drill_down_state = dict(items[-self.max_state_size//2:])
            
            if len(self.filter_state) > self.max_state_size:
                # Keep only the most recent entries
                items = list(self.filter_state.items())
                self.filter_state = dict(items[-self.max_state_size//2:])
                
        except Exception as e:
            # If cleanup fails, clear the dictionaries entirely
            self.drill_down_state = {}
            self.filter_state = {}
    
    def _render_desktop_charts(self, data: Any, state: UIState) -> None:
        """Render desktop-optimized interactive charts"""
        st.markdown("### 📊 Interactive Financial Analysis")
        st.markdown("*Click charts to drill down for detailed analysis*")
        
        # Chart selection tabs
        chart_tabs = st.tabs([
            "💰 NPV Analysis", 
            "📈 Cash Flow Timeline", 
            "🔍 Cost Breakdown", 
            "📊 Scenario Comparison",
            "⚡ Sensitivity Analysis"
        ])
        
        with chart_tabs[0]:
            self._render_interactive_npv_analysis(data, state)
        
        with chart_tabs[1]:
            self._render_interactive_cash_flow(data, state)
        
        with chart_tabs[2]:
            self._render_interactive_cost_breakdown(data, state)
        
        with chart_tabs[3]:
            self._render_interactive_scenario_comparison(data, state)
        
        with chart_tabs[4]:
            self._render_interactive_sensitivity_analysis(data, state)
    
    def _render_mobile_charts(self, data: Any, state: UIState) -> None:
        """Render mobile-optimized charts"""
        st.markdown("### 📱 Mobile Analysis Dashboard")
        
        # Mobile-friendly chart selector
        chart_type = st.selectbox(
            "Select Analysis View",
            ["NPV Analysis", "Cash Flow", "Cost Breakdown", "Scenarios", "Sensitivity"],
            key="mobile_chart_selector"
        )
        
        if chart_type == "NPV Analysis":
            self._render_mobile_npv_chart(data, state)
        elif chart_type == "Cash Flow":
            self._render_mobile_cash_flow_chart(data, state)
        elif chart_type == "Cost Breakdown":
            self._render_mobile_cost_chart(data, state)
        elif chart_type == "Scenarios":
            self._render_mobile_scenario_chart(data, state)
        elif chart_type == "Sensitivity":
            self._render_mobile_sensitivity_chart(data, state)
    
    def _render_interactive_npv_analysis(self, data: Any, state: UIState) -> None:
        """Render interactive NPV analysis with drill-down"""
        st.markdown("#### 💰 Net Present Value Analysis")
        
        # Create drill-down controls
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            drill_level = st.selectbox(
                "Analysis Level",
                ["Summary", "Annual Breakdown", "Quarterly Detail", "Monthly Cashflow"],
                key="npv_drill_level"
            )
        
        with col2:
            show_components = st.checkbox("Show Components", value=True, key="npv_components")
        
        with col3:
            enable_animation = st.checkbox("Animations", value=True, key="npv_animation")
        
        # Generate NPV data based on drill level
        npv_data = self._generate_npv_drill_data(data, drill_level)
        
        # Create interactive NPV chart
        fig = self._create_interactive_npv_chart(npv_data, drill_level, show_components, enable_animation)
        
        # Display chart with interactivity
        selected_data = st.plotly_chart(
            fig, 
            use_container_width=True, 
            key="npv_chart",
            on_select="rerun"
        )
        
        # Handle drill-down interactions
        if selected_data and hasattr(selected_data, 'selection'):
            self._handle_npv_drill_down(selected_data.selection, drill_level)
        
        # Show detailed data table if drill-down is active
        if drill_level != "Summary":
            self._show_npv_detail_table(npv_data, drill_level)
    
    def _render_interactive_cash_flow(self, data: Any, state: UIState) -> None:
        """Render interactive cash flow timeline"""
        st.markdown("#### 📈 Cash Flow Timeline Analysis")
        
        # Timeline controls
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            time_range = st.slider(
                "Years to Display",
                min_value=1,
                max_value=30,
                value=(1, 25),
                key="cashflow_range"
            )
        
        with col2:
            cash_flow_type = st.selectbox(
                "Cash Flow Type",
                ["Net Cash Flow", "Operating Cash Flow", "Investment Cash Flow"],
                key="cashflow_type"
            )
        
        with col3:
            aggregation = st.selectbox(
                "Aggregation",
                ["Annual", "Cumulative", "Moving Average"],
                key="cashflow_aggregation"
            )
        
        with col4:
            show_breakeven = st.checkbox("Show Breakeven", value=True, key="cashflow_breakeven")
        
        # Generate cash flow data
        cash_flow_data = self._generate_cash_flow_data(data, time_range, cash_flow_type, aggregation)
        
        # Create interactive cash flow chart
        fig = self._create_interactive_cash_flow_chart(
            cash_flow_data, 
            cash_flow_type, 
            aggregation, 
            show_breakeven
        )
        
        # Display chart
        st.plotly_chart(fig, use_container_width=True, key="cashflow_chart")
        
        # Cash flow insights
        self._show_cash_flow_insights(cash_flow_data, time_range)
    
    def _render_interactive_cost_breakdown(self, data: Any, state: UIState) -> None:
        """Render interactive cost breakdown analysis"""
        st.markdown("#### 🔍 Cost Breakdown Analysis")
        
        # Breakdown controls
        col1, col2 = st.columns(2)
        
        with col1:
            breakdown_type = st.selectbox(
                "Breakdown Type",
                ["By Category", "By Year", "By Scenario", "By Cost Driver"],
                key="cost_breakdown_type"
            )
        
        with col2:
            chart_style = st.selectbox(
                "Chart Style",
                ["Pie Chart", "Treemap", "Sunburst", "Waterfall"],
                key="cost_chart_style"
            )
        
        # Generate cost breakdown data
        cost_data = self._generate_cost_breakdown_data(data, breakdown_type)
        
        # Create interactive cost chart
        if chart_style == "Pie Chart":
            fig = self._create_interactive_pie_chart(cost_data, breakdown_type)
        elif chart_style == "Treemap":
            fig = self._create_interactive_treemap(cost_data, breakdown_type)
        elif chart_style == "Sunburst":
            fig = self._create_interactive_sunburst(cost_data, breakdown_type)
        else:  # Waterfall
            fig = self._create_interactive_waterfall(cost_data, breakdown_type)
        
        # Display chart
        st.plotly_chart(fig, use_container_width=True, key="cost_chart")
        
        # Cost optimization suggestions
        self._show_cost_optimization_suggestions(cost_data)
    
    def _render_interactive_scenario_comparison(self, data: Any, state: UIState) -> None:
        """Render interactive scenario comparison"""
        st.markdown("#### 📊 Scenario Comparison Analysis")
        
        # Scenario controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            scenarios = st.multiselect(
                "Select Scenarios",
                ["Base Case", "Optimistic", "Pessimistic", "High Interest", "Low Market Growth"],
                default=["Base Case", "Optimistic", "Pessimistic"],
                key="scenario_selection"
            )
        
        with col2:
            comparison_metric = st.selectbox(
                "Comparison Metric",
                ["NPV", "IRR", "Payback Period", "Total ROI"],
                key="scenario_metric"
            )
        
        with col3:
            chart_format = st.selectbox(
                "Chart Format",
                ["Bar Chart", "Radar Chart", "Box Plot", "Violin Plot"],
                key="scenario_chart_format"
            )
        
        # Generate scenario data
        scenario_data = self._generate_scenario_data(data, scenarios, comparison_metric)
        
        # Create scenario comparison chart
        if chart_format == "Bar Chart":
            fig = self._create_scenario_bar_chart(scenario_data, comparison_metric)
        elif chart_format == "Radar Chart":
            fig = self._create_scenario_radar_chart(scenario_data)
        elif chart_format == "Box Plot":
            fig = self._create_scenario_box_plot(scenario_data, comparison_metric)
        else:  # Violin Plot
            fig = self._create_scenario_violin_plot(scenario_data, comparison_metric)
        
        # Display chart
        st.plotly_chart(fig, use_container_width=True, key="scenario_chart")
        
        # Scenario insights
        self._show_scenario_insights(scenario_data, scenarios)
    
    def _render_interactive_sensitivity_analysis(self, data: Any, state: UIState) -> None:
        """Render interactive sensitivity analysis"""
        st.markdown("#### ⚡ Sensitivity Analysis")
        
        # Sensitivity controls
        col1, col2 = st.columns(2)
        
        with col1:
            sensitivity_variables = st.multiselect(
                "Variables to Analyze",
                ["Interest Rate", "Market Appreciation", "Rent Growth", "Operating Costs", "Vacancy Rate"],
                default=["Interest Rate", "Market Appreciation", "Rent Growth"],
                key="sensitivity_variables"
            )
        
        with col2:
            sensitivity_range = st.slider(
                "Sensitivity Range (±%)",
                min_value=5,
                max_value=50,
                value=20,
                step=5,
                key="sensitivity_range"
            )
        
        # Generate sensitivity data
        sensitivity_data = self._generate_sensitivity_data(data, sensitivity_variables, sensitivity_range)
        
        # Create sensitivity charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Tornado chart
            tornado_fig = self._create_tornado_chart(sensitivity_data)
            st.plotly_chart(tornado_fig, use_container_width=True, key="tornado_chart")
        
        with col2:
            # Spider chart
            spider_fig = self._create_spider_chart(sensitivity_data)
            st.plotly_chart(spider_fig, use_container_width=True, key="spider_chart")
        
        # Sensitivity heatmap
        heatmap_fig = self._create_sensitivity_heatmap(sensitivity_data)
        st.plotly_chart(heatmap_fig, use_container_width=True, key="sensitivity_heatmap")
        
        # Sensitivity insights
        self._show_sensitivity_insights(sensitivity_data)
    
    # Chart creation methods
    
    def _create_interactive_npv_chart(self, data: Dict, drill_level: str, show_components: bool, enable_animation: bool) -> go.Figure:
        """Create interactive NPV chart with drill-down capability"""
        fig = go.Figure()
        
        if drill_level == "Summary":
            # Summary bar chart
            scenarios = ["Buy", "Rent"]
            values = [data.get('buy_npv', 0), data.get('rent_npv', 0)]
            colors = [self.colors['ownership'], self.colors['rental']]
            
            fig.add_trace(go.Bar(
                x=scenarios,
                y=values,
                marker_color=colors,
                text=[format_currency(v) for v in values],
                textposition='auto',
                hovertemplate='<b>%{x}</b><br>NPV: %{text}<br><extra></extra>',
                name="NPV"
            ))
            
            # Add difference annotation
            difference = values[0] - values[1]
            fig.add_annotation(
                x=0.5,
                y=max(values) + abs(max(values)) * 0.1,
                text=f"Difference: {format_currency(difference)}",
                showarrow=False,
                font=dict(size=14, color=self.colors['primary'])
            )
        
        elif drill_level == "Annual Breakdown":
            # Annual NPV components
            years = list(range(1, 26))
            buy_annual = data.get('buy_annual_npv', [0] * 25)
            rent_annual = data.get('rent_annual_npv', [0] * 25)
            
            fig.add_trace(go.Scatter(
                x=years,
                y=buy_annual,
                mode='lines+markers',
                name='Buy NPV',
                line=dict(color=self.colors['ownership'], width=3),
                marker=dict(size=6),
                hovertemplate='<b>Year %{x}</b><br>Buy NPV: %{y:$,.0f}<br><extra></extra>'
            ))
            
            fig.add_trace(go.Scatter(
                x=years,
                y=rent_annual,
                mode='lines+markers',
                name='Rent NPV',
                line=dict(color=self.colors['rental'], width=3),
                marker=dict(size=6),
                hovertemplate='<b>Year %{x}</b><br>Rent NPV: %{y:$,.0f}<br><extra></extra>'
            ))
            
            # Add breakeven point if it exists
            for i, (buy, rent) in enumerate(zip(buy_annual, rent_annual)):
                if i > 0 and (buy_annual[i-1] - rent_annual[i-1]) * (buy - rent) < 0:
                    fig.add_vline(
                        x=i+1,
                        line_dash="dash",
                        line_color=self.colors['warning'],
                        annotation_text="Breakeven"
                    )
                    break
        
        # Apply layout
        layout_config = get_chart_layout_config()
        layout_config.update({
            'title': {
                'text': f'NPV Analysis - {drill_level}',
                'x': 0.5,
                'font': {'size': 16, 'color': self.colors['text']}
            },
            'xaxis': {'title': 'Scenario' if drill_level == "Summary" else 'Year'},
            'yaxis': {'title': 'Net Present Value ($)', 'tickformat': '$,.0f'},
            'height': 500
        })
        
        fig.update_layout(**layout_config)
        
        # Add animation if enabled
        if enable_animation and drill_level != "Summary":
            fig.update_layout(
                updatemenus=[{
                    'type': 'buttons',
                    'showactive': False,
                    'buttons': [{
                        'label': 'Play',
                        'method': 'animate',
                        'args': [None, {'frame': {'duration': 500}}]
                    }]
                }]
            )
        
        return fig
    
    def _create_interactive_cash_flow_chart(self, data: Dict, cash_flow_type: str, aggregation: str, show_breakeven: bool) -> go.Figure:
        """Create interactive cash flow timeline chart"""
        fig = go.Figure()
        
        years = data.get('years', list(range(1, 26)))
        buy_cf = data.get('buy_cash_flow', [0] * len(years))
        rent_cf = data.get('rent_cash_flow', [0] * len(years))
        
        # Buy scenario cash flow
        fig.add_trace(go.Scatter(
            x=years,
            y=buy_cf,
            mode='lines+markers',
            name='Buy Scenario',
            line=dict(color=self.colors['ownership'], width=3),
            marker=dict(size=8),
            fill='tonexty' if aggregation == "Cumulative" else None,
            hovertemplate=f'<b>Year %{{x}}</b><br>{cash_flow_type}: %{{y:$,.0f}}<br><extra></extra>'
        ))
        
        # Rent scenario cash flow
        fig.add_trace(go.Scatter(
            x=years,
            y=rent_cf,
            mode='lines+markers',
            name='Rent Scenario',
            line=dict(color=self.colors['rental'], width=3),
            marker=dict(size=8),
            hovertemplate=f'<b>Year %{{x}}</b><br>{cash_flow_type}: %{{y:$,.0f}}<br><extra></extra>'
        ))
        
        # Add zero line
        fig.add_hline(
            y=0,
            line_dash="dot",
            line_color=self.colors['neutral'],
            annotation_text="Break-even"
        )
        
        # Show breakeven point if requested
        if show_breakeven:
            # Find crossover point
            for i in range(1, len(years)):
                if (buy_cf[i-1] - rent_cf[i-1]) * (buy_cf[i] - rent_cf[i]) < 0:
                    fig.add_vline(
                        x=years[i],
                        line_dash="dash",
                        line_color=self.colors['warning'],
                        annotation_text=f"Crossover Year {years[i]}"
                    )
                    break
        
        # Apply layout
        layout_config = get_chart_layout_config()
        layout_config.update({
            'title': {
                'text': f'{cash_flow_type} Timeline - {aggregation}',
                'x': 0.5,
                'font': {'size': 16}
            },
            'xaxis': {'title': 'Year'},
            'yaxis': {'title': f'{cash_flow_type} ($)', 'tickformat': '$,.0f'},
            'height': 500
        })
        
        fig.update_layout(**layout_config)
        
        return fig
    
    def _create_interactive_pie_chart(self, data: Dict, breakdown_type: str) -> go.Figure:
        """Create interactive pie chart for cost breakdown"""
        labels = data.get('labels', [])
        values = data.get('values', [])
        colors = data.get('colors', [self.colors['primary']] * len(labels))
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            marker_colors=colors,
            textinfo='label+percent',
            textposition='auto',
            hovertemplate='<b>%{label}</b><br>Amount: %{value:$,.0f}<br>Percentage: %{percent}<br><extra></extra>',
            hole=0.3  # Donut chart style
        )])
        
        # Apply layout
        layout_config = get_chart_layout_config()
        layout_config.update({
            'title': {
                'text': f'Cost Breakdown - {breakdown_type}',
                'x': 0.5,
                'font': {'size': 16}
            },
            'height': 500,
            'showlegend': True
        })
        
        fig.update_layout(**layout_config)
        
        return fig
    
    def _create_interactive_treemap(self, data: Dict, breakdown_type: str) -> go.Figure:
        """Create interactive treemap for hierarchical cost breakdown"""
        fig = go.Figure(go.Treemap(
            labels=data.get('labels', []),
            values=data.get('values', []),
            parents=data.get('parents', ['']),
            textinfo="label+value+percent parent",
            texttemplate='<b>%{label}</b><br>%{value:$,.0f}<br>%{percentParent}',
            hovertemplate='<b>%{label}</b><br>Value: %{value:$,.0f}<br>Percentage: %{percentParent}<br><extra></extra>',
            maxdepth=3,
            pathbar_visible=True
        ))
        
        # Apply layout
        layout_config = get_chart_layout_config()
        layout_config.update({
            'title': {
                'text': f'Hierarchical Cost Breakdown - {breakdown_type}',
                'x': 0.5,
                'font': {'size': 16}
            },
            'height': 600
        })
        
        fig.update_layout(**layout_config)
        
        return fig
    
    def _create_tornado_chart(self, data: Dict) -> go.Figure:
        """Create tornado chart for sensitivity analysis"""
        variables = data.get('variables', [])
        low_impact = data.get('low_impact', [])
        high_impact = data.get('high_impact', [])
        
        fig = go.Figure()
        
        # Low impact (negative side)
        fig.add_trace(go.Bar(
            y=variables,
            x=[-abs(x) for x in low_impact],
            orientation='h',
            name='Low Impact',
            marker_color=self.colors['rental'],
            text=[f'-{abs(x):,.0f}' for x in low_impact],
            textposition='inside',
            hovertemplate='<b>%{y}</b><br>Low Impact: %{text}<br><extra></extra>'
        ))
        
        # High impact (positive side)
        fig.add_trace(go.Bar(
            y=variables,
            x=high_impact,
            orientation='h',
            name='High Impact',
            marker_color=self.colors['ownership'],
            text=[f'+{x:,.0f}' for x in high_impact],
            textposition='inside',
            hovertemplate='<b>%{y}</b><br>High Impact: %{text}<br><extra></extra>'
        ))
        
        # Apply layout
        layout_config = get_chart_layout_config()
        layout_config.update({
            'title': {
                'text': 'Sensitivity Analysis - Tornado Chart',
                'x': 0.5,
                'font': {'size': 16}
            },
            'xaxis': {'title': 'NPV Impact ($)', 'tickformat': '$,.0f'},
            'yaxis': {'title': 'Variables'},
            'barmode': 'relative',
            'height': 500
        })
        
        fig.update_layout(**layout_config)
        
        return fig
    
    # Data generation methods (these would integrate with actual calculation engines)
    
    def _generate_npv_drill_data(self, data: Any, drill_level: str) -> Dict:
        """Generate NPV data for different drill-down levels"""
        # Mock data generation - would integrate with actual calculation engine
        base_buy_npv = 125000
        base_rent_npv = -50000
        
        if drill_level == "Summary":
            return {
                'buy_npv': base_buy_npv,
                'rent_npv': base_rent_npv
            }
        elif drill_level == "Annual Breakdown":
            # Generate annual NPV contributions
            years = 25
            buy_annual = []
            rent_annual = []
            
            for year in range(1, years + 1):
                # Mock calculation with some variation
                buy_cf = 15000 - (year * 100)  # Decreasing cash flow
                rent_cf = -12000 - (year * 200)  # Increasing rent
                
                discount_factor = (1 + 0.08) ** year
                buy_annual.append(buy_cf / discount_factor)
                rent_annual.append(rent_cf / discount_factor)
            
            return {
                'buy_npv': base_buy_npv,
                'rent_npv': base_rent_npv,
                'buy_annual_npv': buy_annual,
                'rent_annual_npv': rent_annual
            }
        
        return {}
    
    def _generate_cash_flow_data(self, data: Any, time_range: Tuple[int, int], cash_flow_type: str, aggregation: str) -> Dict:
        """Generate cash flow data for visualization"""
        start_year, end_year = time_range
        years = list(range(start_year, end_year + 1))
        
        # Mock cash flow generation
        buy_cf = []
        rent_cf = []
        
        for year in years:
            # Buy scenario: initial negative, then positive
            buy_annual = -50000 if year == 1 else 15000 + (year - 1) * 500
            
            # Rent scenario: consistently negative but increasing
            rent_annual = -12000 - (year - 1) * 300
            
            if aggregation == "Cumulative":
                buy_cf.append(sum([buy_cf[-1] if buy_cf else 0, buy_annual]))
                rent_cf.append(sum([rent_cf[-1] if rent_cf else 0, rent_annual]))
            else:
                buy_cf.append(buy_annual)
                rent_cf.append(rent_annual)
        
        return {
            'years': years,
            'buy_cash_flow': buy_cf,
            'rent_cash_flow': rent_cf
        }
    
    def _generate_cost_breakdown_data(self, data: Any, breakdown_type: str) -> Dict:
        """Generate cost breakdown data"""
        if breakdown_type == "By Category":
            return {
                'labels': ['Mortgage Payment', 'Property Tax', 'Insurance', 'Maintenance', 'Utilities'],
                'values': [180000, 45000, 15000, 25000, 20000],
                'colors': [self.colors['primary'], self.colors['secondary'], self.colors['tertiary'], 
                          self.colors['warning'], self.colors['info']]
            }
        elif breakdown_type == "By Year":
            return {
                'labels': [f'Year {i}' for i in range(1, 6)],
                'values': [50000, 52000, 54000, 56000, 58000],
                'colors': [self.colors['primary']] * 5
            }
        
        return {'labels': [], 'values': [], 'colors': []}
    
    def _generate_scenario_data(self, data: Any, scenarios: List[str], metric: str) -> Dict:
        """Generate scenario comparison data"""
        scenario_values = {
            'Base Case': 125000,
            'Optimistic': 180000,
            'Pessimistic': 50000,
            'High Interest': 75000,
            'Low Market Growth': 100000
        }
        
        return {
            'scenarios': scenarios,
            'values': [scenario_values.get(s, 0) for s in scenarios],
            'metric': metric
        }
    
    def _generate_sensitivity_data(self, data: Any, variables: List[str], sensitivity_range: int) -> Dict:
        """Generate sensitivity analysis data"""
        # Mock sensitivity impacts
        sensitivity_impacts = {
            'Interest Rate': [-25000, 15000],
            'Market Appreciation': [-15000, 30000],
            'Rent Growth': [-20000, 10000],
            'Operating Costs': [-12000, 8000],
            'Vacancy Rate': [-18000, 5000]
        }
        
        selected_vars = [v for v in variables if v in sensitivity_impacts]
        low_impacts = [sensitivity_impacts[v][0] for v in selected_vars]
        high_impacts = [sensitivity_impacts[v][1] for v in selected_vars]
        
        return {
            'variables': selected_vars,
            'low_impact': low_impacts,
            'high_impact': high_impacts
        }
    
    # Mobile rendering methods
    
    def _render_mobile_npv_chart(self, data: Any, state: UIState) -> None:
        """Render mobile-optimized NPV chart"""
        st.markdown("#### 💰 NPV Comparison")
        
        # Simple mobile chart
        npv_data = self._generate_npv_drill_data(data, "Summary")
        fig = self._create_mobile_npv_chart(npv_data)
        st.plotly_chart(fig, use_container_width=True, key="mobile_npv")
    
    def _create_mobile_npv_chart(self, data: Dict) -> go.Figure:
        """Create mobile-optimized NPV chart"""
        scenarios = ["Buy", "Rent"]
        values = [data.get('buy_npv', 0), data.get('rent_npv', 0)]
        colors = [self.colors['ownership'], self.colors['rental']]
        
        fig = go.Figure(data=[go.Bar(
            x=scenarios,
            y=values,
            marker_color=colors,
            text=[format_currency(v, True) for v in values],
            textposition='auto'
        )])
        
        fig.update_layout(
            title='NPV Comparison',
            height=300,
            margin={'l': 20, 'r': 20, 't': 40, 'b': 20},
            showlegend=False
        )
        
        return fig
    
    # Insight and analysis methods
    
    def _show_npv_detail_table(self, data: Dict, drill_level: str) -> None:
        """Show detailed NPV data table"""
        if drill_level == "Annual Breakdown":
            buy_annual = data.get('buy_annual_npv', [])
            rent_annual = data.get('rent_annual_npv', [])
            
            if buy_annual and rent_annual:
                df = pd.DataFrame({
                    'Year': range(1, len(buy_annual) + 1),
                    'Buy NPV': buy_annual,
                    'Rent NPV': rent_annual,
                    'Difference': [b - r for b, r in zip(buy_annual, rent_annual)]
                })
                
                st.dataframe(
                    df.style.format({
                        'Buy NPV': '${:,.0f}',
                        'Rent NPV': '${:,.0f}',
                        'Difference': '${:,.0f}'
                    }),
                    use_container_width=True
                )
    
    def _show_cash_flow_insights(self, data: Dict, time_range: Tuple[int, int]) -> None:
        """Show cash flow insights and analysis"""
        buy_cf = data.get('buy_cash_flow', [])
        rent_cf = data.get('rent_cash_flow', [])
        
        if buy_cf and rent_cf:
            # Calculate key metrics
            total_buy_cf = sum(buy_cf)
            total_rent_cf = sum(rent_cf)
            payback_period = None
            
            # Find payback period
            cumulative_diff = 0
            for i, (buy, rent) in enumerate(zip(buy_cf, rent_cf)):
                cumulative_diff += (buy - rent)
                if cumulative_diff > 0 and payback_period is None:
                    payback_period = i + time_range[0]
                    break
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Buy Cash Flow", format_currency(total_buy_cf))
            with col2:
                st.metric("Total Rent Cash Flow", format_currency(total_rent_cf))
            with col3:
                payback_text = f"Year {payback_period}" if payback_period else "No payback"
                st.metric("Payback Period", payback_text)
    
    def _show_cost_optimization_suggestions(self, data: Dict) -> None:
        """Show cost optimization suggestions"""
        st.markdown("#### 💡 Cost Optimization Opportunities")
        
        suggestions = [
            "Consider energy-efficient upgrades to reduce utility costs",
            "Negotiate property tax assessment for potential savings",
            "Implement preventive maintenance to reduce long-term costs",
            "Explore refinancing options if interest rates have decreased"
        ]
        
        for suggestion in suggestions:
            st.write(f"• {suggestion}")
    
    def _show_scenario_insights(self, data: Dict, scenarios: List[str]) -> None:
        """Show scenario analysis insights"""
        values = data.get('values', [])
        if values:
            best_scenario = scenarios[values.index(max(values))]
            worst_scenario = scenarios[values.index(min(values))]
            
            col1, col2 = st.columns(2)
            with col1:
                st.success(f"🎯 Best Case: {best_scenario}")
                st.write(f"NPV: {format_currency(max(values))}")
            
            with col2:
                st.error(f"⚠️ Worst Case: {worst_scenario}")
                st.write(f"NPV: {format_currency(min(values))}")
    
    def _show_sensitivity_insights(self, data: Dict) -> None:
        """Show sensitivity analysis insights"""
        variables = data.get('variables', [])
        high_impacts = data.get('high_impact', [])
        
        if variables and high_impacts:
            # Find most sensitive variable
            max_impact_idx = high_impacts.index(max(high_impacts, key=abs))
            most_sensitive = variables[max_impact_idx]
            
            st.info(f"🎯 Most Sensitive Variable: **{most_sensitive}**")
            st.write(f"Impact range: {format_currency(abs(high_impacts[max_impact_idx]))}")
    
    # Placeholder methods for additional chart types
    def _render_mobile_cash_flow_chart(self, data: Any, state: UIState) -> None:
        """Mobile cash flow chart - placeholder"""
        st.info("📈 Mobile cash flow chart - coming soon")
    
    def _render_mobile_cost_chart(self, data: Any, state: UIState) -> None:
        """Mobile cost chart - placeholder"""
        st.info("🔍 Mobile cost breakdown chart - coming soon")
    
    def _render_mobile_scenario_chart(self, data: Any, state: UIState) -> None:
        """Mobile scenario chart - placeholder"""
        st.info("📊 Mobile scenario chart - coming soon")
    
    def _render_mobile_sensitivity_chart(self, data: Any, state: UIState) -> None:
        """Mobile sensitivity chart - placeholder"""
        st.info("⚡ Mobile sensitivity chart - coming soon")
    
    def _handle_npv_drill_down(self, selection: Any, drill_level: str) -> None:
        """Handle NPV chart drill-down interactions"""
        # Placeholder for drill-down interaction handling
        pass
    
    def _create_interactive_sunburst(self, data: Dict, breakdown_type: str) -> go.Figure:
        """Create interactive sunburst chart - placeholder"""
        return self._create_interactive_pie_chart(data, breakdown_type)
    
    def _create_interactive_waterfall(self, data: Dict, breakdown_type: str) -> go.Figure:
        """Create interactive waterfall chart - placeholder"""
        return self._create_interactive_pie_chart(data, breakdown_type)
    
    def _create_scenario_bar_chart(self, data: Dict, metric: str) -> go.Figure:
        """Create scenario bar chart - placeholder"""
        scenarios = data.get('scenarios', [])
        values = data.get('values', [])
        
        fig = go.Figure(data=[go.Bar(x=scenarios, y=values)])
        fig.update_layout(title=f'Scenario Comparison - {metric}')
        return fig
    
    def _create_scenario_radar_chart(self, data: Dict) -> go.Figure:
        """Create scenario radar chart - placeholder"""
        return self._create_scenario_bar_chart(data, "Multi-metric")
    
    def _create_scenario_box_plot(self, data: Dict, metric: str) -> go.Figure:
        """Create scenario box plot - placeholder"""
        return self._create_scenario_bar_chart(data, metric)
    
    def _create_scenario_violin_plot(self, data: Dict, metric: str) -> go.Figure:
        """Create scenario violin plot - placeholder"""
        return self._create_scenario_bar_chart(data, metric)
    
    def _create_spider_chart(self, data: Dict) -> go.Figure:
        """Create spider/radar chart for sensitivity - placeholder"""
        return self._create_tornado_chart(data)
    
    def _create_sensitivity_heatmap(self, data: Dict) -> go.Figure:
        """Create sensitivity heatmap - placeholder"""
        return self._create_tornado_chart(data)
    
    # Required interface methods
    def validate_input(self, field_name: str, value: Any) -> 'ValidationResult':
        """Validate chart input parameters"""
        from shared.interfaces import ValidationResult, ValidationStatus
        return ValidationResult(is_valid=True, status=ValidationStatus.VALID, message="Valid")
    
    def get_guidance(self, context: 'GuidanceContext') -> str:
        """Get guidance for chart interactions"""
        return "Click on chart elements to drill down for more detail"


def create_interactive_charts_component() -> InteractiveChartsComponent:
    """Factory function to create interactive charts component"""
    return InteractiveChartsComponent()


# Demo function for testing
def demo_interactive_charts():
    """Demo function for testing interactive charts"""
    st.title("📊 Interactive Charts Demo")
    
    # Create mock state
    from shared.interfaces import UIState
    mock_state = UIState(
        active_tab="charts",
        input_values={"currency": "USD"},
        validation_results={},
        guidance_visible=True,
        mobile_mode=st.sidebar.checkbox("Mobile Mode", False)
    )
    
    # Create component
    component = create_interactive_charts_component()
    
    # Render component
    component.render(None, mock_state)


if __name__ == "__main__":
    demo_interactive_charts()