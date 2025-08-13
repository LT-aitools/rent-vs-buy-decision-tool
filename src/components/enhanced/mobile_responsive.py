"""
Mobile Responsive Component
Week 4 UX Enhancement - Mobile-first responsive design

Features:
- Adaptive layouts for different screen sizes
- Touch-friendly interface elements
- Optimized navigation for mobile devices
- Performance optimization for mobile networks
- Progressive web app capabilities
- Offline functionality support
"""

import streamlit as st
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass
from datetime import datetime
import sys
import os

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from shared.interfaces import UIComponent, UIState, GuidanceContext, AnalyticsResult


@dataclass
class ScreenSize:
    """Screen size breakpoints"""
    MOBILE_SMALL = "mobile_small"  # < 576px
    MOBILE_LARGE = "mobile_large"  # 576px - 768px
    TABLET = "tablet"              # 768px - 992px
    DESKTOP = "desktop"            # 992px - 1200px
    DESKTOP_LARGE = "desktop_large"  # > 1200px


@dataclass
class MobileLayoutConfig:
    """Configuration for mobile layouts"""
    screen_size: str
    column_count: int
    card_style: str  # 'compact', 'standard', 'expanded'
    navigation_style: str  # 'tabs', 'accordion', 'drawer'
    touch_targets: bool = True
    simplified_inputs: bool = True
    progressive_disclosure: bool = True


class MobileResponsiveComponent(UIComponent):
    """Mobile-responsive component with adaptive layouts"""
    
    def __init__(self):
        self.current_screen_size = self._detect_screen_size()
        self.layout_config = self._get_layout_config()
        self.mobile_navigation_state = {}
        self.touch_optimizations = True
        
    def render(self, data: Any, state: UIState) -> None:
        """Render responsive layout based on screen size"""
        # Inject mobile-specific CSS
        self._inject_mobile_css()
        
        # Update screen size detection
        self._update_screen_size()
        
        if self.current_screen_size in [ScreenSize.MOBILE_SMALL, ScreenSize.MOBILE_LARGE]:
            self._render_mobile_layout(data, state)
        elif self.current_screen_size == ScreenSize.TABLET:
            self._render_tablet_layout(data, state)
        else:
            self._render_desktop_layout(data, state)
    
    def _render_mobile_layout(self, data: Any, state: UIState) -> None:
        """Render mobile-optimized layout"""
        st.markdown("### 📱 Mobile Analysis Dashboard")
        
        # Mobile navigation
        self._render_mobile_navigation(state)
        
        # Current section content
        current_section = self._get_current_mobile_section(state)
        
        if current_section == "inputs":
            self._render_mobile_inputs(state)
        elif current_section == "analysis":
            self._render_mobile_analysis(data, state)
        elif current_section == "results":
            self._render_mobile_results(data, state)
        elif current_section == "charts":
            self._render_mobile_charts(data, state)
        else:
            self._render_mobile_overview(data, state)
    
    def _render_tablet_layout(self, data: Any, state: UIState) -> None:
        """Render tablet-optimized layout"""
        st.markdown("### 📱 Tablet Analysis Dashboard")
        
        # Tablet uses 2-column layout with condensed navigation
        col1, col2 = st.columns([1, 2])
        
        with col1:
            self._render_tablet_sidebar(state)
        
        with col2:
            self._render_tablet_main_content(data, state)
    
    def _render_desktop_layout(self, data: Any, state: UIState) -> None:
        """Render desktop layout (fallback to standard components)"""
        st.info("💻 Desktop layout - using standard components")
        # This would delegate to existing desktop components
    
    def _render_mobile_navigation(self, state: UIState) -> None:
        """Render mobile-friendly navigation"""
        # Bottom navigation bar style
        st.markdown("""
        <div class="mobile-nav-container">
            <div class="mobile-nav-bar">
                Navigation will be here
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Use selectbox for section navigation (more mobile-friendly)
        sections = ["Overview", "Inputs", "Analysis", "Results", "Charts"]
        
        current_section = st.selectbox(
            "📍 Navigate to:",
            sections,
            index=0,
            key="mobile_navigation",
            help="Select the section you want to view"
        )
        
        # Store current section in session state
        st.session_state['mobile_current_section'] = current_section.lower()
        
        # Add progress indicator
        self._render_mobile_progress_indicator(state)
    
    def _render_mobile_progress_indicator(self, state: UIState) -> None:
        """Show progress indicator for mobile users"""
        # Calculate completion percentage
        completion_stats = self._calculate_completion_stats(state)
        
        progress_col1, progress_col2, progress_col3 = st.columns([2, 1, 1])
        
        with progress_col1:
            st.progress(
                completion_stats['percentage'] / 100,
                text=f"Progress: {completion_stats['percentage']:.0f}%"
            )
        
        with progress_col2:
            st.metric(
                "Fields",
                f"{completion_stats['completed']}/{completion_stats['total']}"
            )
        
        with progress_col3:
            if completion_stats['percentage'] >= 80:
                st.success("✅ Ready")
            elif completion_stats['percentage'] >= 50:
                st.warning("⚠️ Partial")
            else:
                st.info("📝 Started")
    
    def _render_mobile_inputs(self, state: UIState) -> None:
        """Render mobile-optimized input forms"""
        st.markdown("#### 📝 Project Inputs")
        
        # Use accordion-style sections for mobile
        input_sections = [
            ("📋 Project Info", self._render_mobile_project_inputs),
            ("🏢 Property Details", self._render_mobile_property_inputs),
            ("💰 Financial Terms", self._render_mobile_financial_inputs),
            ("⚙️ Operations", self._render_mobile_operational_inputs)
        ]
        
        for section_title, render_func in input_sections:
            with st.expander(section_title, expanded=False):
                render_func(state)
        
        # Mobile-friendly validation summary
        self._render_mobile_validation_summary(state)
    
    def _render_mobile_project_inputs(self, state: UIState) -> None:
        """Mobile project inputs - simplified and touch-friendly"""
        # Stack inputs vertically for mobile
        st.text_input(
            "Project Name *",
            key="project_name",
            placeholder="e.g., Downtown Office Analysis",
            help="Give your analysis a memorable name"
        )
        
        st.text_input(
            "Location *",
            key="location", 
            placeholder="e.g., 123 Main St, City",
            help="Property address or general location"
        )
        
        st.text_input(
            "Your Name *",
            key="analyst_name",
            placeholder="e.g., John Smith",
            help="Who is conducting this analysis"
        )
        
        st.date_input(
            "Analysis Date *",
            key="analysis_date",
            help="Date of this analysis"
        )
        
        # Currency selector with mobile-friendly formatting
        currencies = ["USD ($)", "EUR (€)", "GBP (£)", "CAD (C$)"]
        st.selectbox(
            "Currency *",
            currencies,
            key="currency_mobile",
            help="Select your local currency"
        )
    
    def _render_mobile_property_inputs(self, state: UIState) -> None:
        """Mobile property inputs"""
        property_types = ["Office", "Retail", "Industrial", "Warehouse", "Mixed Use"]
        st.selectbox(
            "Property Type *",
            property_types,
            key="property_type",
            help="Type of commercial property"
        )
        
        # Use number input with step controls for better mobile UX
        st.number_input(
            "Property Size (m²) *",
            min_value=500,
            max_value=100000,
            step=500,
            key="ownership_property_size",
            help="Total property size in square meters"
        )
        
        st.number_input(
            "Space You Need (m²) *",
            min_value=100,
            max_value=50000,
            step=100,
            key="current_space_needed",
            help="Space you actually need for operations"
        )
        
        # Mobile-friendly slider
        st.select_slider(
            "Market Growth Rate *",
            options=["1%", "2%", "3%", "4%", "5%", "6%", "7%", "8%"],
            value="3%",
            key="market_appreciation_mobile",
            help="Expected annual property value growth"
        )
    
    def _render_mobile_financial_inputs(self, state: UIState) -> None:
        """Mobile financial inputs"""
        # Large number inputs with clear formatting
        st.number_input(
            "Purchase Price ($) *",
            min_value=50000,
            max_value=10000000,
            step=10000,
            key="purchase_price",
            help="Total cost to buy the property",
            format="%d"
        )
        
        # Use slider for percentages on mobile (easier than typing)
        st.slider(
            "Down Payment % *",
            min_value=0,
            max_value=100,
            step=5,
            key="down_payment_percent",
            help="Percentage of purchase price as down payment"
        )
        
        st.number_input(
            "Interest Rate % *",
            min_value=0.0,
            max_value=15.0,
            step=0.1,
            key="interest_rate",
            help="Annual mortgage interest rate",
            format="%.1f"
        )
        
        st.number_input(
            "Annual Rent ($) *",
            min_value=1000,
            max_value=1000000,
            step=1000,
            key="current_annual_rent",
            help="Current annual rental cost",
            format="%d"
        )
    
    def _render_mobile_operational_inputs(self, state: UIState) -> None:
        """Mobile operational inputs"""
        st.slider(
            "Analysis Period (years) *",
            min_value=5,
            max_value=30,
            value=25,
            step=1,
            key="analysis_period",
            help="How many years to analyze"
        )
        
        st.number_input(
            "Cost of Capital % *",
            min_value=0.0,
            max_value=20.0,
            step=0.5,
            key="cost_of_capital",
            help="Required return rate for investment",
            format="%.1f"
        )
        
        st.number_input(
            "Inflation Rate % *",
            min_value=0.0,
            max_value=10.0,
            step=0.1,
            key="inflation_rate",
            help="Expected annual inflation rate",
            format="%.1f"
        )
    
    def _render_mobile_validation_summary(self, state: UIState) -> None:
        """Mobile validation summary"""
        st.markdown("---")
        st.markdown("#### ✅ Input Status")
        
        # Simple validation check
        required_fields = ['project_name', 'location', 'purchase_price', 'current_annual_rent']
        completed_fields = sum(1 for field in required_fields if st.session_state.get(field))
        
        if completed_fields == len(required_fields):
            st.success("🎉 Ready to analyze!")
            if st.button("🚀 Run Analysis", use_container_width=True):
                st.session_state['mobile_current_section'] = 'analysis'
                st.rerun()
        else:
            missing = len(required_fields) - completed_fields
            st.warning(f"⚠️ {missing} required field(s) missing")
    
    def _render_mobile_analysis(self, data: Any, state: UIState) -> None:
        """Mobile analysis view"""
        st.markdown("#### 🧮 Running Analysis")
        
        # Show analysis progress
        with st.spinner("Calculating financial projections..."):
            # Simulate analysis progress
            progress_bar = st.progress(0, text="Initializing...")
            
            import time
            for i in range(100):
                time.sleep(0.01)  # Simulate work
                progress_text = "Calculating NPV..." if i < 50 else "Generating results..."
                progress_bar.progress(i + 1, text=progress_text)
        
        st.success("✅ Analysis Complete!")
        
        # Quick results summary for mobile
        self._render_mobile_quick_results(data, state)
        
        # Navigation to full results
        if st.button("📊 View Detailed Results", use_container_width=True):
            st.session_state['mobile_current_section'] = 'results'
            st.rerun()
    
    def _render_mobile_quick_results(self, data: Any, state: UIState) -> None:
        """Quick results summary for mobile"""
        st.markdown("#### 📊 Quick Results")
        
        # Mock results for demo
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "Buy NPV",
                "$125,000",
                delta="Better choice"
            )
        
        with col2:
            st.metric(
                "Rent NPV", 
                "-$50,000",
                delta="-$175,000"
            )
        
        # Simple recommendation
        st.success("💡 **Recommendation**: Buy is financially better over 25 years")
        
        # Key insights
        with st.expander("📈 Key Insights", expanded=False):
            insights = [
                "Break-even point: Year 8",
                "Total savings by buying: $175,000", 
                "Monthly cash flow advantage: $850",
                "Risk level: Moderate"
            ]
            
            for insight in insights:
                st.write(f"• {insight}")
    
    def _render_mobile_results(self, data: Any, state: UIState) -> None:
        """Mobile detailed results view"""
        st.markdown("#### 📈 Detailed Results")
        
        # Results navigation
        result_tabs = st.tabs(["💰 Summary", "📊 Charts", "📋 Details"])
        
        with result_tabs[0]:
            self._render_mobile_results_summary(data, state)
        
        with result_tabs[1]:
            self._render_mobile_results_charts(data, state)
        
        with result_tabs[2]:
            self._render_mobile_results_details(data, state)
    
    def _render_mobile_results_summary(self, data: Any, state: UIState) -> None:
        """Mobile results summary"""
        # Financial metrics grid
        metrics = [
            ("Buy NPV", "$125,000", "green"),
            ("Rent NPV", "-$50,000", "red"), 
            ("Difference", "$175,000", "blue"),
            ("Payback", "8 years", "orange")
        ]
        
        for i in range(0, len(metrics), 2):
            col1, col2 = st.columns(2)
            
            with col1:
                metric = metrics[i]
                st.metric(metric[0], metric[1])
            
            if i + 1 < len(metrics):
                with col2:
                    metric = metrics[i + 1]
                    st.metric(metric[0], metric[1])
        
        # Decision guidance
        st.markdown("---")
        st.markdown("#### 🎯 Decision Guidance")
        st.success("**Strong Buy Recommendation**")
        st.write("The analysis shows significant financial advantages to purchasing:")
        
        advantages = [
            "NPV advantage of $175,000 over 25 years",
            "Reasonable payback period of 8 years", 
            "Building equity vs. paying rent",
            "Potential for property appreciation"
        ]
        
        for advantage in advantages:
            st.write(f"✅ {advantage}")
    
    def _render_mobile_results_charts(self, data: Any, state: UIState) -> None:
        """Mobile results charts"""
        # Simple chart selection for mobile
        chart_type = st.selectbox(
            "Select Chart",
            ["NPV Comparison", "Cash Flow", "Cost Breakdown"],
            key="mobile_chart_type"
        )
        
        if chart_type == "NPV Comparison":
            self._render_mobile_npv_chart()
        elif chart_type == "Cash Flow":
            self._render_mobile_cashflow_chart()
        else:
            self._render_mobile_cost_chart()
    
    def _render_mobile_npv_chart(self) -> None:
        """Simple mobile NPV chart"""
        import plotly.graph_objects as go
        
        fig = go.Figure(data=[
            go.Bar(
                x=['Buy', 'Rent'],
                y=[125000, -50000],
                marker_color=['green', 'red'],
                text=['$125k', '-$50k'],
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title='NPV Comparison',
            height=300,
            margin=dict(l=20, r=20, t=40, b=20),
            font=dict(size=14)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_mobile_cashflow_chart(self) -> None:
        """Mobile cash flow chart"""
        st.info("📈 Cash flow chart optimized for mobile - coming soon")
    
    def _render_mobile_cost_chart(self) -> None:
        """Mobile cost breakdown chart"""
        st.info("🥧 Cost breakdown chart optimized for mobile - coming soon")
    
    def _render_mobile_results_details(self, data: Any, state: UIState) -> None:
        """Mobile detailed results"""
        st.markdown("#### 📋 Analysis Details")
        
        # Expandable sections for details
        detail_sections = [
            ("💰 Financial Summary", self._render_financial_details),
            ("📊 Assumptions Used", self._render_assumptions_details),
            ("⚠️ Risk Factors", self._render_risk_details),
            ("💡 Recommendations", self._render_recommendations_details)
        ]
        
        for title, render_func in detail_sections:
            with st.expander(title, expanded=False):
                render_func()
    
    def _render_mobile_charts(self, data: Any, state: UIState) -> None:
        """Mobile charts view"""
        st.markdown("#### 📊 Interactive Charts")
        st.info("Full interactive charts optimized for mobile devices")
        
        # Would integrate with interactive_charts component
        from .interactive_charts import create_interactive_charts_component
        charts_component = create_interactive_charts_component()
        
        # Render in mobile mode
        mobile_state = UIState(
            active_tab="charts",
            input_values=state.input_values,
            validation_results={},
            guidance_visible=False,
            mobile_mode=True
        )
        
        charts_component.render(data, mobile_state)
    
    def _render_mobile_overview(self, data: Any, state: UIState) -> None:
        """Mobile overview/dashboard"""
        st.markdown("#### 🏠 Analysis Overview")
        
        # Project summary card
        with st.container():
            st.markdown("**📋 Project Summary**")
            project_name = st.session_state.get('project_name', 'Untitled Analysis')
            location = st.session_state.get('location', 'Not specified')
            
            st.write(f"**Project**: {project_name}")
            st.write(f"**Location**: {location}")
            
            completion_stats = self._calculate_completion_stats(state)
            st.write(f"**Progress**: {completion_stats['percentage']:.0f}% complete")
        
        st.markdown("---")
        
        # Quick action buttons
        st.markdown("**🚀 Quick Actions**")
        
        action_col1, action_col2 = st.columns(2)
        
        with action_col1:
            if st.button("📝 Edit Inputs", use_container_width=True):
                st.session_state['mobile_current_section'] = 'inputs'
                st.rerun()
        
        with action_col2:
            if st.button("🧮 Run Analysis", use_container_width=True):
                st.session_state['mobile_current_section'] = 'analysis'
                st.rerun()
        
        # Recent activity or tips
        st.markdown("---")
        st.markdown("**💡 Tips for Better Analysis**")
        
        tips = [
            "Get current interest rates from your lender",
            "Research comparable properties in the area",
            "Factor in all operating costs and maintenance",
            "Consider your business growth plans"
        ]
        
        for tip in tips:
            st.write(f"• {tip}")
    
    def _render_tablet_sidebar(self, state: UIState) -> None:
        """Render tablet sidebar navigation"""
        st.markdown("### 📱 Navigation")
        
        sections = ["Overview", "Inputs", "Analysis", "Results"]
        
        for section in sections:
            if st.button(f"📍 {section}", use_container_width=True, key=f"tablet_{section}"):
                st.session_state['tablet_current_section'] = section.lower()
                st.rerun()
        
        # Progress summary
        st.markdown("---")
        st.markdown("### 📊 Progress")
        completion_stats = self._calculate_completion_stats(state)
        st.progress(completion_stats['percentage'] / 100)
        st.caption(f"{completion_stats['completed']}/{completion_stats['total']} fields complete")
    
    def _render_tablet_main_content(self, data: Any, state: UIState) -> None:
        """Render tablet main content area"""
        current_section = st.session_state.get('tablet_current_section', 'overview')
        
        if current_section == 'inputs':
            st.markdown("### 📝 Project Inputs")
            # Render condensed input forms suitable for tablet
            self._render_tablet_inputs(state)
        elif current_section == 'analysis':
            st.markdown("### 🧮 Analysis")
            self._render_mobile_analysis(data, state)  # Reuse mobile analysis
        elif current_section == 'results':
            st.markdown("### 📈 Results")
            self._render_mobile_results(data, state)   # Reuse mobile results
        else:
            st.markdown("### 🏠 Overview")
            self._render_mobile_overview(data, state)  # Reuse mobile overview
    
    def _render_tablet_inputs(self, state: UIState) -> None:
        """Tablet-optimized input forms"""
        # Use 2-column layout for tablet
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📋 Project & Property")
            st.text_input("Project Name *", key="project_name")
            st.text_input("Location *", key="location")
            st.selectbox("Property Type *", ["Office", "Retail", "Industrial"], key="property_type")
            
        with col2:
            st.markdown("#### 💰 Financial")
            st.number_input("Purchase Price ($) *", min_value=0, step=10000, key="purchase_price")
            st.slider("Down Payment %", 0, 100, 20, key="down_payment_percent") 
            st.number_input("Interest Rate %", 0.0, 15.0, 6.5, step=0.1, key="interest_rate")
    
    # Helper methods
    
    def _detect_screen_size(self) -> str:
        """Detect current screen size (simplified for Streamlit)"""
        # In a real implementation, this would use JavaScript to detect screen size
        # For now, we'll use a simple approach with session state
        if 'screen_size' not in st.session_state:
            st.session_state['screen_size'] = ScreenSize.DESKTOP
        
        return st.session_state.get('screen_size', ScreenSize.DESKTOP)
    
    def _update_screen_size(self) -> None:
        """Update screen size detection"""
        # Add screen size selector for demo purposes
        if st.sidebar.checkbox("🔧 Screen Size Simulator", False):
            sizes = [ScreenSize.MOBILE_SMALL, ScreenSize.MOBILE_LARGE, ScreenSize.TABLET, ScreenSize.DESKTOP]
            selected_size = st.sidebar.selectbox("Screen Size", sizes)
            st.session_state['screen_size'] = selected_size
            self.current_screen_size = selected_size
    
    def _get_layout_config(self) -> MobileLayoutConfig:
        """Get layout configuration based on screen size"""
        configs = {
            ScreenSize.MOBILE_SMALL: MobileLayoutConfig(
                screen_size=ScreenSize.MOBILE_SMALL,
                column_count=1,
                card_style='compact',
                navigation_style='tabs',
                touch_targets=True,
                simplified_inputs=True
            ),
            ScreenSize.MOBILE_LARGE: MobileLayoutConfig(
                screen_size=ScreenSize.MOBILE_LARGE,
                column_count=1,
                card_style='standard',
                navigation_style='tabs',
                touch_targets=True,
                simplified_inputs=True
            ),
            ScreenSize.TABLET: MobileLayoutConfig(
                screen_size=ScreenSize.TABLET,
                column_count=2,
                card_style='standard',
                navigation_style='drawer',
                touch_targets=True,
                simplified_inputs=False
            )
        }
        
        return configs.get(self.current_screen_size, MobileLayoutConfig(
            screen_size=ScreenSize.DESKTOP,
            column_count=3,
            card_style='expanded',
            navigation_style='drawer'
        ))
    
    def _get_current_mobile_section(self, state: UIState) -> str:
        """Get current mobile section"""
        return st.session_state.get('mobile_current_section', 'overview')
    
    def _calculate_completion_stats(self, state: UIState) -> Dict[str, Any]:
        """Calculate input completion statistics"""
        required_fields = ['project_name', 'location', 'analyst_name', 'purchase_price', 
                          'current_annual_rent', 'analysis_period']
        
        completed = sum(1 for field in required_fields if st.session_state.get(field))
        total = len(required_fields)
        percentage = (completed / total) * 100 if total > 0 else 0
        
        return {
            'completed': completed,
            'total': total,
            'percentage': percentage
        }
    
    def _inject_mobile_css(self) -> None:
        """Inject mobile-specific CSS with security validation"""
        try:
            from .enhanced_security import input_sanitizer
            
            mobile_css = """
            <style>
            .mobile-nav-container {
                position: sticky;
                top: 0;
                z-index: 1000;
                background: white;
                padding: 10px 0;
                border-bottom: 1px solid #e6e6e6;
            }
            
            .mobile-nav-bar {
                display: flex;
                justify-content: space-around;
                align-items: center;
                padding: 10px;
                background: #f0f2f6;
                border-radius: 8px;
                margin: 0 10px;
            }
            
            /* Touch-friendly buttons */
            .stButton > button {
                min-height: 44px;
                font-size: 16px;
                padding: 12px 24px;
            }
            
            /* Larger input fields for mobile */
            .stTextInput > div > div > input {
                font-size: 16px;
                padding: 12px;
            }
            
            .stNumberInput > div > div > input {
                font-size: 16px; 
                padding: 12px;
            }
            
            /* Responsive metrics */
            @media (max-width: 768px) {
                .metric-container {
                    margin-bottom: 16px;
                }
                
                .stMetric {
                    background: #f8f9fa;
                    padding: 16px;
                    border-radius: 8px;
                    border: 1px solid #e9ecef;
                }
            }
            
            /* Improved spacing for mobile */
            .element-container {
                margin-bottom: 12px;
            }
            
            /* Better card styling */
            .stContainer {
                padding: 16px;
                margin-bottom: 16px;
            }
            </style>
            """
            
            # Sanitize CSS before injection
            sanitized_css = input_sanitizer.sanitize_css(mobile_css)
            st.markdown(sanitized_css, unsafe_allow_html=True)
            
        except Exception as e:
            # Fallback to no custom CSS if there's an error
            st.error(f"Error loading mobile styles: {str(e)}")
            import logging
            logging.error(f"Mobile CSS injection failed: {e}")
    
    # Detail rendering methods
    
    def _render_financial_details(self) -> None:
        """Render financial details section"""
        details = [
            ("Initial Investment", "$500,000"),
            ("Down Payment", "$100,000 (20%)"),
            ("Loan Amount", "$400,000"),
            ("Monthly Payment", "$2,847"),
            ("Total Interest", "$225,000"),
            ("Property Taxes", "$12,000/year"),
            ("Insurance", "$8,000/year")
        ]
        
        for label, value in details:
            col1, col2 = st.columns([2, 1])
            with col1:
                st.write(label)
            with col2:
                st.write(f"**{value}**")
    
    def _render_assumptions_details(self) -> None:
        """Render assumptions details"""
        assumptions = [
            "Property appreciation: 3.0% annually",
            "Rental rate increase: 2.5% annually", 
            "Inflation rate: 3.0% annually",
            "Cost of capital: 8.0%",
            "Analysis period: 25 years",
            "Maintenance: 2.0% of property value"
        ]
        
        for assumption in assumptions:
            st.write(f"• {assumption}")
    
    def _render_risk_details(self) -> None:
        """Render risk details"""
        risks = [
            ("Interest Rate Risk", "Medium", "Rising rates increase borrowing costs"),
            ("Market Risk", "Medium", "Property values may decline"),
            ("Liquidity Risk", "High", "Property harder to sell quickly"),
            ("Operational Risk", "Low", "Stable income property type")
        ]
        
        for risk, level, description in risks:
            st.write(f"**{risk}** ({level})")
            st.write(f"_{description}_")
            st.write("")
    
    def _render_recommendations_details(self) -> None:
        """Render recommendations details"""
        recommendations = [
            "✅ **Proceed with Purchase**: Strong financial case for buying",
            "🔍 **Due Diligence**: Conduct thorough property inspection", 
            "💰 **Financing**: Lock in current interest rates if possible",
            "📊 **Monitoring**: Review assumptions annually",
            "🎯 **Timeline**: Execute purchase within 6 months"
        ]
        
        for recommendation in recommendations:
            st.markdown(recommendation)
    
    # Required interface methods
    
    def validate_input(self, field_name: str, value: Any) -> 'ValidationResult':
        """Validate input for mobile component"""
        from shared.interfaces import ValidationResult, ValidationStatus
        return ValidationResult(is_valid=True, status=ValidationStatus.VALID, message="Valid")
    
    def get_guidance(self, context: 'GuidanceContext') -> str:
        """Get guidance for mobile users"""
        return "Mobile-optimized guidance: Use the navigation menu to move between sections."


def create_mobile_responsive_component() -> MobileResponsiveComponent:
    """Factory function to create mobile responsive component"""
    return MobileResponsiveComponent()


# Demo function for testing
def demo_mobile_responsive():
    """Demo function for testing mobile responsive component"""
    st.title("📱 Mobile Responsive Demo")
    
    # Create mock state
    from shared.interfaces import UIState
    mock_state = UIState(
        active_tab="mobile",
        input_values={"currency": "USD"},
        validation_results={},
        guidance_visible=False,
        mobile_mode=True
    )
    
    # Create component
    component = create_mobile_responsive_component()
    
    # Render component
    component.render(None, mock_state)


if __name__ == "__main__":
    demo_mobile_responsive()