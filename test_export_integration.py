"""
Test Export System Integration
Quick test to verify PDF and Excel export systems work correctly

This script tests:
- PDF generation system functionality
- Excel export system availability
- Data format compatibility
- Error handling
"""

import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_export_systems():
    """Test both PDF and Excel export systems"""
    
    print("🧪 Testing Export System Integration...")
    print("=" * 50)
    
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
            'analysis_period': 25,
            'cost_of_capital': 8.0,
            'property_tax_rate': 1.2,
            'current_annual_rent': 36000.0,
            'rent_increase_rate': 3.0
        },
        'ownership_flows': [
            {'year': 1, 'net_cash_flow': -45000, 'annual_rent': 0},
            {'year': 2, 'net_cash_flow': -42000, 'annual_rent': 0},
            {'year': 3, 'net_cash_flow': -41000, 'annual_rent': 0}
        ],
        'rental_flows': [
            {'year': 1, 'net_cash_flow': -36000, 'annual_rent': 36000},
            {'year': 2, 'net_cash_flow': -37080, 'annual_rent': 37080},
            {'year': 3, 'net_cash_flow': -38192, 'annual_rent': 38192}
        ]
    }
    
    # Test PDF Export System
    print("1. Testing PDF Export System...")
    try:
        from export.pdf_integration import PDFExportManager, PDF_SYSTEM_AVAILABLE
        
        if PDF_SYSTEM_AVAILABLE:
            print("   ✅ PDF system dependencies available")
            
            pdf_manager = PDFExportManager()
            capabilities = pdf_manager.get_export_capabilities()
            print(f"   ✅ PDF Manager initialized - {len(capabilities['templates'])} templates available")
            
            # Test validation
            validation = pdf_manager.pdf_generator.validate_export_data(sample_export_data)
            print(f"   ✅ Data validation: {validation['is_valid']}")
            
            print("   📄 Available PDF templates:", capabilities['templates'])
            
        else:
            print("   ❌ PDF system dependencies not available")
            
    except ImportError as e:
        print(f"   ❌ PDF system import failed: {str(e)}")
    except Exception as e:
        print(f"   ⚠️ PDF system error: {str(e)}")
    
    print()
    
    # Test Excel Export System
    print("2. Testing Excel Export System...")
    try:
        from export.streamlit_integration import ExcelExportManager, EXCEL_SYSTEM_AVAILABLE
        
        if EXCEL_SYSTEM_AVAILABLE:
            print("   ✅ Excel system dependencies available")
            
            excel_manager = ExcelExportManager()
            capabilities = excel_manager.get_export_capabilities()
            print(f"   ✅ Excel Manager initialized - {len(capabilities['templates'])} templates available")
            
            print("   📊 Available Excel features:", list(capabilities['features'].keys()))
            
        else:
            print("   ❌ Excel system dependencies not available")
            
    except ImportError as e:
        print(f"   ❌ Excel system import failed: {str(e)}")
    except Exception as e:
        print(f"   ⚠️ Excel system error: {str(e)}")
    
    print()
    
    # Test basic PDF generation (if available)
    print("3. Testing Basic PDF Generation...")
    try:
        if PDF_SYSTEM_AVAILABLE:
            import asyncio
            from pathlib import Path
            import tempfile
            
            pdf_manager = PDFExportManager()
            
            # Test simple PDF generation
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                output_path = Path(tmp_file.name)
            
            async def test_pdf():
                try:
                    pdf_path, info = await pdf_manager.generate_pdf_report(
                        export_data=sample_export_data,
                        template_type='executive'
                    )
                    
                    if pdf_path.exists():
                        file_size = pdf_path.stat().st_size
                        print(f"   ✅ PDF generated successfully - Size: {file_size:,} bytes")
                        print(f"   📄 Generation time: {info.get('generation_time', 0):.1f}s")
                        
                        # Clean up
                        pdf_path.unlink()
                        return True
                    else:
                        print("   ❌ PDF file not found after generation")
                        return False
                        
                except Exception as e:
                    print(f"   ❌ PDF generation failed: {str(e)}")
                    return False
            
            success = asyncio.run(test_pdf())
            
        else:
            print("   ⏭️ Skipping PDF generation test (dependencies not available)")
            
    except Exception as e:
        print(f"   ❌ PDF generation test failed: {str(e)}")
    
    print()
    
    # Test data format compatibility
    print("4. Testing Data Format Compatibility...")
    try:
        # Test if our sample data matches expected format
        required_keys = ['analysis_results', 'inputs', 'ownership_flows', 'rental_flows']
        missing_keys = [key for key in required_keys if key not in sample_export_data]
        
        if not missing_keys:
            print("   ✅ Sample data format is compatible")
        else:
            print(f"   ⚠️ Missing keys in sample data: {missing_keys}")
        
        # Check analysis results structure
        analysis_required = ['recommendation', 'ownership_npv', 'rental_npv']
        analysis_missing = [key for key in analysis_required if key not in sample_export_data['analysis_results']]
        
        if not analysis_missing:
            print("   ✅ Analysis results format is compatible")
        else:
            print(f"   ⚠️ Missing analysis keys: {analysis_missing}")
            
    except Exception as e:
        print(f"   ❌ Data compatibility test failed: {str(e)}")
    
    print()
    print("=" * 50)
    print("🎉 Export system integration test completed!")
    print()
    print("To test the full UI:")
    print("1. Run: streamlit run src/app_with_visualizations.py")
    print("2. Complete all input fields")
    print("3. Run financial analysis")  
    print("4. Go to 'Export & Share' tab")
    print("5. Test PDF and Excel generation")


if __name__ == "__main__":
    test_export_systems()