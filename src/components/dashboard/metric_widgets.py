"""
Metric Widgets
Professional metric display widgets for executive dashboards

This module provides reusable metric widgets for professional presentations:
- KPI cards with status indicators
- Confidence badges and progress indicators
- Status indicators and comparison metrics
- Mobile-responsive design with consistent styling
"""

import streamlit as st
from typing import Optional, Literal, Dict, Any
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def create_metric_widget(
    title: str,
    value: str,
    delta: Optional[str] = None,
    delta_color: Literal["normal", "inverse", "off"] = "normal",
    help_text: Optional[str] = None
) -> None:
    """
    Create a basic metric widget using Streamlit's metric component
    
    Args:
        title: Metric title/label
        value: Main metric value to display
        delta: Optional delta/change indicator
        delta_color: Color scheme for delta ("normal", "inverse", "off")
        help_text: Optional tooltip help text
    """
    st.metric(
        label=title,
        value=value,
        delta=delta,
        delta_color=delta_color,
        help=help_text
    )


def create_status_indicator(
    status: Literal["success", "warning", "error", "info"],
    text: str
) -> None:
    """
    Create a colored status indicator
    
    Args:
        status: Status type determining color
        text: Status text to display
    """
    status_colors = {
        "success": "#96CEB4",
        "warning": "#FECA57", 
        "error": "#FF6B6B",
        "info": "#45B7D1"
    }
    
    status_icons = {
        "success": "✅",
        "warning": "⚠️",
        "error": "❌", 
        "info": "ℹ️"
    }
    
    color = status_colors.get(status, "#F0F2F6")
    icon = status_icons.get(status, "")
    
    st.markdown(f"""
    <div style="background-color: {color}; padding: 0.5rem 1rem; border-radius: 0.5rem; 
                display: inline-block; margin: 0.25rem; font-weight: bold;">
        {icon} {text}
    </div>
    """, unsafe_allow_html=True)


def create_confidence_badge(confidence: str) -> None:
    """
    Create a confidence level badge
    
    Args:
        confidence: Confidence level ("High", "Medium", "Low")
    """
    confidence_config = {
        "High": {"color": "#96CEB4", "icon": "🔥"},
        "Medium": {"color": "#FECA57", "icon": "📊"},
        "Low": {"color": "#FF9FF3", "icon": "⚠️"}
    }
    
    config = confidence_config.get(confidence, {"color": "#F0F2F6", "icon": "❓"})
    
    st.markdown(f"""
    <div style="background-color: {config['color']}; padding: 0.5rem 1rem; border-radius: 1rem; 
                display: inline-block; font-weight: bold; color: #262730;">
        {config['icon']} {confidence} Confidence
    </div>
    """, unsafe_allow_html=True)


def create_progress_indicator(
    percentage: float,
    label: str = "Progress",
    color: str = "#FF6B6B"
) -> None:
    """
    Create a progress indicator bar
    
    Args:
        percentage: Progress percentage (0-100)
        label: Progress label
        color: Progress bar color
    """
    st.markdown(f"**{label}**: {percentage:.0f}%")
    st.progress(percentage / 100)


def create_kpi_card(
    title: str,
    value: str,
    subtitle: str = "",
    status: Literal["positive", "negative", "neutral"] = "neutral"
) -> None:
    """
    Create a professional KPI card widget
    
    Args:
        title: KPI title
        value: Main KPI value
        subtitle: Additional context text
        status: Status type for color coding
    """
    status_colors = {
        "positive": "#96CEB4",
        "negative": "#FF6B6B", 
        "neutral": "#F0F2F6"
    }
    
    text_colors = {
        "positive": "#262730",
        "negative": "#FFFFFF",
        "neutral": "#262730"
    }
    
    bg_color = status_colors.get(status, "#F0F2F6")
    text_color = text_colors.get(status, "#262730")
    
    st.markdown(f"""
    <div style="background-color: {bg_color}; padding: 1rem; border-radius: 0.5rem; 
                text-align: center; min-height: 100px; display: flex; flex-direction: column; 
                justify-content: center;">
        <h4 style="margin: 0; color: {text_color}; font-size: 0.9rem;">{title}</h4>
        <h2 style="margin: 0.5rem 0; color: {text_color}; font-size: 1.5rem;">{value}</h2>
        {f'<p style="margin: 0; color: {text_color}; font-size: 0.8rem; opacity: 0.8;">{subtitle}</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)


def create_comparison_metric_pair(
    title: str,
    value1: str,
    label1: str,
    value2: str,
    label2: str,
    winner: Literal["first", "second", "tie"] = "tie"
) -> None:
    """
    Create a side-by-side comparison of two metrics
    
    Args:
        title: Overall comparison title
        value1: First metric value
        label1: First metric label
        value2: Second metric value  
        label2: Second metric label
        winner: Which metric is better ("first", "second", "tie")
    """
    st.markdown(f"#### {title}")
    
    col1, col2 = st.columns(2)
    
    # Determine styling based on winner
    color1 = "#96CEB4" if winner == "first" else "#F0F2F6"
    color2 = "#96CEB4" if winner == "second" else "#F0F2F6"
    
    with col1:
        icon1 = "🏆 " if winner == "first" else ""
        st.markdown(f"""
        <div style="background-color: {color1}; padding: 1rem; border-radius: 0.5rem; text-align: center;">
            <h4 style="margin: 0; color: #262730;">{icon1}{label1}</h4>
            <h3 style="margin: 0.5rem 0 0 0; color: #262730;">{value1}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        icon2 = "🏆 " if winner == "second" else ""
        st.markdown(f"""
        <div style="background-color: {color2}; padding: 1rem; border-radius: 0.5rem; text-align: center;">
            <h4 style="margin: 0; color: #262730;">{icon2}{label2}</h4>
            <h3 style="margin: 0.5rem 0 0 0; color: #262730;">{value2}</h3>
        </div>
        """, unsafe_allow_html=True)


def create_mini_chart_widget(
    title: str,
    data: Dict[str, float],
    chart_type: Literal["line", "bar", "gauge"] = "line"
) -> None:
    """
    Create a small embedded chart widget
    
    Args:
        title: Chart title
        data: Dictionary with chart data
        chart_type: Type of chart to create
    """
    st.markdown(f"**{title}**")
    
    if chart_type == "line" and len(data) >= 2:
        fig = go.Figure(data=go.Scatter(
            x=list(data.keys()),
            y=list(data.values()),
            mode='lines+markers'
        ))
        fig.update_layout(
            height=150,
            margin=dict(l=0, r=0, t=0, b=0),
            showlegend=False,
            xaxis=dict(showticklabels=False),
            yaxis=dict(showticklabels=False)
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
    elif chart_type == "bar" and len(data) >= 1:
        fig = go.Figure(data=go.Bar(
            x=list(data.keys()),
            y=list(data.values())
        ))
        fig.update_layout(
            height=150,
            margin=dict(l=0, r=0, t=0, b=0),
            showlegend=False,
            xaxis=dict(showticklabels=False),
            yaxis=dict(showticklabels=False)
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
    elif chart_type == "gauge" and len(data) == 1:
        value = list(data.values())[0]
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=value,
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={'axis': {'range': [0, 100]},
                   'bar': {'color': "#FF6B6B"}}
        ))
        fig.update_layout(
            height=150,
            margin=dict(l=0, r=0, t=0, b=0)
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    else:
        st.info("Insufficient data for chart")


def create_executive_summary_card(
    recommendation: str,
    npv_difference: float,
    confidence: str,
    key_insight: str = ""
) -> None:
    """
    Create executive summary card with key decision information
    
    Args:
        recommendation: BUY, RENT, or MARGINAL
        npv_difference: NPV advantage amount
        confidence: Confidence level
        key_insight: Additional insight text
    """
    # Determine card styling based on recommendation
    if recommendation == 'BUY':
        bg_color = "#96CEB4"
        icon = "🏠"
        action = "Purchase Recommended"
    elif recommendation == 'RENT':  
        bg_color = "#FECA57"
        icon = "🏢"
        action = "Rental Recommended"
    else:
        bg_color = "#FF9FF3" 
        icon = "⚖️"
        action = "Decision Marginal"
    
    from ..charts.core_charts import format_currency
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {bg_color} 0%, rgba(255,255,255,0.9) 100%); 
                padding: 2rem; border-radius: 1rem; margin: 1rem 0; 
                border: 2px solid {bg_color}; text-align: center;">
        <h1 style="margin: 0; color: #262730; font-size: 2rem;">
            {icon} {action}
        </h1>
        <h2 style="margin: 1rem 0; color: #262730; font-size: 1.5rem;">
            NPV Advantage: {format_currency(abs(npv_difference))}
        </h2>
        <div style="display: flex; justify-content: center; gap: 1rem; margin: 1rem 0; flex-wrap: wrap;">
            <div style="background: rgba(255,255,255,0.9); padding: 0.5rem 1rem; 
                        border-radius: 0.5rem; font-weight: bold; color: #262730;">
                {confidence} Confidence
            </div>
        </div>
        {f'<p style="margin: 1rem 0 0 0; color: #262730; font-style: italic;">{key_insight}</p>' if key_insight else ''}
    </div>
    """, unsafe_allow_html=True)


def create_metric_grid(metrics: Dict[str, Dict[str, Any]], columns: int = 4) -> None:
    """
    Create a responsive grid of metric widgets
    
    Args:
        metrics: Dictionary of metrics with their configurations
        columns: Number of columns in the grid
    """
    metric_items = list(metrics.items())
    
    # Create rows of metrics
    for i in range(0, len(metric_items), columns):
        cols = st.columns(columns)
        
        for j in range(columns):
            if i + j < len(metric_items):
                metric_name, config = metric_items[i + j]
                
                with cols[j]:
                    create_kpi_card(
                        title=config.get('title', metric_name),
                        value=config.get('value', 'N/A'),
                        subtitle=config.get('subtitle', ''),
                        status=config.get('status', 'neutral')
                    )


def create_alert_banner(
    message: str,
    alert_type: Literal["info", "success", "warning", "error"] = "info"
) -> None:
    """
    Create an alert banner for important notifications
    
    Args:
        message: Alert message text
        alert_type: Type of alert for styling
    """
    alert_config = {
        "info": {"color": "#45B7D1", "icon": "ℹ️"},
        "success": {"color": "#96CEB4", "icon": "✅"},
        "warning": {"color": "#FECA57", "icon": "⚠️"},
        "error": {"color": "#FF6B6B", "icon": "❌"}
    }
    
    config = alert_config.get(alert_type, alert_config["info"])
    
    st.markdown(f"""
    <div style="background-color: {config['color']}; padding: 1rem; border-radius: 0.5rem; 
                margin: 1rem 0; border-left: 4px solid rgba(0,0,0,0.2);">
        <strong>{config['icon']} {message}</strong>
    </div>
    """, unsafe_allow_html=True)


# Example usage and testing
if __name__ == "__main__":
    # This would be used for testing the metric widgets
    pass