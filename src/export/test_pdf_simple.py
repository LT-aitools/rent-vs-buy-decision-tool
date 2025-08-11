"""
Simple PDF System Test
Basic PDF generation test without chart dependencies

This script validates:
- PDF generator core functionality
- Layout engine operation
- Template system basic operation
- ReportLab integration
"""

import logging
from pathlib import Path
from typing import Dict, Any
import tempfile

# Test logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_sample_export_data() -> Dict[str, Any]:
    """Create sample export data for testing"""
    
    return {
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
        'ownership_flows': {
            'annual_cash_flows': [
                -45000, -42000, -41000, -40000, -39000, -38000, -37000, -36000, -35000, -34000,
                -33000, -32000, -31000, -30000, -29000, -28000, -27000, -26000, -25000, -24000,
                -23000, -22000, -21000, -20000, 580000  # Final year includes sale proceeds
            ]
        },
        'rental_flows': {
            'annual_cash_flows': [
                -36000, -37080, -38192, -39338, -40518, -41733, -42985, -44275, -45603, -46971,
                -48380, -49832, -51327, -52866, -54452, -56086, -57768, -59501, -61286, -63125,
                -65019, -66969, -68978, -71047, -73177
            ]
        }
    }

def test_pdf_generator():
    """Test basic PDF generation"""
    
    logger.info("Testing PDF Generator...")
    
    try:
        from pdf.pdf_generator import PDFGenerator
        
        generator = PDFGenerator()
        sample_data = create_sample_export_data()
        
        # Test validation
        validation = generator.validate_export_data(sample_data)
        logger.info(f"Validation result: {validation}")
        
        if not validation['is_valid']:
            logger.error("Sample data validation failed")
            return False
        
        # Test PDF generation (executive summary only, no charts)
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            output_path = Path(tmp_file.name)
        
        try:
            pdf_path = generator.generate_report(
                export_data=sample_data,
                template_type='executive',
                output_path=output_path,
                chart_images=None  # No charts for simple test
            )
            
            logger.info(f"PDF generated: {pdf_path}")
            
            # Verify file exists and has content
            if not pdf_path.exists():
                logger.error(f"PDF file not created: {pdf_path}")
                return False
            
            file_size = pdf_path.stat().st_size
            if file_size < 1000:  # Should be at least 1KB
                logger.error(f"PDF file too small: {file_size} bytes")
                return False
            
            logger.info(f"✅ PDF generation test passed - File size: {file_size:,} bytes")
            
            # Clean up
            pdf_path.unlink()
            return True
            
        except Exception as e:
            logger.error(f"PDF generation failed: {str(e)}")
            return False
        
    except ImportError as e:
        logger.error(f"PDF Generator import failed: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"PDF Generator test failed: {str(e)}")
        return False

def test_layout_engine():
    """Test layout engine functionality"""
    
    logger.info("Testing Layout Engine...")
    
    try:
        from pdf.layout_engine import LayoutEngine, ContentType
        
        layout = LayoutEngine()
        
        # Test basic functionality
        layout_info = layout.get_layout_info()
        logger.info(f"Layout info: {layout_info}")
        
        # Test grid calculations
        width, offset = layout.calculate_content_area(0, 12)
        logger.info(f"Full width: {width:.0f}pt, offset: {offset:.0f}pt")
        
        # Test chart sizing
        chart_width, chart_height = layout.optimize_chart_size(ContentType.CHART, 12, 1.5)
        logger.info(f"Optimized chart size: {chart_width:.0f}x{chart_height:.0f}pt")
        
        # Test table styling
        table_style = layout.create_table_style('professional')
        if table_style is not None:
            logger.info("✅ Table style created successfully")
        
        logger.info("✅ Layout Engine test passed")
        return True
        
    except ImportError as e:
        logger.error(f"Layout Engine import failed: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Layout Engine test failed: {str(e)}")
        return False

def test_template_builder():
    """Test template builder functionality"""
    
    logger.info("Testing Template Builder...")
    
    try:
        from pdf.executive_templates import ExecutiveTemplateBuilder, TemplateConfig, TemplateType
        
        # Test executive template
        config = TemplateConfig(TemplateType.EXECUTIVE)
        template_builder = ExecutiveTemplateBuilder(config)
        
        sample_data = create_sample_export_data()
        
        # Test building executive summary content (without charts)
        story = template_builder.build_executive_summary(sample_data, chart_images=None)
        
        if len(story) < 5:  # Should have multiple elements
            logger.error("Executive summary story too short")
            return False
        
        logger.info(f"✅ Executive summary built with {len(story)} elements")
        
        # Test detailed analysis
        detailed_story = template_builder.build_detailed_analysis(sample_data, chart_images=None)
        
        if len(detailed_story) < len(story):
            logger.error("Detailed analysis should be longer than executive summary")
            return False
        
        logger.info(f"✅ Detailed analysis built with {len(detailed_story)} elements")
        
        # Test investor presentation
        investor_story = template_builder.build_investor_presentation(sample_data, chart_images=None)
        
        if len(investor_story) < 5:
            logger.error("Investor presentation story too short")
            return False
        
        logger.info(f"✅ Investor presentation built with {len(investor_story)} elements")
        
        logger.info("✅ Template Builder test passed")
        return True
        
    except ImportError as e:
        logger.error(f"Template Builder import failed: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Template Builder test failed: {str(e)}")
        return False

def run_simple_tests():
    """Run all simple PDF tests"""
    
    logger.info("="*50)
    logger.info("SIMPLE PDF SYSTEM TEST SUITE")
    logger.info("="*50)
    
    tests = [
        ("Layout Engine", test_layout_engine),
        ("Template Builder", test_template_builder),
        ("PDF Generator", test_pdf_generator)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n--- Testing {test_name} ---")
        
        try:
            if test_func():
                passed_tests += 1
                logger.info(f"✅ {test_name} test PASSED")
            else:
                logger.error(f"❌ {test_name} test FAILED")
        except Exception as e:
            logger.error(f"❌ {test_name} test ERROR: {str(e)}")
    
    # Final results
    logger.info("\n" + "="*50)
    logger.info(f"TEST RESULTS: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        logger.info("🎉 ALL SIMPLE TESTS PASSED - PDF system core is working!")
        success = True
    else:
        logger.error(f"❌ {total_tests - passed_tests} test(s) failed")
        success = False
    
    logger.info("="*50)
    
    return success

if __name__ == "__main__":
    success = run_simple_tests()
    exit(0 if success else 1)