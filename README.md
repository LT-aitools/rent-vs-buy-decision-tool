# Real Estate Rent vs. Buy Decision Tool

A comprehensive financial analysis platform to evaluate rent versus purchase decisions for warehouse and logistics facilities across global subsidiaries, built with Streamlit and optimized for hold-forever investment strategies.

## 🎯 Project Overview

**Purpose**: Standardize real estate decision-making, reduce analysis time by 60%, improve capital allocation efficiency by 15%, and provide defensible recommendations for executive approval.

**Repository**: https://github.com/LT-aitools/rent-vs-buy-decision-tool

**Key Benefits**:
- Zero ongoing hosting costs ($0/month)
- 4-week development timeline for full functionality
- Professional-grade analysis suitable for executive presentations
- Standardized methodology across all global subsidiaries
- Complete audit trail with transparent calculations
- Hold-forever investment strategy optimized

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Git

### Installation
```bash
git clone https://github.com/LT-aitools/rent-vs-buy-decision-tool.git
cd rent-vs-buy-decision-tool
pip install -r requirements.txt
```

### Run the Application
```bash
streamlit run src/app.py
```

## 📁 Repository Structure

```
rent-vs-buy-decision-tool/
├── docs/
│   ├── business-prd.md              # Complete Business PRD
│   ├── technical-prd.md             # Technical Implementation Specifications
│   └── user-guide.md                # User documentation
├── src/
│   ├── app.py                       # Main Streamlit application
│   ├── calculations.py              # Financial calculation engine
│   ├── visualizations.py           # Chart and graph generation
│   ├── excel_export.py             # Excel report generation
│   └── utils.py                     # Utility functions and validation
├── .streamlit/
│   └── config.toml                  # Streamlit configuration and theming
├── tests/
│   ├── test_calculations.py         # Unit tests for financial calculations
│   └── test_integration.py          # Integration tests
├── requirements.txt                 # Python dependencies
├── .gitignore                       # Git ignore file
├── LICENSE                          # License file
└── README.md                        # This file
```

## 📋 Features

### Core Analysis
- **Hold-Forever Strategy**: Optimized for perpetual property ownership
- **NPV Analysis**: Comprehensive net present value comparison
- **Cash Flow Modeling**: Year-by-year operational cost analysis
- **Terminal Value**: Wealth accumulation analysis (not sale-based)
- **Edge Case Handling**: 100% down payment, 0% interest scenarios

### Advanced Features
- **Multi-Variable Sensitivity Analysis**: Interest rates, rent escalation, appreciation rates
- **Professional Excel Export**: Executive-ready reports with all calculations
- **Scenario Sharing**: URL-based parameter sharing
- **Risk Assessment**: Long-term property risks and obsolescence factors

### Input Categories (30+ Fields)
1. **Project Information**: Basic project details and metadata
2. **Property & Market**: Property specifications and market assumptions
3. **Purchase Parameters**: All ownership-related costs and financing
4. **Rental Parameters**: All rental-related costs and terms
5. **Operational Parameters**: Growth, expansion, and business assumptions
6. **Tax & Accounting**: Tax rates, depreciation, and deductibility settings

## 🛠 Technology Stack

- **Frontend/Backend**: Streamlit 1.45.1+
- **Python Version**: 3.10+
- **Data Processing**: pandas 2.3.1, numpy 2.3.2
- **Visualization**: plotly 5.24.1
- **Excel Export**: openpyxl 3.1.5
- **Deployment**: Streamlit Community Cloud (Free)
- **Storage**: Session state only (no database required)

## 📊 Business Logic

### Hold-Forever Investment Strategy
This tool is specifically designed for companies that intend to hold warehouse properties indefinitely:

- **Terminal Value**: Represents wealth accumulation, not sale proceeds
- **Operational Focus**: Emphasizes long-term operational efficiency
- **Risk Integration**: Includes property upgrade cycles and obsolescence factors
- **Wealth Comparison**: Shows equity building vs. rental (no asset accumulation)

### Key Calculations
- **Mortgage Payments**: Handles all-cash and zero-interest scenarios
- **Property Appreciation**: Separate land and building appreciation with depreciation
- **Tax Benefits**: Configurable deductions for interest, depreciation, property taxes
- **Operational Costs**: All ownership costs including CapEx reserves
- **Year-by-Year Analysis**: Consistent Year-1 indexing for cost escalation

## 🎨 User Interface

### Executive Dashboard
- **Recommendation Engine**: Buy/Rent recommendation with confidence levels
- **Key Metrics**: NPV Advantage, Operational Break-Even, Cash Flow Impact
- **Wealth Accumulation Charts**: Visual comparison of long-term wealth building
- **Sensitivity Analysis**: Interactive exploration of key variables

### Professional Reporting
- **Excel Export**: Complete analysis with multiple worksheets
- **Audit Trail**: All assumptions and intermediate calculations visible
- **Scenario Comparison**: Side-by-side analysis capabilities

## 🔧 Development

### Setup Development Environment
```bash
# Clone repository
git clone https://github.com/LT-aitools/rent-vs-buy-decision-tool.git
cd rent-vs-buy-decision-tool

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run in development mode
streamlit run src/app.py
```

### Running Tests
```bash
pytest tests/
```

### Development Timeline
- **Week 1**: Core MVP with input forms and basic calculations
- **Week 2**: NPV analysis and cash flow modeling  
- **Week 3**: Advanced features and sensitivity analysis
- **Week 4**: Polish, testing, and deployment

## 📈 Business Impact

### Expected ROI
- **60% reduction** in analysis time
- **15% improvement** in capital allocation efficiency
- **Standardized methodology** across global subsidiaries
- **Executive-ready presentations** with professional reporting

### Target Users
- Corporate Real Estate teams
- Finance teams evaluating property investments
- Executive leadership making capital allocation decisions
- Global subsidiaries requiring standardized analysis

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For questions or support, please open an issue in this repository or contact the LT-aitools team.

## 🔗 Links

- [Business PRD](docs/business-prd.md) - Complete business requirements
- [Technical PRD](docs/technical-prd.md) - Technical implementation details
- [User Guide](docs/user-guide.md) - End-user documentation
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Live Demo](https://rent-vs-buy-decision-tool.streamlit.app/) - (After deployment)

---

**Built with ❤️ by LT-aitools for better real estate investment decisions**