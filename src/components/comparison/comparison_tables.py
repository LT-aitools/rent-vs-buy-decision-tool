"""
Comparison Tables
Professional table components for detailed rent vs buy comparisons

This module provides specialized table components for detailed comparisons:
- Annual costs breakdown tables
- Cash flow comparison tables  
- Investment summary tables
- Table formatting utilities
- Visual indicators for better/worse outcomes
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
import plotly.graph_objects as go

from ..charts.core_charts import format_currency


def format_comparison_table(
    df: pd.DataFrame,
    highlight_column: Optional[str] = None,
    highlight_condition: str = "max"
) -> pd.DataFrame:
    """
    Format a comparison table with professional styling
    
    Args:
        df: DataFrame to format
        highlight_column: Column to highlight best values
        highlight_condition: "max" or "min" for best value determination
    
    Returns:
        Formatted DataFrame
    """
    # Apply basic formatting
    styled_df = df.copy()
    
    # Format currency columns
    currency_columns = [col for col in df.columns if any(
        keyword in col.lower() for keyword in ['cost', 'npv', 'value', 'investment', 'payment']
    )]
    
    for col in currency_columns:
        if col in styled_df.columns:
            try:
                # Convert to numeric if string
                if styled_df[col].dtype == 'object':
                    # Clean up string values before conversion
                    cleaned_values = styled_df[col].str.replace('$', '').str.replace(',', '').str.strip()
                    styled_df[col] = pd.to_numeric(cleaned_values, errors='coerce')
                
                # Format currency values with proper error handling
                styled_df[col] = styled_df[col].apply(lambda x: format_currency(x) if pd.notna(x) and x != 0 else 'N/A')
                
            except AttributeError as e:
                # Handle issues with string operations on non-string columns
                st.warning(f"⚠️ Column '{col}' formatting issue: Cannot apply string operations to {styled_df[col].dtype} type")
                continue
            except Exception as e:
                # Handle other formatting errors
                st.warning(f"⚠️ Could not format column '{col}': {str(e)}")
                continue
    
    return styled_df


def add_visual_indicators(
    df: pd.DataFrame,
    comparison_columns: List[str],
    better_when: str = "lower"
) -> pd.DataFrame:
    """
    Add visual indicators to show which option is better
    
    Args:
        df: DataFrame to enhance
        comparison_columns: Columns to compare
        better_when: "lower" or "higher" values are better
    
    Returns:
        DataFrame with visual indicators
    """
    enhanced_df = df.copy()
    
    if len(comparison_columns) == 2 and len(enhanced_df) > 0:
        col1, col2 = comparison_columns
        
        for index, row in enhanced_df.iterrows():
            try:
                # Extract numeric values for comparison with improved error handling
                val1_str = str(row[col1]).replace('$', '').replace(',', '').replace('+', '').strip()
                val2_str = str(row[col2]).replace('$', '').replace(',', '').replace('+', '').strip()
                
                # Handle common non-numeric strings
                if val1_str.lower() in ['n/a', 'na', 'none', '']:
                    val1_str = '0'
                if val2_str.lower() in ['n/a', 'na', 'none', '']:
                    val2_str = '0'
                
                val1 = float(val1_str)
                val2 = float(val2_str)
                
                # Determine better option
                if better_when == "lower":
                    if val1 < val2:
                        enhanced_df.at[index, col1] = f"🟢 {row[col1]}"
                        enhanced_df.at[index, col2] = f"🔴 {row[col2]}"
                    elif val2 < val1:
                        enhanced_df.at[index, col1] = f"🔴 {row[col1]}"
                        enhanced_df.at[index, col2] = f"🟢 {row[col2]}"
                    else:
                        enhanced_df.at[index, col1] = f"🟡 {row[col1]}"
                        enhanced_df.at[index, col2] = f"🟡 {row[col2]}"
                else:  # higher is better
                    if val1 > val2:
                        enhanced_df.at[index, col1] = f"🟢 {row[col1]}"
                        enhanced_df.at[index, col2] = f"🔴 {row[col2]}"
                    elif val2 > val1:
                        enhanced_df.at[index, col1] = f"🔴 {row[col1]}"
                        enhanced_df.at[index, col2] = f"🟢 {row[col2]}"
                    else:
                        enhanced_df.at[index, col1] = f"🟡 {row[col1]}"
                        enhanced_df.at[index, col2] = f"🟡 {row[col2]}"
                        
            except ValueError as e:
                # Log specific conversion errors for debugging
                error_msg = f"Could not convert values for comparison in row {index}: '{val1_str}' vs '{val2_str}'"
                st.warning(f"⚠️ Data conversion issue: {error_msg}")
                # Leave values as-is without indicators
                continue
            except KeyError as e:
                # Handle missing column issues
                st.error(f"❌ Missing column in data: {e}")
                continue
            except Exception as e:
                # Handle any other unexpected errors
                st.error(f"❌ Unexpected error processing row {index}: {str(e)}")
                continue
    
    return enhanced_df


def create_annual_costs_table(
    ownership_flows: List[Dict[str, float]],
    rental_flows: List[Dict[str, float]],
    max_years: int = 10
) -> None:
    """
    Create detailed annual costs breakdown table
    
    Args:
        ownership_flows: Ownership cash flow data
        rental_flows: Rental cash flow data
        max_years: Maximum number of years to display
    """
    if not ownership_flows or not rental_flows:
        st.error("Annual costs data not available")
        return
    
    st.subheader("📊 Annual Costs Breakdown")
    
    # Prepare table data
    table_data = []
    years_to_show = min(max_years, len(ownership_flows), len(rental_flows))
    
    for i in range(years_to_show):
        ownership_flow = ownership_flows[i]
        rental_flow = rental_flows[i]
        
        row = {
            'Year': ownership_flow['year'],
            'Ownership Total': abs(ownership_flow['net_cash_flow']),
            'Mortgage Payment': ownership_flow.get('mortgage_payment', 0),
            'Property Taxes': ownership_flow.get('property_taxes', 0),
            'Insurance': ownership_flow.get('insurance', 0),
            'Maintenance': ownership_flow.get('maintenance', 0),
            'Other Costs': (
                ownership_flow.get('property_management', 0) +
                ownership_flow.get('capex_reserve', 0) +
                ownership_flow.get('obsolescence_cost', 0)
            ),
            'Tax Benefits': ownership_flow.get('tax_benefits', 0),
            'Rental Total': abs(rental_flow['net_cash_flow']),
            'Annual Difference': abs(ownership_flow['net_cash_flow']) - abs(rental_flow['net_cash_flow'])
        }
        table_data.append(row)
    
    df = pd.DataFrame(table_data)
    
    # Format the table
    formatted_df = format_comparison_table(df)
    
    # Add visual indicators for better option
    indicator_df = add_visual_indicators(
        formatted_df, 
        ['Ownership Total', 'Rental Total'], 
        better_when="lower"
    )
    
    # Display table
    st.dataframe(
        indicator_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Year": st.column_config.NumberColumn("Year", format="%d"),
            "Ownership Total": st.column_config.TextColumn("Ownership Total", width="medium"),
            "Mortgage Payment": st.column_config.TextColumn("Mortgage", width="small"),
            "Property Taxes": st.column_config.TextColumn("Taxes", width="small"),
            "Insurance": st.column_config.TextColumn("Insurance", width="small"),
            "Maintenance": st.column_config.TextColumn("Maintenance", width="small"),
            "Other Costs": st.column_config.TextColumn("Other", width="small"),
            "Tax Benefits": st.column_config.TextColumn("Tax Benefits", width="small"),
            "Rental Total": st.column_config.TextColumn("Rental Total", width="medium"),
            "Annual Difference": st.column_config.TextColumn("Difference", width="medium")
        }
    )
    
    # Add summary
    total_ownership = sum(abs(f['net_cash_flow']) for f in ownership_flows[:years_to_show])
    total_rental = sum(abs(f['net_cash_flow']) for f in rental_flows[:years_to_show])
    total_difference = total_ownership - total_rental
    
    st.markdown(f"""
    **{years_to_show}-Year Totals:**
    - Ownership: {format_currency(total_ownership)}
    - Rental: {format_currency(total_rental)}
    - Difference: {format_currency(total_difference)} ({'Ownership costs more' if total_difference > 0 else 'Rental costs more'})
    """)


def create_cash_flow_comparison_table(
    ownership_flows: List[Dict[str, float]],
    rental_flows: List[Dict[str, float]],
    analysis_results: Dict[str, Any]
) -> None:
    """
    Create cash flow comparison table with NPV calculations
    
    Args:
        ownership_flows: Ownership cash flows
        rental_flows: Rental cash flows
        analysis_results: Analysis results with discount rate
    """
    if not ownership_flows or not rental_flows:
        st.error("Cash flow comparison data not available")
        return
    
    st.subheader("💰 Cash Flow Comparison")
    
    cost_of_capital = analysis_results.get('cost_of_capital', 8.0) / 100
    
    # Prepare comparison data
    table_data = []
    cumulative_ownership_pv = 0
    cumulative_rental_pv = 0
    
    for i, (ownership_flow, rental_flow) in enumerate(zip(ownership_flows, rental_flows)):
        year = ownership_flow['year']
        
        # Annual cash flows (negative = outflow)
        ownership_cf = ownership_flow['net_cash_flow']
        rental_cf = rental_flow['net_cash_flow']
        
        # Present value calculations
        discount_factor = (1 + cost_of_capital) ** year
        ownership_pv = ownership_cf / discount_factor
        rental_pv = rental_cf / discount_factor
        
        cumulative_ownership_pv += ownership_pv
        cumulative_rental_pv += rental_pv
        
        row = {
            'Year': year,
            'Ownership Cash Flow': ownership_cf,
            'Rental Cash Flow': rental_cf,
            'Annual Difference': ownership_cf - rental_cf,
            'Ownership PV': ownership_pv,
            'Rental PV': rental_pv,
            'PV Difference': ownership_pv - rental_pv,
            'Cumulative PV Difference': cumulative_ownership_pv - cumulative_rental_pv
        }
        table_data.append(row)
    
    df = pd.DataFrame(table_data)
    
    # Format currency columns
    currency_cols = ['Ownership Cash Flow', 'Rental Cash Flow', 'Annual Difference', 
                    'Ownership PV', 'Rental PV', 'PV Difference', 'Cumulative PV Difference']
    
    for col in currency_cols:
        df[col] = df[col].apply(lambda x: format_currency(x))
    
    # Display table (first 10 years)
    display_df = df.head(10)
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Year": st.column_config.NumberColumn("Year", format="%d"),
            "Ownership Cash Flow": st.column_config.TextColumn("Ownership CF", width="medium"),
            "Rental Cash Flow": st.column_config.TextColumn("Rental CF", width="medium"),
            "Annual Difference": st.column_config.TextColumn("CF Difference", width="medium"),
            "Ownership PV": st.column_config.TextColumn("Ownership PV", width="medium"),
            "Rental PV": st.column_config.TextColumn("Rental PV", width="medium"),
            "PV Difference": st.column_config.TextColumn("PV Difference", width="medium"),
            "Cumulative PV Difference": st.column_config.TextColumn("Cumulative PV Diff", width="medium")
        }
    )
    
    # Add terminal values
    st.markdown("**Terminal Values (Present Value):**")
    col1, col2 = st.columns(2)
    
    with col1:
        ownership_terminal = analysis_results.get('ownership_terminal_value', 0)
        st.markdown(f"- Ownership Terminal Value: {format_currency(ownership_terminal)}")
    
    with col2:
        rental_terminal = analysis_results.get('rental_terminal_value', 0) 
        st.markdown(f"- Rental Terminal Value: {format_currency(rental_terminal)}")


def create_investment_summary_table(analysis_results: Dict[str, Any]) -> None:
    """
    Create investment summary comparison table
    
    Args:
        analysis_results: Complete analysis results
    """
    st.subheader("📈 Investment Summary")
    
    # Prepare summary data
    summary_data = [
        {
            'Component': 'Initial Investment',
            'Ownership': analysis_results.get('ownership_initial_investment', 0),
            'Rental': analysis_results.get('rental_initial_investment', 0),
            'Advantage': 'Lower is Better'
        },
        {
            'Component': 'Terminal Value (PV)',
            'Ownership': analysis_results.get('ownership_terminal_value', 0),
            'Rental': analysis_results.get('rental_terminal_value', 0),
            'Advantage': 'Higher is Better'
        },
        {
            'Component': 'Total NPV',
            'Ownership': analysis_results.get('ownership_npv', 0),
            'Rental': analysis_results.get('rental_npv', 0),
            'Advantage': 'Higher is Better'
        }
    ]
    
    # Calculate differences and winners
    for item in summary_data:
        ownership_val = item['Ownership']
        rental_val = item['Rental']
        difference = ownership_val - rental_val
        item['Difference'] = difference
        
        if item['Advantage'] == 'Higher is Better':
            item['Winner'] = 'Ownership' if difference > 0 else 'Rental' if difference < 0 else 'Tie'
        else:  # Lower is Better
            item['Winner'] = 'Rental' if difference > 0 else 'Ownership' if difference < 0 else 'Tie'
    
    # Create DataFrame
    df = pd.DataFrame(summary_data)
    
    # Format currency columns
    df['Ownership'] = df['Ownership'].apply(lambda x: format_currency(x))
    df['Rental'] = df['Rental'].apply(lambda x: format_currency(x))
    df['Difference'] = df['Difference'].apply(lambda x: format_currency(x))
    
    # Add winner indicators
    df['Winner'] = df['Winner'].apply(lambda x: f"🏆 {x}" if x != 'Tie' else "⚖️ Tie")
    
    # Display table
    st.dataframe(
        df[['Component', 'Ownership', 'Rental', 'Difference', 'Winner']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Component": st.column_config.TextColumn("Component", width="medium"),
            "Ownership": st.column_config.TextColumn("🏠 Ownership", width="medium"),
            "Rental": st.column_config.TextColumn("🏢 Rental", width="medium"),
            "Difference": st.column_config.TextColumn("Difference", width="medium"),
            "Winner": st.column_config.TextColumn("Advantage", width="small")
        }
    )
    
    # Overall winner
    npv_difference = analysis_results.get('npv_difference', 0)
    overall_winner = "Ownership" if npv_difference > 0 else "Rental"
    recommendation = analysis_results.get('recommendation', 'UNKNOWN')
    
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, #FF6B6B 0%, #4ECDC4 100%); 
                padding: 1rem; border-radius: 0.5rem; margin-top: 1rem; color: white; text-align: center;">
        <strong>Overall Winner: {overall_winner} | Final Recommendation: {recommendation}</strong>
    </div>
    """, unsafe_allow_html=True)


def create_sensitivity_comparison_table(
    sensitivity_results: Dict[str, Dict[str, float]],
    base_npv_difference: float
) -> None:
    """
    Create sensitivity analysis comparison table
    
    Args:
        sensitivity_results: Sensitivity analysis results
        base_npv_difference: Base case NPV difference
    """
    st.subheader("📊 Sensitivity Analysis Summary")
    
    if not sensitivity_results:
        st.info("No sensitivity analysis results available")
        return
    
    # Prepare sensitivity data
    sensitivity_data = []
    
    for parameter, results in sensitivity_results.items():
        if isinstance(results, dict) and len(results) >= 2:
            npv_values = [result['npv_difference'] if isinstance(result, dict) else result 
                         for result in results.values()]
            
            min_npv = min(npv_values)
            max_npv = max(npv_values)
            range_impact = max_npv - min_npv
            
            sensitivity_data.append({
                'Parameter': parameter.replace('_', ' ').title(),
                'Min NPV Impact': min_npv - base_npv_difference,
                'Max NPV Impact': max_npv - base_npv_difference,
                'Total Range': range_impact,
                'Sensitivity Level': 'High' if range_impact > 500000 else 'Medium' if range_impact > 100000 else 'Low'
            })
    
    if not sensitivity_data:
        st.info("Insufficient sensitivity data for analysis")
        return
    
    # Sort by total range (most sensitive first)
    sensitivity_data.sort(key=lambda x: x['Total Range'], reverse=True)
    
    df = pd.DataFrame(sensitivity_data)
    
    # Format currency columns
    currency_cols = ['Min NPV Impact', 'Max NPV Impact', 'Total Range']
    for col in currency_cols:
        df[col] = df[col].apply(lambda x: format_currency(x))
    
    # Add sensitivity level indicators
    df['Sensitivity Level'] = df['Sensitivity Level'].apply(
        lambda x: f"🔥 {x}" if x == 'High' else f"📊 {x}" if x == 'Medium' else f"📈 {x}"
    )
    
    # Display table
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Parameter": st.column_config.TextColumn("Parameter", width="medium"),
            "Min NPV Impact": st.column_config.TextColumn("Min Impact", width="medium"),
            "Max NPV Impact": st.column_config.TextColumn("Max Impact", width="medium"),
            "Total Range": st.column_config.TextColumn("Total Range", width="medium"),
            "Sensitivity Level": st.column_config.TextColumn("Sensitivity", width="small")
        }
    )
    
    st.markdown("💡 **Key Insight**: Parameters with higher sensitivity levels have greater impact on the final recommendation.")


# Example usage and testing
if __name__ == "__main__":
    # This would be used for testing the comparison table components
    pass