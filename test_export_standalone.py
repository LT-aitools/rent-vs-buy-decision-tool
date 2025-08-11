"""
Standalone Export Test
Test PDF and Excel generation without Streamlit UI

This creates actual export files you can open to verify the functionality
"""

import sys
import os
import asyncio
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

async def test_standalone_exports():
    """Test both PDF and Excel exports with real file outputs"""
    
    print("🧪 Testing Standalone Export Generation...")
    print("=" * 60)
    
    # Sample data similar to what the app generates
    sample_export_data = {
        'analysis_results': {
            'ownership_npv': 125000.0,
            'rental_npv': 85000.0,
            'npv_difference': 40000.0,
            'ownership_initial_investment': 150000.0,
            'rental_initial_investment': 5000.0,
            'ownership_irr': 0.08,
            'rental_irr': 0.06,
            'recommendation': 'BUY',
            'confidence': 'High'
        },
        'inputs': {
            'purchase_price': 750000.0,
            'down_payment_percent': 20.0,
            'interest_rate': 5.5,
            'loan_term': 30,
            'analysis_period': 25,
            'cost_of_capital': 8.0,
            'property_tax_rate': 1.2,
            'property_tax_escalation_rate': 2.0,
            'insurance_cost': 5000.0,
            'annual_maintenance_percent': 2.0,
            'property_appreciation_rate': 3.5,
            'current_annual_rent': 36000.0,
            'rent_increase_rate': 3.0,
            'security_deposit': 3000.0,
            'transaction_costs_percent': 5.0,
            'sale_transaction_costs_percent': 6.0,
            'tax_rate': 32.0,
            'inflation_rate': 2.5
        },
        'ownership_flows': [
            {'year': i+1, 'net_cash_flow': -45000 + i*1000, 'annual_rent': 0} 
            for i in range(25)
        ],
        'rental_flows': [
            {'year': i+1, 'net_cash_flow': -36000 - i*1000, 'annual_rent': 36000 + i*1080} 
            for i in range(25)
        ]
    }
    
    # Set up output directory
    output_dir = Path("test_exports")
    output_dir.mkdir(exist_ok=True)
    print(f"📁 Output directory: {output_dir.absolute()}")
    
    # Test PDF Export
    print("\n1. Testing PDF Export...")
    try:
        from export.pdf_integration import PDFExportManager, PDF_SYSTEM_AVAILABLE
        
        if PDF_SYSTEM_AVAILABLE:
            pdf_manager = PDFExportManager()
            
            # Test all three templates
            templates = ['executive', 'detailed', 'investor']
            
            for template in templates:
                print(f"   📄 Generating {template} PDF...")
                
                try:
                    pdf_path, info = await pdf_manager.generate_pdf_report(
                        export_data=sample_export_data,
                        template_type=template
                    )
                    
                    # Move to our output directory with descriptive name
                    output_path = output_dir / f"sample_analysis_{template}_report.pdf"
                    pdf_path.rename(output_path)
                    
                    file_size = output_path.stat().st_size
                    print(f"   ✅ {template.title()} PDF: {output_path.name} ({file_size:,} bytes)")
                    
                except Exception as e:
                    print(f"   ❌ {template.title()} PDF failed: {str(e)}")
            
        else:
            print("   ❌ PDF system not available")
            
    except Exception as e:
        print(f"   ❌ PDF system error: {str(e)}")
    
    # Test Excel Export
    print("\n2. Testing Excel Export...")
    try:
        from export.streamlit_integration import ExcelExportManager, EXCEL_SYSTEM_AVAILABLE
        
        if EXCEL_SYSTEM_AVAILABLE:
            excel_manager = ExcelExportManager()
            
            print(f"   📊 Generating comprehensive Excel report...")
            
            try:
                excel_path, info = await excel_manager.generate_excel_report(
                    export_data=sample_export_data,
                    template_type='comprehensive',
                    include_charts=True
                )
                
                # Move to our output directory
                output_path = output_dir / "sample_analysis_comprehensive.xlsx"
                excel_path.rename(output_path)
                
                file_size = output_path.stat().st_size
                print(f"   ✅ Excel Report: {output_path.name} ({file_size:,} bytes)")
                print(f"   📊 Worksheets: {info['worksheets']}")
                print(f"   ⏱️  Generation time: {info['generation_time']:.1f}s")
                
            except Exception as e:
                print(f"   ❌ Excel generation failed: {str(e)}")
                import traceback
                traceback.print_exc()
            
        else:
            print("   ❌ Excel system not available")
            
    except Exception as e:
        print(f"   ❌ Excel system error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("🎉 Standalone export test completed!")
    
    # List all generated files
    generated_files = list(output_dir.glob("*"))
    if generated_files:
        print(f"\n📂 Generated files in {output_dir}:")
        for file_path in generated_files:
            size = file_path.stat().st_size
            print(f"   • {file_path.name} ({size:,} bytes)")
        
        print(f"\n📖 You can now open these files to verify the export functionality:")
        print(f"   📄 PDF files: Open with any PDF viewer")  
        print(f"   📊 Excel files: Open with Excel or Google Sheets")
        
    else:
        print("\n⚠️  No files were generated - check error messages above")

if __name__ == "__main__":
    asyncio.run(test_standalone_exports())