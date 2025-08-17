"""
Calculation Tooltips Utility
Provides detailed explanations for all financial calculations shown in analysis results

This module contains comprehensive tooltips that explain:
- How each calculation is performed
- Formula explanations in plain language
- Key assumptions and parameters
- Business logic behind calculations
- Similar to input field tooltips but for results
"""

from typing import Dict, Any, Optional
import streamlit as st


# NPV Analysis Tooltips
NPV_TOOLTIPS = {
    "npv_difference": {
        "title": "NPV Difference",
        "formula": "Ownership NPV - Rental NPV",
        "explanation": "The net present value difference shows which option provides better long-term financial value. A positive value means ownership is better; negative means rental is better. This accounts for the time value of money using your cost of capital.",
        "calculation": "Calculated by comparing the present value of all future cash flows from both scenarios over the analysis period, including terminal values. Includes subletting income, expansion costs, property upgrades, and tax benefits where applicable."
    },
    
    "ownership_npv": {
        "title": "Ownership NPV", 
        "formula": "Initial Investment + Present Value of Annual Costs + Present Value of Terminal Value",
        "explanation": "Total net present value of the ownership scenario, including all costs and the final property value. Accounts for business expansion, subletting income, and property upgrades over time.",
        "calculation": "Down payment + transaction costs + space improvements + PV of (mortgage payments + property taxes + insurance + maintenance + management fees + expansion costs + property upgrades - tax benefits - subletting income) + PV of terminal property value"
    },
    
    "rental_npv": {
        "title": "Rental NPV",
        "formula": "Initial Rental Costs + Present Value of Annual Rent Payments + Present Value of Terminal Alternative Investment",
        "explanation": "Total net present value of the rental scenario, including all rental costs and alternative investment returns. Accounts for business expansion requiring additional rental space over time.",
        "calculation": "Security deposit + moving costs + rental commission + PV of (annual rent payments + expansion space rent - tax benefits) + PV of alternative investment terminal value"
    },
    
    "initial_investment": {
        "title": "Initial Investment",
        "formula": "Down Payment + Transaction Costs + Space Improvements",
        "explanation": "Total upfront cash required to purchase and customize the property. This is the immediate capital requirement that impacts your cash flow.",
        "calculation": "Purchase Price × Down Payment % + Transaction Costs (legal, inspection, stamp duty) + Space Improvement Cost (tenant improvements, customizations)"
    },
    
    "terminal_value": {
        "title": "Terminal Value (Present Value)",
        "formula": "(Future Property Value - Remaining Loan Balance) ÷ (1 + Discount Rate)^Years",
        "explanation": "Present value of your net equity in the property at the end of the analysis period. This represents the cash you would receive if you sold the property.",
        "calculation": "[Purchase Price × (1 + Market Appreciation Rate)^Analysis Period - Outstanding Mortgage Balance] ÷ (1 + Cost of Capital)^Analysis Period"
    }
}

# Annual Cost Tooltips
ANNUAL_COST_TOOLTIPS = {
    "mortgage_payment": {
        "title": "Annual Mortgage Payment",
        "formula": "Monthly Payment × 12",
        "explanation": "Annual mortgage payments including principal and interest.",
        "calculation": "Based on loan amount (Purchase Price - Down Payment), interest rate, and loan term using standard amortization formula"
    },
    
    "property_taxes": {
        "title": "Property Taxes",
        "formula": "Property Value × Property Tax Rate × Escalation Factor",
        "explanation": "Annual property taxes with year-over-year increases.",
        "calculation": "Year 1: Purchase Price × Property Tax Rate. Year N: Year 1 Amount × (1 + Property Tax Escalation)^(N-1)"
    },
    
    "insurance_cost": {
        "title": "Property Insurance",
        "formula": "Base Insurance Cost × Inflation Factor", 
        "explanation": "Annual property insurance premiums, escalating with inflation.",
        "calculation": "Year 1: Base Insurance Cost. Year N: Base Cost × (1 + Inflation Rate)^(N-1)"
    },
    
    "maintenance_cost": {
        "title": "Annual Maintenance",
        "formula": "Purchase Price × Maintenance % × Inflation Factor",
        "explanation": "Annual maintenance costs as percentage of property value, escalating with inflation.",
        "calculation": "Base Amount = Purchase Price × Annual Maintenance %. Year N: Base Amount × (1 + Inflation Rate)^(N-1)"
    },
    
    "property_management": {
        "title": "Property Management Fees",
        "formula": "Base Management Fee × Inflation Factor",
        "explanation": "Annual property management fees, escalating with inflation.",
        "calculation": "Year 1: Base Management Fee. Year N: Base Fee × (1 + Inflation Rate)^(N-1)"
    },
    
    "capex_reserve": {
        "title": "CapEx Reserve",
        "formula": "Purchase Price × CapEx Reserve Rate × Inflation Factor",
        "explanation": "Annual capital expenditure reserves for major repairs and improvements.",
        "calculation": "Base Amount = Purchase Price × CapEx Reserve Rate %. Year N: Base Amount × (1 + Inflation Rate)^(N-1)"
    },
    
    "annual_rent": {
        "title": "Annual Rent",
        "formula": "(Base Rent + Expansion Rent) × Real Rent Escalation Factor",
        "explanation": "Annual rental payments with year-over-year increases. Uses real (inflation-adjusted) rent increase rate to avoid double-counting inflation. Includes expansion space rent when business growth occurs.",
        "calculation": "Year 1: Current Annual Rent for current space. Year N: Year 1 Amount × (1 + Real Rent Increase Rate)^(N-1). Real rate = Nominal rate - Inflation rate. Additional rent added when expansion year is reached."
    },
    
    "rental_cost_comparison": {
        "title": "Rental Cost in Comparisons",
        "formula": "Annual Rent - Tax Benefits",
        "explanation": "After-tax rental cost used in comparison tables. Lower than gross rent because rent is tax-deductible as a business expense.",
        "calculation": "Gross Annual Rent - (Gross Annual Rent × Corporate Tax Rate). This ensures fair comparison with ownership costs that also include tax benefits."
    },
    
    "net_cash_flow": {
        "title": "Net Cash Flow",
        "formula": "Total Costs - Tax Benefits - Income",
        "explanation": "Annual net cash outflow for each scenario. Negative values represent costs; positive values represent income.",
        "calculation": "For ownership: Mortgage + Property Taxes + Insurance + Maintenance + Management + CapEx + Obsolescence - Tax Benefits - Subletting Income. For rental: Rent Payments - Tax Benefits."
    },
    
    "corporate_tax_rate": {
        "title": "Corporate Tax Rate",
        "formula": "Country-Specific Corporate Income Tax Rate",
        "explanation": "The standard corporate income tax rate for the selected country. This rate is used to calculate tax benefits from business expense deductions.",
        "calculation": "Based on current tax regulations for each country. Includes federal/national rates and may include average provincial/state rates where applicable. Used to calculate tax savings from rent deductions (rental scenario) and property-related business deductions (ownership scenario)."
    },
    
    "tax_benefits": {
        "title": "Tax Benefits",
        "formula": "(Mortgage Interest + Property Taxes + Depreciation + Other Deductions) × Tax Rate",
        "explanation": "Annual tax savings from ownership deductions. Includes all allowable business deductions for property-related expenses.",
        "calculation": "Sum of deductible expenses (mortgage interest + property taxes + depreciation + maintenance + property management + insurance) × Corporate Tax Rate"
    },
    
    "subletting_income": {
        "title": "Subletting Income",
        "formula": "Available Subletting Space × Subletting Rate × (1 + Rent Escalation)^Year",
        "explanation": "Annual income from subletting unused space to other tenants. Income grows with rent escalation and decreases as your business expands.",
        "calculation": "Available Space = MIN(Total Property Size - Current Space Needed - Future Expansion, Desired Subletting Space). Income = Available Space × Subletting Rate × (1 + Rent Increase Rate)^(Year-1)"
    },
    
    "space_improvement_cost": {
        "title": "Space Improvement Cost",
        "formula": "One-time Improvement Investment",
        "explanation": "Total cost for customizing and improving the space to meet specific business needs. This is a capital investment that may qualify for depreciation benefits.",
        "calculation": "Includes tenant improvements, customizations, equipment installations, and space modifications required before occupancy. May include IT infrastructure, specialized flooring, partition walls, and business-specific modifications."
    },
    
    "property_upgrade_cost": {
        "title": "Property Upgrade Cost",
        "formula": "Periodic Major Renovations",
        "explanation": "Costs for major property renovations and upgrades that occur on a cyclical basis (e.g., every 20-30 years).",
        "calculation": "Calculated as a percentage of building value (excluding land) applied every property upgrade cycle. Includes major renovations, HVAC replacements, roof repairs, and structural upgrades."
    },
    
    "expansion_costs": {
        "title": "Business Expansion Costs",
        "formula": "Additional Space Costs from Growth",
        "explanation": "Additional costs incurred when your business grows and requires more space.",
        "calculation": "For ownership: May trigger property upgrades or additional space purchase. For rental: Additional rent for expanded space calculated at market rates with rent escalation."
    },
    
    "obsolescence_cost": {
        "title": "Obsolescence Risk Cost",
        "formula": "Purchase Price × Obsolescence Risk Rate × Inflation Factor",
        "explanation": "Annual allowance for building obsolescence and depreciation beyond normal maintenance.",
        "calculation": "Base Amount = Purchase Price × Obsolescence Risk Rate %. Year N: Base Amount × (1 + Inflation Rate)^(N-1). Accounts for technological and functional obsolescence."
    }
}

# Cash Flow Analysis Tooltips
CASH_FLOW_TOOLTIPS = {
    "present_value": {
        "title": "Present Value", 
        "formula": "Future Cash Flow ÷ (1 + Discount Rate)^Year",
        "explanation": "Current value of future cash flows, discounted by the cost of capital.",
        "calculation": "Each year's cash flow divided by (1 + Cost of Capital)^Year Number"
    },
    
    "cumulative_npv": {
        "title": "Cumulative NPV",
        "formula": "Sum of all Present Values through current year",
        "explanation": "Running total of present values showing financial position over time.",
        "calculation": "Sum of PV of Year 1 through PV of Current Year"
    },
    
    "cash_flow_difference": {
        "title": "Annual Cash Flow Difference",
        "formula": "Ownership Cash Flow - Rental Cash Flow", 
        "explanation": "Year-by-year comparison of cash requirements between scenarios.",
        "calculation": "Total ownership costs (negative) minus total rental costs (negative) for each year"
    }
}

# Terminal Value Analysis Tooltips
TERMINAL_VALUE_TOOLTIPS = {
    "property_appreciation": {
        "title": "Property Appreciation",
        "formula": "Purchase Price × (1 + Market Appreciation Rate)^Years",
        "explanation": "Estimated future property value based on market appreciation assumptions. Considers both land and building appreciation.",
        "calculation": "Purchase Price × (1 + Market Appreciation Rate %)^Analysis Period. Land typically appreciates faster than buildings, which depreciate over time."
    },
    
    "remaining_loan_balance": {
        "title": "Remaining Loan Balance",
        "formula": "Outstanding principal after N years of payments",
        "explanation": "Amount still owed on the mortgage at the end of the analysis period.",
        "calculation": "Calculated using standard amortization schedule based on original loan terms"
    },
    
    "net_equity": {
        "title": "Net Equity Position", 
        "formula": "Property Value - Remaining Loan Balance",
        "explanation": "Owner's equity in the property at the end of the analysis period.",
        "calculation": "Appreciated Property Value - Outstanding Mortgage Balance"
    },
    
    "alternative_investment": {
        "title": "Alternative Investment Value",
        "formula": "Initial Investment × (1 + Investment Return Rate)^Years",
        "explanation": "Value of alternative investment for rental scenario using saved down payment. Represents opportunity cost of not investing the down payment elsewhere.",
        "calculation": "Down Payment Amount × (1 + Cost of Capital %)^Analysis Period. Assumes the down payment could earn your cost of capital rate in alternative investments."
    }
}

# Comprehensive tooltip dictionary
ALL_CALCULATION_TOOLTIPS = {
    **NPV_TOOLTIPS,
    **ANNUAL_COST_TOOLTIPS, 
    **CASH_FLOW_TOOLTIPS,
    **TERMINAL_VALUE_TOOLTIPS
}


def get_calculation_tooltip(calculation_key: str) -> Optional[Dict[str, str]]:
    """
    Get tooltip information for a specific calculation
    
    Args:
        calculation_key: Key identifying the calculation
        
    Returns:
        Dictionary with tooltip information or None if not found
    """
    return ALL_CALCULATION_TOOLTIPS.get(calculation_key)


def display_calculation_tooltip(calculation_key: str, custom_help_text: str = None) -> str:
    """
    Get formatted help text for a calculation to use in Streamlit components
    
    Args:
        calculation_key: Key identifying the calculation
        custom_help_text: Optional custom text to append
        
    Returns:
        Formatted help text string
    """
    tooltip = get_calculation_tooltip(calculation_key)
    
    if not tooltip:
        return custom_help_text or "Calculation details not available"
    
    help_text = f"""
**{tooltip['title']}**

📐 **Formula**: {tooltip['formula']}

💡 **Explanation**: {tooltip['explanation']}

🔢 **Calculation**: {tooltip['calculation']}
    """.strip()
    
    if custom_help_text:
        help_text += f"\n\n📝 **Additional Notes**: {custom_help_text}"
    
    return help_text


def create_calculation_help_button(calculation_key: str, button_text: str = "ℹ️") -> None:
    """
    Create an expandable help section for a calculation
    
    Args:
        calculation_key: Key identifying the calculation
        button_text: Text to display on the help button
    """
    tooltip = get_calculation_tooltip(calculation_key)
    
    if not tooltip:
        return
    
    with st.expander(f"{button_text} {tooltip['title']} - How is this calculated?", expanded=False):
        st.markdown(f"**Formula**: `{tooltip['formula']}`")
        st.markdown(f"**Explanation**: {tooltip['explanation']}")  
        st.markdown(f"**Calculation Details**: {tooltip['calculation']}")


def add_metric_with_tooltip(
    label: str,
    value: str, 
    calculation_key: str,
    delta: str = None,
    delta_color: str = "normal"
) -> None:
    """
    Create a metric widget with integrated calculation tooltip
    
    Args:
        label: Metric label
        value: Metric value to display
        calculation_key: Key for the calculation tooltip
        delta: Optional delta value
        delta_color: Delta color ("normal", "inverse", "off")
    """
    tooltip_text = display_calculation_tooltip(calculation_key)
    
    # Create metric with help text
    st.metric(
        label=label,
        value=value,
        delta=delta,
        delta_color=delta_color,
        help=tooltip_text
    )


def create_detailed_calculation_expander(
    title: str, 
    calculation_keys: list,
    values: Dict[str, Any] = None
) -> None:
    """
    Create an expander section with multiple calculation explanations
    
    Args:
        title: Expander title
        calculation_keys: List of calculation keys to explain
        values: Optional dictionary of actual values to show
    """
    with st.expander(f"📊 {title} - Calculation Details", expanded=False):
        for key in calculation_keys:
            tooltip = get_calculation_tooltip(key)
            if tooltip:
                st.markdown(f"### {tooltip['title']}")
                st.markdown(f"**Formula**: `{tooltip['formula']}`")
                st.markdown(f"**Explanation**: {tooltip['explanation']}")
                st.markdown(f"**Calculation**: {tooltip['calculation']}")
                
                if values and key in values:
                    if values[key] == "Calculated annually for each scenario":
                        st.markdown(f"**Note**: {values[key]}")
                    else:
                        st.markdown(f"**Current Value**: {values[key]}")
                
                st.markdown("---")


# Contextual tooltip helpers for specific analysis sections

def get_npv_analysis_tooltips() -> Dict[str, str]:
    """Get tooltips specifically for NPV analysis results"""
    return {
        "npv_difference": display_calculation_tooltip("npv_difference"),
        "ownership_npv": display_calculation_tooltip("ownership_npv"),
        "rental_npv": display_calculation_tooltip("rental_npv"),
        "initial_investment": display_calculation_tooltip("initial_investment"),
        "terminal_value": display_calculation_tooltip("terminal_value")
    }

def get_annual_costs_tooltips() -> Dict[str, str]:
    """Get tooltips specifically for annual costs breakdown"""
    return {
        "mortgage_payment": display_calculation_tooltip("mortgage_payment"),
        "property_taxes": display_calculation_tooltip("property_taxes"), 
        "insurance_cost": display_calculation_tooltip("insurance_cost"),
        "maintenance_cost": display_calculation_tooltip("maintenance_cost"),
        "annual_rent": display_calculation_tooltip("annual_rent"),
        "tax_benefits": display_calculation_tooltip("tax_benefits")
    }

def get_cash_flow_tooltips() -> Dict[str, str]:
    """Get tooltips specifically for cash flow analysis"""
    return {
        "present_value": display_calculation_tooltip("present_value"),
        "cumulative_npv": display_calculation_tooltip("cumulative_npv"),
        "cash_flow_difference": display_calculation_tooltip("cash_flow_difference")
    }


# Examples of usage in components:
"""
# In dashboard components:
add_metric_with_tooltip(
    label="NPV Difference",
    value=format_currency(npv_difference),
    calculation_key="npv_difference",
    delta=f"{confidence} confidence"
)

# In comparison tables:
st.dataframe(
    df,
    column_config={
        "NPV": st.column_config.NumberColumn(
            "NPV",
            help=display_calculation_tooltip("ownership_npv"),
            format="$%.0f"
        )
    }
)

# In detailed sections:
create_detailed_calculation_expander(
    "NPV Analysis Breakdown",
    ["npv_difference", "ownership_npv", "rental_npv"],
    {"npv_difference": "$150,000", "ownership_npv": "$-2,450,000"}
)
"""