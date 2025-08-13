"""
Enhanced Guidance System Component
Week 4 UX Enhancement - Contextual help and decision guidance

Features:
- Intelligent contextual help based on user experience level
- Progressive disclosure of complex concepts
- Decision guidance based on analysis results
- Interactive tutorials and onboarding
- Smart tooltips and field explanations
- Accessibility-compliant help system
"""

import streamlit as st
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import sys
import os

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from shared.interfaces import GuidanceSystem, GuidanceContext, AnalyticsResult, UIState, ValidationResult
from utils.defaults import get_field_description


@dataclass
class GuidanceLevel:
    """Guidance complexity levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    EXPERT = "expert"


@dataclass
class GuidanceType:
    """Types of guidance available"""
    FIELD_HELP = "field_help"
    DECISION_SUPPORT = "decision_support"
    TUTORIAL = "tutorial"
    WARNING = "warning"
    SUGGESTION = "suggestion"
    EXPLANATION = "explanation"


@dataclass
class GuidanceContent:
    """Structured guidance content"""
    title: str
    content: str
    level: str
    guidance_type: str
    interactive_elements: Optional[List[str]] = None
    related_fields: Optional[List[str]] = None
    priority: int = 1  # 1=high, 2=medium, 3=low


class EnhancedGuidanceSystem(GuidanceSystem):
    """Enhanced guidance system with contextual help and decision support"""
    
    def __init__(self):
        self.guidance_cache = {}
        self.user_progress = {}
        self.dismissed_guidance = set()
        self.guidance_analytics = {}
        self.max_cache_size = 100  # Limit cache size
        
        # Initialize guidance content
        self._initialize_guidance_content()
        
    def _initialize_guidance_content(self):
        """Initialize structured guidance content"""
        self.guidance_content = {
            # Field-specific guidance
            "project_name": {
                GuidanceLevel.BEGINNER: GuidanceContent(
                    title="Project Name",
                    content="Choose a descriptive name that helps you identify this analysis later. Include location or key details.",
                    level=GuidanceLevel.BEGINNER,
                    guidance_type=GuidanceType.FIELD_HELP,
                    interactive_elements=["example_generator"],
                    priority=1
                ),
                GuidanceLevel.EXPERT: GuidanceContent(
                    title="Project Identification",
                    content="Use systematic naming convention for portfolio analysis tracking.",
                    level=GuidanceLevel.EXPERT,
                    guidance_type=GuidanceType.FIELD_HELP,
                    priority=3
                )
            },
            
            "purchase_price": {
                GuidanceLevel.BEGINNER: GuidanceContent(
                    title="Purchase Price",
                    content="Enter the total cost to buy the property, including the asking price plus estimated closing costs and fees.",
                    level=GuidanceLevel.BEGINNER,
                    guidance_type=GuidanceType.FIELD_HELP,
                    interactive_elements=["cost_breakdown", "market_comparison"],
                    priority=1
                ),
                GuidanceLevel.INTERMEDIATE: GuidanceContent(
                    title="Acquisition Cost",
                    content="Include transaction costs (2-4%), due diligence fees, and any immediate capital improvements needed.",
                    level=GuidanceLevel.INTERMEDIATE,
                    guidance_type=GuidanceType.FIELD_HELP,
                    priority=2
                ),
                GuidanceLevel.EXPERT: GuidanceContent(
                    title="Total Investment",
                    content="Factor in all acquisition costs, working capital requirements, and strategic investment components.",
                    level=GuidanceLevel.EXPERT,
                    guidance_type=GuidanceType.FIELD_HELP,
                    priority=3
                )
            },
            
            "interest_rate": {
                GuidanceLevel.BEGINNER: GuidanceContent(
                    title="Interest Rate",
                    content="This is the annual interest rate your lender will charge. Current commercial rates are typically 6-8%.",
                    level=GuidanceLevel.BEGINNER,
                    guidance_type=GuidanceType.FIELD_HELP,
                    interactive_elements=["current_rates", "rate_calculator"],
                    priority=1
                ),
                GuidanceLevel.INTERMEDIATE: GuidanceContent(
                    title="Borrowing Cost",
                    content="Consider fixed vs. variable rates, term structure, and prepayment penalties.",
                    level=GuidanceLevel.INTERMEDIATE,
                    guidance_type=GuidanceType.FIELD_HELP,
                    priority=2
                )
            },
            
            "analysis_period": {
                GuidanceLevel.BEGINNER: GuidanceContent(
                    title="How Long to Analyze",
                    content="This is how many years into the future you want to compare rent vs. buy. Longer periods show more benefits of ownership.",
                    level=GuidanceLevel.BEGINNER,
                    guidance_type=GuidanceType.FIELD_HELP,
                    interactive_elements=["period_impact_demo"],
                    priority=1
                ),
                GuidanceLevel.EXPERT: GuidanceContent(
                    title="Investment Horizon",
                    content="Align with business planning cycles and asset lifecycle considerations.",
                    level=GuidanceLevel.EXPERT,
                    guidance_type=GuidanceType.FIELD_HELP,
                    priority=3
                )
            }
        }
        
        # Decision guidance templates
        self.decision_guidance = {
            "strong_buy": {
                "title": "Strong Buy Recommendation",
                "content": "Analysis shows significant financial advantage to purchasing.",
                "details": [
                    "NPV difference exceeds 20% of purchase price",
                    "Payback period is reasonable for your business",
                    "Cash flow positive within analysis period"
                ],
                "considerations": [
                    "Ensure adequate cash reserves for maintenance",
                    "Consider market cycle timing",
                    "Evaluate operational flexibility needs"
                ]
            },
            "marginal_buy": {
                "title": "Marginal Buy Recommendation", 
                "content": "Purchasing shows modest advantages but requires careful consideration.",
                "details": [
                    "NPV difference is positive but modest",
                    "Benefits appear in later years",
                    "Sensitivity to key assumptions"
                ],
                "considerations": [
                    "Run sensitivity analysis on key variables",
                    "Consider shorter-term rental with future purchase option",
                    "Evaluate opportunity cost of capital"
                ]
            },
            "neutral": {
                "title": "Neutral Analysis",
                "content": "Rent and buy options show similar financial outcomes.",
                "details": [
                    "NPV difference is minimal",
                    "Non-financial factors may be decisive",
                    "Risk profiles are different"
                ],
                "considerations": [
                    "Consider operational flexibility needs",
                    "Evaluate management burden preferences",
                    "Assess market timing factors"
                ]
            },
            "strong_rent": {
                "title": "Strong Rent Recommendation",
                "content": "Analysis shows significant financial advantage to renting.",
                "details": [
                    "Rental option preserves capital flexibility",
                    "Lower risk profile for uncertain business growth",
                    "Operational advantages outweigh ownership benefits"
                ],
                "considerations": [
                    "Monitor rental rate escalations",
                    "Plan for potential relocation needs",
                    "Consider future purchase timing"
                ]
            }
        }
    
    def get_help_text(self, field_name: str, context: GuidanceContext) -> str:
        """Get contextual help text for a specific field"""
        try:
            # Clean cache if it gets too large
            self._cleanup_cache()
            
            cache_key = f"{field_name}_{context.user_experience_level}"
            
            if cache_key in self.guidance_cache:
                return self.guidance_cache[cache_key]
            
            # Get guidance based on user experience level
            field_guidance = self.guidance_content.get(field_name, {})
            level_guidance = field_guidance.get(context.user_experience_level)
            
            if not level_guidance:
                # Fall back to beginner level if specific level not available
                level_guidance = field_guidance.get(GuidanceLevel.BEGINNER)
            
            if level_guidance:
                help_text = f"**{level_guidance.title}**\n\n{level_guidance.content}"
                
                # Add interactive elements if available
                if level_guidance.interactive_elements:
                    help_text += self._generate_interactive_elements(field_name, level_guidance.interactive_elements, context)
                
                self.guidance_cache[cache_key] = help_text
                return help_text
            
            # Fallback to default description
            return get_field_description(field_name)
        
        except Exception as e:
            # Fallback to basic help on error
            import logging
            logging.error(f"Error getting help text for {field_name}: {e}")
            return f"Help for {field_name.replace('_', ' ').title()}"
    
    def _cleanup_cache(self) -> None:
        """Clean up guidance cache to prevent memory bloat"""
        try:
            if len(self.guidance_cache) > self.max_cache_size:
                # Keep only the most recent entries
                items = list(self.guidance_cache.items())
                self.guidance_cache = dict(items[-self.max_cache_size//2:])
        except Exception:
            # If cleanup fails, clear the cache entirely
            self.guidance_cache = {}
    
    def get_decision_guidance(self, analysis_result: AnalyticsResult) -> str:
        """Provide guidance based on analysis results"""
        if not analysis_result:
            return "Complete the analysis to receive decision guidance."
        
        # Determine recommendation category
        npv_buy = analysis_result.base_npv_buy
        npv_rent = analysis_result.base_npv_rent
        npv_difference = npv_buy - npv_rent
        
        # Calculate relative difference
        purchase_price = self._estimate_purchase_price_from_npv(npv_buy)
        relative_difference = abs(npv_difference) / purchase_price if purchase_price > 0 else 0
        
        # Determine guidance category
        if npv_difference > 0 and relative_difference > 0.20:
            guidance_key = "strong_buy"
        elif npv_difference > 0 and relative_difference > 0.05:
            guidance_key = "marginal_buy"
        elif abs(relative_difference) <= 0.05:
            guidance_key = "neutral"
        else:
            guidance_key = "strong_rent"
        
        guidance = self.decision_guidance[guidance_key]
        
        # Generate comprehensive guidance
        guidance_text = f"""
## {guidance['title']}

{guidance['content']}

### Key Analysis Points:
"""
        for detail in guidance['details']:
            guidance_text += f"• {detail}\n"
        
        guidance_text += "\n### Important Considerations:\n"
        for consideration in guidance['considerations']:
            guidance_text += f"• {consideration}\n"
        
        # Add specific metrics
        guidance_text += f"""
### Financial Summary:
• **NPV Difference**: ${npv_difference:,.0f} (Buy - Rent)
• **Relative Impact**: {relative_difference:.1%} of investment
• **Risk Assessment**: {analysis_result.risk_assessment.overall_risk_level.value.title()}
"""
        
        return guidance_text
    
    def get_next_step_suggestion(self, current_state: UIState) -> str:
        """Suggest next steps based on current state"""
        input_values = current_state.input_values
        validation_results = current_state.validation_results
        
        # Check completion status
        required_fields = self._get_required_fields()
        missing_fields = [field for field in required_fields if not input_values.get(field)]
        
        if missing_fields:
            next_field = missing_fields[0]
            return f"**Next Step**: Complete the '{self._format_field_name(next_field)}' field to continue your analysis."
        
        # Check for validation errors
        error_fields = [field for field, result in validation_results.items() 
                       if hasattr(result, 'is_valid') and not result.is_valid]
        
        if error_fields:
            return f"**Next Step**: Fix validation errors in {len(error_fields)} field(s) before running analysis."
        
        # Check if analysis has been run
        if not current_state.input_values.get('analysis_completed'):
            return "**Next Step**: Your inputs look good! Click 'Run Analysis' to see your results."
        
        # Analysis is complete - suggest next actions
        return self._get_post_analysis_suggestions(current_state)
    
    def show_contextual_guidance(self, field_name: str, context: GuidanceContext) -> None:
        """Display contextual guidance in the UI"""
        if f"guidance_{field_name}" in self.dismissed_guidance:
            return
        
        guidance_text = self.get_help_text(field_name, context)
        
        # Create expandable guidance section
        with st.expander(f"💡 Help: {self._format_field_name(field_name)}", expanded=False):
            st.markdown(guidance_text)
            
            # Add interactive elements if applicable
            self._render_interactive_guidance_elements(field_name, context)
            
            # Dismiss button
            if st.button(f"Don't show this again", key=f"dismiss_{field_name}"):
                self.dismissed_guidance.add(f"guidance_{field_name}")
                st.rerun()
    
    def show_progressive_tutorial(self, current_step: str, user_level: str) -> None:
        """Show progressive tutorial based on current step"""
        tutorials = {
            "getting_started": {
                "title": "Getting Started with Real Estate Analysis",
                "steps": [
                    "Fill in basic project information",
                    "Enter property details and market assumptions", 
                    "Configure financial parameters",
                    "Set operational assumptions",
                    "Run the analysis"
                ],
                "current_step_guidance": {
                    1: "Start by giving your project a name and location. This helps organize multiple analyses.",
                    2: "Property type affects market rates and assumptions. Be specific about size and location.",
                    3: "Get current interest rates from your lender. Don't forget closing costs and fees.",
                    4: "Think about your business growth plans and space needs over time.",
                    5: "The analysis will compare rent vs. buy scenarios over your specified time period."
                }
            }
        }
        
        if current_step in tutorials:
            tutorial = tutorials[current_step]
            
            st.info(f"**{tutorial['title']}**")
            
            # Show progress
            current_step_num = self._get_current_step_number(current_step)
            progress = current_step_num / len(tutorial['steps'])
            st.progress(progress, text=f"Step {current_step_num} of {len(tutorial['steps'])}")
            
            # Show current step guidance
            if current_step_num in tutorial['current_step_guidance']:
                st.markdown(tutorial['current_step_guidance'][current_step_num])
    
    def show_smart_tooltips(self, field_name: str, field_value: Any, context: GuidanceContext) -> None:
        """Show smart tooltips based on field value and context"""
        tooltips = {
            "purchase_price": self._get_price_tooltip,
            "interest_rate": self._get_rate_tooltip,
            "down_payment_percent": self._get_down_payment_tooltip,
            "analysis_period": self._get_period_tooltip
        }
        
        if field_name in tooltips and field_value:
            tooltip_func = tooltips[field_name]
            tooltip_content = tooltip_func(field_value, context)
            
            if tooltip_content:
                st.caption(f"💡 {tooltip_content}")
    
    def show_decision_wizard(self, analysis_result: Optional[AnalyticsResult]) -> None:
        """Show interactive decision wizard"""
        st.markdown("### 🧙‍♂️ Decision Wizard")
        
        if not analysis_result:
            st.info("Run the analysis first to activate the decision wizard.")
            return
        
        # Step 1: Financial Analysis Review
        with st.expander("📊 Step 1: Review Financial Analysis", expanded=True):
            self._show_financial_summary(analysis_result)
            
            financial_acceptable = st.radio(
                "Are the financial projections acceptable?",
                ["Yes", "No", "Need to adjust assumptions"],
                key="financial_acceptable"
            )
            
            if financial_acceptable == "Need to adjust assumptions":
                st.info("💡 Use the sensitivity analysis to see which factors have the biggest impact.")
        
        # Step 2: Risk Assessment
        with st.expander("⚖️ Step 2: Risk Assessment", expanded=False):
            self._show_risk_assessment(analysis_result)
            
            risk_tolerance = st.select_slider(
                "Your risk tolerance for this investment:",
                options=["Very Conservative", "Conservative", "Moderate", "Aggressive", "Very Aggressive"],
                value="Moderate",
                key="risk_tolerance"
            )
        
        # Step 3: Operational Considerations
        with st.expander("⚙️ Step 3: Operational Factors", expanded=False):
            self._show_operational_considerations()
        
        # Step 4: Final Recommendation
        with st.expander("🎯 Step 4: Final Recommendation", expanded=False):
            self._show_final_recommendation(analysis_result)
    
    def track_guidance_usage(self, guidance_type: str, field_name: str, user_action: str) -> None:
        """Track guidance system usage for analytics"""
        timestamp = datetime.now()
        
        if guidance_type not in self.guidance_analytics:
            self.guidance_analytics[guidance_type] = []
        
        self.guidance_analytics[guidance_type].append({
            'field_name': field_name,
            'user_action': user_action,
            'timestamp': timestamp
        })
    
    # Helper methods
    
    def _generate_interactive_elements(self, field_name: str, elements: List[str], context: GuidanceContext) -> str:
        """Generate interactive guidance elements"""
        interactive_content = ""
        
        for element in elements:
            if element == "example_generator":
                interactive_content += self._generate_example_content(field_name, context)
            elif element == "cost_breakdown":
                interactive_content += self._generate_cost_breakdown_help(field_name, context)
            elif element == "market_comparison":
                interactive_content += self._generate_market_comparison_help(field_name, context)
            elif element == "current_rates":
                interactive_content += self._generate_current_rates_help(field_name, context)
        
        return interactive_content
    
    def _generate_example_content(self, field_name: str, context: GuidanceContext) -> str:
        """Generate example content for field"""
        examples = {
            "project_name": [
                "Downtown Office Analysis 2024",
                "Main Street Retail Expansion",
                "Industrial Park Warehouse Study"
            ]
        }
        
        if field_name in examples:
            content = "\n\n**Examples:**\n"
            for example in examples[field_name]:
                content += f"• {example}\n"
            return content
        
        return ""
    
    def _generate_cost_breakdown_help(self, field_name: str, context: GuidanceContext) -> str:
        """Generate cost breakdown help"""
        if field_name == "purchase_price":
            return """
\n**Typical Cost Breakdown:**
• Property price: 85-90%
• Closing costs: 2-4%
• Due diligence: 1-2%
• Immediate improvements: Variable
"""
        return ""
    
    def _generate_market_comparison_help(self, field_name: str, context: GuidanceContext) -> str:
        """Generate market comparison help"""
        return "\n💡 *Market data integration coming soon - will show local comparables*"
    
    def _generate_current_rates_help(self, field_name: str, context: GuidanceContext) -> str:
        """Generate current rates help"""
        return """
\n**Current Market Context:**
• Commercial mortgage rates: 6.5-8.0%
• SBA loans: 6.0-7.5%
• Portfolio lenders: 5.5-7.0%
"""
    
    def _render_interactive_guidance_elements(self, field_name: str, context: GuidanceContext) -> None:
        """Render interactive elements in guidance"""
        # Placeholder for interactive elements like calculators, demos, etc.
        pass
    
    def _get_required_fields(self) -> List[str]:
        """Get list of required fields"""
        return [
            "project_name", "location", "analyst_name", "analysis_date",
            "property_type", "purchase_price", "ownership_property_size",
            "current_space_needed", "down_payment_percent", "interest_rate",
            "loan_term", "current_annual_rent", "rental_property_size",
            "analysis_period", "cost_of_capital", "inflation_rate"
        ]
    
    def _format_field_name(self, field_name: str) -> str:
        """Format field name for display"""
        return field_name.replace("_", " ").title()
    
    def _get_post_analysis_suggestions(self, state: UIState) -> str:
        """Get suggestions after analysis is complete"""
        suggestions = [
            "Review the sensitivity analysis to understand key risk factors",
            "Compare different scenarios to test your assumptions", 
            "Export results for stakeholder presentations",
            "Save your analysis for future reference"
        ]
        
        return "**Suggested Next Steps:**\n" + "\n".join([f"• {s}" for s in suggestions])
    
    def _get_current_step_number(self, step: str) -> int:
        """Get current step number for progress tracking"""
        step_mapping = {
            "project_info": 1,
            "property_details": 2, 
            "financial_params": 3,
            "operational_params": 4,
            "analysis": 5
        }
        return step_mapping.get(step, 1)
    
    def _estimate_purchase_price_from_npv(self, npv_buy: float) -> float:
        """Estimate purchase price from NPV (placeholder)"""
        # This would integrate with actual analysis data
        return abs(npv_buy) * 4  # Rough estimate
    
    def _get_price_tooltip(self, value: float, context: GuidanceContext) -> str:
        """Get price-specific tooltip"""
        if value > 5000000:
            return "Large investment - consider detailed due diligence"
        elif value < 100000:
            return "Verify this is the total acquisition cost"
        return ""
    
    def _get_rate_tooltip(self, value: float, context: GuidanceContext) -> str:
        """Get rate-specific tooltip"""
        if value > 10:
            return "High interest rate - consider alternative financing"
        elif value < 3:
            return "Very low rate - verify with lender"
        return ""
    
    def _get_down_payment_tooltip(self, value: float, context: GuidanceContext) -> str:
        """Get down payment tooltip"""
        if value < 10:
            return "Low down payment may require higher interest rates"
        elif value > 50:
            return "High down payment reduces financing benefits"
        return ""
    
    def _get_period_tooltip(self, value: int, context: GuidanceContext) -> str:
        """Get analysis period tooltip"""
        if value < 10:
            return "Short period may not show full ownership benefits"
        elif value > 30:
            return "Long period increases forecast uncertainty"
        return ""
    
    def _show_financial_summary(self, analysis_result: AnalyticsResult) -> None:
        """Show financial summary in decision wizard"""
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Buy NPV", f"${analysis_result.base_npv_buy:,.0f}")
        with col2:
            st.metric("Rent NPV", f"${analysis_result.base_npv_rent:,.0f}")
        with col3:
            difference = analysis_result.base_npv_buy - analysis_result.base_npv_rent
            st.metric("Difference", f"${difference:,.0f}")
    
    def _show_risk_assessment(self, analysis_result: AnalyticsResult) -> None:
        """Show risk assessment in decision wizard"""
        risk = analysis_result.risk_assessment
        
        st.write(f"**Overall Risk Level**: {risk.overall_risk_level.value.title()}")
        st.write(f"**Risk Description**: {risk.risk_description}")
        
        if risk.risk_factors:
            st.write("**Key Risk Factors**:")
            for factor, score in risk.risk_factors.items():
                st.write(f"• {factor.replace('_', ' ').title()}: {score:.1%}")
    
    def _show_operational_considerations(self) -> None:
        """Show operational considerations"""
        considerations = [
            "Management burden of property ownership",
            "Flexibility to relocate or expand", 
            "Maintenance and repair responsibilities",
            "Property tax and insurance obligations"
        ]
        
        st.write("**Consider these operational factors:**")
        for consideration in considerations:
            importance = st.select_slider(
                consideration,
                options=["Not Important", "Somewhat Important", "Very Important"],
                value="Somewhat Important",
                key=f"consideration_{consideration.replace(' ', '_')}"
            )
    
    def _show_final_recommendation(self, analysis_result: AnalyticsResult) -> None:
        """Show final recommendation"""
        recommendation = self.get_decision_guidance(analysis_result)
        st.markdown(recommendation)
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💾 Save Analysis"):
                st.success("Analysis saved!")
        
        with col2:
            if st.button("📊 Run Sensitivity"):
                st.info("Redirecting to sensitivity analysis...")
        
        with col3:
            if st.button("📄 Export Report"):
                st.info("Report export coming soon...")


def create_guidance_system() -> EnhancedGuidanceSystem:
    """Factory function to create guidance system"""
    return EnhancedGuidanceSystem()


# Demo function for testing
def demo_guidance_system():
    """Demo function for testing guidance system"""
    st.title("🧭 Enhanced Guidance System Demo")
    
    # Create mock context
    from shared.interfaces import GuidanceContext, UIState
    
    user_level = st.selectbox(
        "User Experience Level",
        [GuidanceLevel.BEGINNER, GuidanceLevel.INTERMEDIATE, GuidanceLevel.EXPERT]
    )
    
    mock_context = GuidanceContext(
        current_step="purchase_price",
        user_inputs={"currency": "USD"},
        analysis_results=None,
        user_experience_level=user_level
    )
    
    # Create guidance system
    guidance_system = create_guidance_system()
    
    # Demo different guidance features
    st.markdown("## Field Help Demo")
    field_name = st.selectbox("Select Field", ["project_name", "purchase_price", "interest_rate", "analysis_period"])
    help_text = guidance_system.get_help_text(field_name, mock_context)
    st.markdown(help_text)
    
    st.markdown("## Tutorial Demo")
    guidance_system.show_progressive_tutorial("getting_started", user_level)
    
    st.markdown("## Decision Wizard Demo")
    guidance_system.show_decision_wizard(None)


if __name__ == "__main__":
    demo_guidance_system()