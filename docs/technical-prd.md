# Updated PRD: Rent vs. Buy Real Estate Decision Tool (Streamlit Implementation)

## Executive Summary

A comprehensive financial decision-support tool built with Streamlit, enabling global subsidiaries to evaluate real estate acquisition versus rental decisions with **hold-forever investment strategy**. Prioritizes rapid development, zero hosting costs, and immediate business value with mathematically accurate financial modeling.

## Technical Architecture

### Technology Stack (Updated 2025)
- **Backend/Frontend**: Streamlit 1.45.1+ (Latest with enhanced container features)
- **Python Version**: 3.10+ (Required for NumPy 2.3+ compatibility)
- **Calculations**: pandas 2.3.1 + numpy 2.3.2 for financial modeling
- **Visualization**: Streamlit native charts + plotly 5.24.1 for advanced visualizations
- **Export**: openpyxl 3.1.5 for Excel functionality with formatted reporting
- **Deployment**: Streamlit Community Cloud (FREE with 12-hour sleep policy)
- **Storage**: No backend - session state only for data privacy

### Cost Structure: $0/month
- Streamlit Community Cloud: Free
- GitHub hosting: Free
- No database or server costs
- Optional custom domain: ~$15/year

## MVP Requirements (Week 1-3)

### Core Input Interface

```python
# Updated Streamlit sidebar with all corrected input fields
with st.sidebar:
    st.header("Project Information")
    project_name = st.text_input("Project Name", value=f"Property Analysis {datetime.now().strftime('%Y-%m-%d')}")
    location = st.text_input("Location/Address")
    analyst_name = st.text_input("Analyst Name")
    currency = st.selectbox("Currency", ["USD", "EUR", "GBP", "CAD", "AUD", "ILS", "LEI", "PLN"])
    
    st.header("Property & Market Information")
    property_type = st.selectbox("Property Type", ["Warehouse", "Distribution Center", "Manufacturing", "Office", "Mixed Use"])
    total_property_size = st.number_input("Total Property Size (sq meters)", min_value=1000)
    current_space_needed = st.number_input("Current Space Needed (sq meters)", min_value=500, max_value=total_property_size)
    market_appreciation_rate = st.slider("Market Appreciation Rate (%)", 0.0, 15.0, 3.0, 0.1)
    
    st.header("Financial Parameters - Purchase")
    purchase_price = st.number_input("Purchase Price", min_value=50000)
    transaction_costs = st.number_input("Transaction Costs", value=int(purchase_price * 0.05))
    down_payment_pct = st.slider("Down Payment %", 0, 100, 30)
    interest_rate = st.slider("Interest Rate (%)", 0.0, 20.0, 5.0, 0.1)
    loan_term = st.number_input("Loan Term (years)", 0, 30, 20)
    property_tax_rate = st.slider("Property Tax Rate (%)", 0.0, 10.0, 1.2, 0.1)
    property_tax_escalation = st.slider("Property Tax Escalation Rate (%)", 0.0, 10.0, 2.0, 0.1)
    insurance_cost = st.number_input("Annual Insurance", value=5000)
    annual_maintenance = st.number_input("Annual Maintenance", value=int(purchase_price * 0.02))
    property_management = st.number_input("Property Management Fee", value=0)
    land_value_pct = st.slider("Land Value %", 10, 50, 25)
    space_improvement_cost = st.number_input("Space Improvement Cost (per sq meter)", value=50)
    
    st.header("Hold-Forever Parameters")
    capex_reserve = st.slider("Long-term CapEx Reserve (%)", 0.0, 10.0, 1.5, 0.1)
    property_upgrade_cycle = st.number_input("Property Upgrade Cycle (years)", 5, 50, 15)
    obsolescence_risk = st.slider("Obsolescence Risk Factor (%)", 0.0, 5.0, 0.5, 0.1)
    
    st.header("Financial Parameters - Rental")
    current_annual_rent = st.number_input("Current Annual Rent", min_value=1000)
    rent_increase_rate = st.slider("Rent Increase Rate (%)", 0.0, 15.0, 3.0, 0.1)
    security_deposit = st.number_input("Security Deposit", value=int(current_annual_rent/6))
    rental_commission = st.number_input("Rental Commission", value=int(current_annual_rent/12))
    lease_break_penalty = st.number_input("Lease Break Penalty", value=int(current_annual_rent/2))
    moving_costs = st.number_input("Moving Costs", value=0)
    
    st.header("Operational Parameters")
    analysis_period = st.number_input("Analysis Period (years)", 0, 100, 25)
    growth_rate = st.slider("Business Growth Rate (%)", -5.0, 25.0, 5.0, 0.1)
    future_expansion_year = st.selectbox("Future Expansion Year", ["Never"] + [f"Year {i}" for i in range(1, 26)])
    additional_space_needed = st.number_input("Additional Space Needed (sq meters)", value=0)
    subletting_potential = st.checkbox("Subletting Potential", value=False)
    if subletting_potential:
        subletting_rate = st.number_input("Subletting Rate (per sq meter)", value=0)
        subletting_occupancy = st.slider("Subletting Occupancy %", 0, 100, 85)
    cost_of_capital = st.slider("Cost of Capital (%)", 0.0, 20.0, 8.0, 0.1)
    
    st.header("Tax & Accounting")
    corporate_tax_rate = st.slider("Corporate Tax Rate (%)", 0.0, 50.0, 25.0, 0.1)
    depreciation_period = st.number_input("Depreciation Period (years)", 0, 50, 39)
    interest_deductible = st.checkbox("Interest Deductible", value=True)
    property_tax_deductible = st.checkbox("Property Tax Deductible", value=True)
    rent_deductible = st.checkbox("Rent Deductible", value=True)
    inflation_rate = st.slider("Inflation Rate (%)", 0.0, 20.0, 3.0, 0.1)
```

## Key Calculations (Updated for Hold-Forever Strategy)

### 1. Hold-Forever Wealth Analysis (Primary Model)
- Compare perpetual cash flows with terminal wealth accumulation
- **Ownership**: Builds equity through appreciation + debt paydown
- **Rental**: No asset wealth accumulated
- Factor in all ownership costs including CapEx reserves and obsolescence risk

### 2. Corrected Total Cost of Ownership Analysis
```python
# Mortgage calculation with edge case handling
if down_payment_pct == 100:
    annual_mortgage_payment = 0
elif interest_rate == 0:
    annual_mortgage_payment = loan_amount / loan_term
else:
    monthly_payment = np.pmt(interest_rate/12/100, loan_term*12, -loan_amount)
    annual_mortgage_payment = monthly_payment * 12

# Annual costs with proper Year-1 indexing
for year in range(1, analysis_period + 1):
    property_taxes = purchase_price * property_tax_rate/100 * (1 + property_tax_escalation/100)**(year-1)
    insurance = insurance_cost * (1 + inflation_rate/100)**(year-1)
    maintenance = annual_maintenance * (1 + inflation_rate/100)**(year-1)
    capex_reserve_cost = purchase_price * capex_reserve/100 * (1 + inflation_rate/100)**(year-1)
    obsolescence_cost = purchase_price * obsolescence_risk/100 * (1 + inflation_rate/100)**(year-1)
    
    # Property upgrade costs in cycle years
    property_upgrade_cost = 0
    if year % property_upgrade_cycle == 0:
        building_value = purchase_price * (1 - land_value_pct/100)
        property_upgrade_cost = building_value * 0.02
```

### 3. Terminal Wealth Analysis
```python
# Corrected terminal value calculation
land_value = purchase_price * land_value_pct / 100
building_value = purchase_price - land_value

land_value_end = land_value * (1 + market_appreciation_rate/100)**analysis_period
accumulated_depreciation = min(building_value, building_value * analysis_period / depreciation_period)
depreciated_building = building_value - accumulated_depreciation
building_value_end = depreciated_building * (1 + market_appreciation_rate/100)**analysis_period

terminal_property_value = land_value_end + building_value_end
net_property_equity = terminal_property_value - remaining_loan_balance

# Rental terminal value
rental_terminal_value = security_deposit * (1 + inflation_rate/100)**analysis_period
```

## Output Dashboard (Updated)

### Main Dashboard Layout
```python
# Executive summary with corrected metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Recommendation", recommendation, delta=confidence_level)
with col2:
    st.metric("NPV Advantage", f"${npv_difference:,.0f}", delta=f"{analysis_period} years")
with col3:
    st.metric("Operational Break-Even", f"{operational_breakeven:.1f} years" if operational_breakeven else "Never")
with col4:
    st.metric("Year 1 Cash Impact", f"${year1_difference:+,.0f}")

# Hold-forever wealth accumulation chart
st.subheader("Wealth Accumulation Analysis (Hold-Forever Strategy)")
fig = create_wealth_accumulation_chart(ownership_wealth, rental_wealth, years)
st.plotly_chart(fig)

# Annual cash flow comparison
st.subheader("Annual Cash Flow Analysis")
cash_flow_df = create_cashflow_comparison(ownership_costs, rental_costs, years)
st.line_chart(cash_flow_df)
```

## Enhanced Features (Week 3-4)

### Sensitivity Analysis (Updated)
```python
# Multi-variable sensitivity analysis
st.header("Sensitivity Analysis")
interest_range = st.slider("Interest Rate Range (+/-)", 0.5, 3.0, 1.0, 0.5)
rent_range = st.slider("Rent Increase Range (+/-)", 1.0, 5.0, 2.0, 0.5)
appreciation_range = st.slider("Appreciation Rate Range (+/-)", 1.0, 5.0, 2.0, 0.5)

# Generate comprehensive sensitivity matrix
sensitivity_df = calculate_multi_sensitivity(base_inputs, interest_range, rent_range, appreciation_range)
st.dataframe(sensitivity_df.style.background_gradient(cmap='RdYlGn'))
```

## Excel Export (Enhanced)
```python
@st.cache_data
def create_comprehensive_excel_report(calculations_df, inputs_dict, sensitivity_results):
    """Create detailed Excel report with all corrected calculations"""
    wb = openpyxl.Workbook()
    
    # Executive Summary Sheet
    ws1 = wb.active
    ws1.title = "Executive Summary"
    # Include corrected NPV, operational break-even, wealth analysis
    
    # Detailed Calculations Sheet  
    ws2 = wb.create_sheet("Calculations")
    # Year-by-year cash flows with all cost components
    
    # Hold-Forever Analysis Sheet
    ws3 = wb.create_sheet("Wealth Analysis")
    # Terminal value breakdown, equity accumulation
    
    # Sensitivity Analysis Sheet
    ws4 = wb.create_sheet("Sensitivity")
    # Multi-variable sensitivity results
    
    return wb
```

## Business Features Integration

### Risk Analysis (Enhanced for Hold-Forever)
- **Long-term Property Risks**: Obsolescence, major renovation cycles
- **Market Risk Scenarios**: Appreciation rate sensitivity
- **Operational Risk**: Space expansion needs and timing
- **Financial Risk**: Interest rate and tax policy changes

### Collaboration Features
- **URL parameter sharing**: Complete scenario preservation
- **Export capabilities**: Professional Excel reports for stakeholders
- **Version tracking**: Session-based scenario management

## Development Timeline (Updated)

### Week 1: Core MVP
- Streamlit app structure with corrected input forms
- **Corrected financial calculations** with all edge cases
- Basic validation and error handling
- Hold-forever wealth analysis implementation

### Week 2: Analysis Enhancement  
- NPV calculations with proper terminal value logic
- **Operational break-even analysis** (not sale-based)
- Year-by-year cash flow tables
- Basic visualization dashboard

### Week 3: Advanced Features
- **Multi-variable sensitivity analysis**
- Interactive charts and advanced visualizations
- Comprehensive Excel export with formatted reports
- Enhanced UI/UX with professional styling

### Week 4: Polish & Deploy
- Edge case handling and validation improvements
- **User testing with corrected calculations**
- Streamlit Community Cloud deployment
- Final refinements and documentation

## Cost-Optimized Implementation Plan

**Total Cost: $0/month**
- **Development**: Internal time only
- **Hosting**: Streamlit Community Cloud (free)
- **Domain**: Optional custom domain (~$10/year)  
- **Storage**: No database needed

### Migration Path (if scaling needed later)
1. **Phase 1**: Streamlit MVP (immediate value)
2. **Phase 2**: Validate with users, gather requirements
3. **Phase 3**: Scale to React frontend if needed (enterprise features)

## Advantages of This Approach

1. **Speed**: MVP ready in 2-3 weeks with corrected calculations
2. **Cost**: Zero ongoing operational costs
3. **Maintenance**: Minimal - Python dependencies only
4. **Features**: Rich functionality for financial analysis tools
5. **Validation**: Quick user feedback before larger investment
6. **Accuracy**: Mathematically sound hold-forever investment analysis

## Sample App Structure (Updated)

```
rent_vs_buy_tool/
├── app.py                    # Main Streamlit app with corrected UI
├── calculations.py           # All corrected financial calculation functions
├── visualizations.py         # Chart generation with hold-forever focus  
├── excel_export.py          # Enhanced Excel reporting
├── utils.py                 # Input validation and helper functions
├── requirements.txt         # Updated Python dependencies (3.10+)
├── .streamlit/
│   └── config.toml          # Professional theming configuration
└── README.md               # Documentation
```

## Updated requirements.txt:
```
python>=3.10,<3.14
streamlit>=1.45.0
pandas>=2.3.1
numpy>=2.3.0
plotly>=5.24.1
openpyxl>=3.1.5
```

The **corrected Streamlit approach** gives you a professional financial tool with zero hosting costs, mathematically accurate calculations, and proper hold-forever investment analysis - ready for immediate business use with global subsidiaries.