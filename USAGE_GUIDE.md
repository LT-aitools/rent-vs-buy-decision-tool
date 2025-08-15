# Real Estate Decision Tool - Usage Guide

## 🚀 Quick Start

### Accessing the Application

#### **🌐 Live Production App**
**Recommended**: Use the live application at:
https://rent-vs-buy-decision-tool-app.streamlit.app/

#### **💻 Local Development**
```bash
cd rent-vs-buy-decision-tool
streamlit run src/app.py
```
The application will start at `http://localhost:8501`

## 📱 User Interface Overview

### **Main Navigation**
The application has four main tabs:
1. **📝 Input Forms** - Data entry and configuration
2. **📊 Analysis Results** - Dashboard with analysis output and visualizations
3. **🔗 Data Integration** - Real-time market data status and configuration
4. **📤 Export & Sharing** - Professional reports and data export

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

### **Step 2: Run Financial Analysis**
Navigate to the **Analysis Results** tab and click **"Run Financial Analysis"** to:
- Generate NPV calculations and decision recommendations
- Create interactive visualizations and charts  
- Perform sensitivity analysis with tornado diagrams
- Compare rent vs. buy scenarios comprehensively

### **Step 3: Review Results**
In the **Analysis Results** tab you'll find:
- **Executive Summary** with clear buy/rent recommendation
- **Key Financial Metrics** including NPV difference and ROI
- **Advanced Analysis** with sensitivity analysis and scenario comparisons
- **Detailed Comparisons** with comprehensive financial breakdowns

### **Step 4: Export Professional Reports**
Navigate to **Export & Sharing** tab to:
- Generate executive-ready Excel reports with comprehensive data
- Download complete analysis as JSON for backup and sharing
- Access synchronized data that matches your current analysis inputs

## 🔧 Professional Features

### **Smart Defaults**
- All fields have business-appropriate defaults
- Defaults based on Business PRD specifications
- Currency-specific formatting

### **Analysis Features**
- **Sensitivity Analysis**: Interactive tornado diagrams showing NPV impact of key variables
- **Global Data Integration**: Real-time market data from 21+ countries
- **Professional Reporting**: Executive-grade analysis and recommendations
- **Performance Optimized**: Streamlined interface focused on essential metrics

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

### **Analysis Best Practices**
- Complete all required input fields before running analysis
- Review sensitivity analysis to understand key risk factors
- Use the Data Integration tab to verify market data sources
- Export results to Excel for professional presentations

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

### **Excel Export**
- Executive-ready reports with comprehensive financial analysis
- Multiple worksheets with organized data
- Synchronized with current analysis inputs (stale data prevention)
- Professional formatting suitable for presentations

### **JSON Export**
- Complete input parameter backup
- Shareable with colleagues  
- Importable for future analysis
- Timestamp and metadata included for tracking

## 🆘 Troubleshooting

### **Common Issues**
- **Analysis Won't Run**: Ensure all required fields are completed
- **Export Shows Warning**: Re-run analysis if inputs have changed since last analysis
- **Performance**: App optimized for speed - contact support if issues persist
- **Mobile Issues**: Use landscape mode for best experience

### **Getting Help**
- Use the **Data Integration** tab to verify market data status
- Check export data synchronization warnings in Export & Sharing tab
- Refer to sensitivity analysis for understanding key decision factors
- Contact support for technical issues with the live application

---

**Ready to make professional real estate investment decisions! 🏢**