# Real Estate Decision Tool - Usage Guide

## 🚀 Quick Start

### Running the Application
```bash
cd /Users/Amos/wt-ui-components
streamlit run src/app.py
```

The application will start at `http://localhost:8501`

## 📱 User Interface Overview

### **Main Navigation**
The application has three main tabs:
1. **📊 Analysis Dashboard** - Primary input interface
2. **📤 Export & Share** - Data management
3. **❓ Help & Documentation** - User guidance

### **Sidebar Input Sections**
All input forms are organized in the sidebar with expandable sections:

#### 📋 **Project Information** (Always Expanded)
- Project Name, Location, Analyst Name
- Analysis Date, Currency Selection

#### 🏢 **Property & Market Information** (Always Expanded)  
- Property Type, Total Size, Current Space Needed
- Market Appreciation Rate

#### 💰 **Purchase Parameters** (Expandable)
- Purchase Price, Down Payment, Interest Rate
- Loan Term, Property Tax, Insurance
- Advanced parameters in sub-section

#### 🏠 **Rental Parameters** (Expandable)
- Current Annual Rent, Rent Increase Rate
- Security Deposit, Moving Costs

#### ⚙️ **Operational Parameters** (Expandable)
- Analysis Period, Growth Rate, Cost of Capital  
- Expansion Planning, Subletting Options

#### 📊 **Tax & Accounting Parameters** (Expandable)
- Corporate Tax Rate, Depreciation Period
- Tax Deductibility Options

## 🎯 How to Use

### **Step 1: Complete Required Fields**
Fill out all fields marked with (*) asterisk:
- Project Name, Location, Analyst Name
- Total Property Size, Current Space Needed
- Purchase Price, Current Annual Rent

### **Step 2: Review Validation**
- ✅ Green checkmarks = Section complete
- ⏳ Clock icons = Section pending
- Error messages appear in red
- Warnings appear in yellow
- Info messages appear in blue

### **Step 3: Monitor Progress**
- Progress bar shows completion percentage
- Section completion indicators in sidebar navigation
- Input summary updates in real-time

### **Step 4: Export & Share**
- Download input data as JSON for backup
- Reset all inputs to start over
- Import previously saved analysis

## 🔧 Professional Features

### **Smart Defaults**
- All fields have business-appropriate defaults
- Defaults based on Business PRD specifications
- Currency-specific formatting

### **Input Validation**
```
✅ Valid input accepted
⚠️ Warning: Unusual but acceptable value
❌ Error: Invalid input, must be corrected
ℹ️ Info: Helpful context or calculation
```

### **Professional Styling**
- Executive-grade appearance
- Responsive design for all devices
- Clean, modern interface
- Professional color scheme

### **Real-time Calculations**
- Rent per square meter automatically calculated
- Transaction costs computed as percentage
- Loan amounts updated dynamically
- Progress tracking in real-time

## 💡 Tips for Best Results

### **Input Strategy**
1. Start with **Project Information** - sets context
2. Complete **Property & Market** - defines the analysis scope  
3. Fill **Purchase Parameters** - financing details
4. Complete **Rental Parameters** - current situation
5. Configure **Operational Parameters** - business assumptions
6. Set **Tax & Accounting** - financial implications

### **Validation Best Practices**
- Address red error messages first
- Consider yellow warnings carefully  
- Use info messages for context
- Check cross-field relationships

### **Professional Usage**
- Use descriptive project names
- Include full property addresses
- Document analyst name for accountability
- Save/export data for future reference

## 🔍 Field Explanations

### **Key Business Terms**
- **Market Appreciation Rate**: Expected annual property value increase
- **Cost of Capital**: Company's discount rate for NPV calculations
- **CapEx Reserve**: Annual reserve for major property improvements
- **Obsolescence Risk**: Annual risk of property becoming unsuitable

### **Financial Parameters**
- **Down Payment %**: Equity percentage of purchase price
- **Transaction Costs**: Legal, inspection, broker fees
- **Property Tax Escalation**: Annual tax assessment increases
- **Subletting Potential**: Ability to rent excess space

## 📊 Data Export Options

### **JSON Export**
- Complete input parameter backup
- Shareable with colleagues
- Importable for future analysis
- Timestamp included for tracking

### **Coming Soon**
- Excel reports with full calculations
- PDF executive summaries  
- Detailed analysis charts
- Sensitivity analysis results

## 🆘 Troubleshooting

### **Common Issues**
- **Validation Errors**: Check all required fields are filled
- **Import Failures**: Verify JSON file format is correct
- **Performance**: Refresh browser if updates are slow
- **Mobile Issues**: Use landscape mode for best experience

### **Getting Help**
- Hover over ❓ icons for field explanations
- Review validation messages for specific guidance
- Check the Help & Documentation tab
- Refer to Business PRD for methodology details

---

**Ready to make professional real estate investment decisions! 🏢**