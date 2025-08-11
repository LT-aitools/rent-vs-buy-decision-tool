"""
PDF System Test Script
Test PDF generation system with sample data

This script validates:
- PDF generation system functionality
- Chart rendering integration
- Template system operation
- Export data compatibility
- Error handling and validation

Repository: https://github.com/LT-aitools/rent-vs-buy-decision-tool
"""

import asyncio
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

async def test_pdf_system():
    """Test the complete PDF generation system"""
    
    logger.info("Starting PDF system test...")
    
    try:
        # Import PDF system components
        from pdf_integration import PDFExportManager
        
        # Create test data
        sample_data = create_sample_export_data()
        logger.info("Sample data created")
        
        # Initialize PDF export manager
        manager = PDFExportManager()
        logger.info("PDF Export Manager initialized")
        
        # Test system capabilities
        capabilities = manager.get_export_capabilities()
        logger.info(f"System capabilities: {capabilities}")
        
        if not capabilities['pdf_system_available']:
            logger.error("PDF system not available - please install dependencies")
            return False
        
        # Test validation
        validation = manager.pdf_generator.validate_export_data(sample_data)
        logger.info(f"Data validation: {validation}")
        
        if not validation['is_valid']:
            logger.error("Sample data validation failed")
            return False
        
        # Test chart rendering info
        chart_info = manager.chart_renderer.get_chart_rendering_info()
        logger.info(f"Chart rendering capabilities: {chart_info}")
        
        # Test PDF generation for each template type
        templates_to_test = ['executive', 'detailed', 'investor']
        
        for template_type in templates_to_test:
            logger.info(f"\n--- Testing {template_type} template ---")
            
            try:
                # Generate PDF
                pdf_path, generation_info = await manager.generate_pdf_report(
                    export_data=sample_data,
                    template_type=template_type
                )
                
                logger.info(f"PDF generated: {pdf_path}")
                logger.info(f"Generation info: {generation_info}")
                
                # Verify file exists and has content
                if not pdf_path.exists():
                    logger.error(f"PDF file not created: {pdf_path}")
                    return False
                
                file_size = pdf_path.stat().st_size
                if file_size < 1000:  # Should be at least 1KB
                    logger.error(f"PDF file too small: {file_size} bytes")
                    return False
                
                logger.info(f"✅ {template_type} template test passed - File size: {file_size:,} bytes")
                
                # Clean up test file
                try:
                    pdf_path.unlink()
                except:
                    pass
                
            except Exception as e:
                logger.error(f"❌ {template_type} template test failed: {str(e)}")
                return False
        
        logger.info("\n🎉 All PDF system tests passed!")
        return True
        
    except ImportError as e:
        logger.error(f"Import error - PDF system dependencies missing: {str(e)}")
        logger.info("Please run: pip install reportlab Pillow pypdf")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during testing: {str(e)}")
        return False

def test_individual_components():
    """Test individual PDF system components"""
    
    logger.info("\n--- Testing Individual Components ---")
    
    try:
        # Test PDF generator
        from pdf.pdf_generator import PDFGenerator
        
        generator = PDFGenerator()
        sample_data = create_sample_export_data()
        validation = generator.validate_export_data(sample_data)
        
        logger.info(f"✅ PDF Generator validation: {validation['is_valid']}")
        
        # Test layout engine
        from pdf.layout_engine import LayoutEngine
        
        layout = LayoutEngine()
        layout_info = layout.get_layout_info()
        
        logger.info(f"✅ Layout Engine initialized - Content area: {layout_info['dimensions']['content_width']:.0f}x{layout_info['dimensions']['content_height']:.0f}")
        
        # Test chart renderer
        from pdf.chart_renderer import PDFChartRenderer
        
        chart_renderer = PDFChartRenderer()
        renderer_info = chart_renderer.get_chart_rendering_info()
        
        logger.info(f"✅ Chart Renderer initialized - Resolution: {renderer_info['resolution']} DPI")
        
        # Test template builder
        from pdf.executive_templates import ExecutiveTemplateBuilder, TemplateConfig, TemplateType
        
        config = TemplateConfig(TemplateType.EXECUTIVE)
        template_builder = ExecutiveTemplateBuilder(config)
        
        logger.info("✅ Template Builder initialized")
        
        logger.info("🎉 All individual component tests passed!")
        return True
        
    except ImportError as e:
        logger.error(f"❌ Component import failed: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"❌ Component test failed: {str(e)}")
        return False

def run_all_tests():
    """Run all PDF system tests"""
    
    logger.info("="*50)
    logger.info("PDF SYSTEM TEST SUITE")
    logger.info("="*50)
    
    # Test individual components first
    component_test_passed = test_individual_components()
    
    if not component_test_passed:
        logger.error("❌ Component tests failed - skipping integration tests")
        return False
    
    # Test full system integration
    try:
        integration_test_passed = asyncio.run(test_pdf_system())
    except Exception as e:
        logger.error(f"❌ Integration test failed: {str(e)}")
        integration_test_passed = False
    
    # Final results
    logger.info("\n" + "="*50)
    if component_test_passed and integration_test_passed:
        logger.info("🎉 ALL TESTS PASSED - PDF system is ready!")
        logger.info("The PDF report generation system is working correctly.")
    else:
        logger.error("❌ SOME TESTS FAILED")
        if not component_test_passed:
            logger.error("- Component tests failed")
        if not integration_test_passed:
            logger.error("- Integration tests failed")
        logger.info("Please check the error messages above and install missing dependencies.")
    
    logger.info("="*50)
    
    return component_test_passed and integration_test_passed

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)