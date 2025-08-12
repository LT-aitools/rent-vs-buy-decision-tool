#!/usr/bin/env python3
"""
Test Excel Export System - End-to-End Test
Verifies that all critical issues have been fixed
"""

import asyncio
import sys
import logging
from pathlib import Path
import tempfile

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from export.excel.excel_generator import ExcelGenerator
from export.streamlit_integration import generate_excel_report
from export.validation import validate_export_data

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def create_test_data():
    """Create realistic test data that matches what the Streamlit app provides"""
    
    # This is the exact format the app provides
    export_data = {
        'analysis_results': {
            'ownership_npv': 125000.50,
            'rental_npv': -75000.25,
            'npv_difference': 200000.75,
            'recommendation': 'BUY',
            'confidence': 'High',
            'ownership_initial_investment': 100000,
            'rental_initial_investment': 5000,
            'analysis_period': 25,
            'cost_of_capital': 8.0
        },
        'ownership_flows': [  # List format, not dict!
            {'year': 1, 'net_cash_flow': -15000},
            {'year': 2, 'net_cash_flow': -12000},
            {'year': 3, 'net_cash_flow': -10000},
            {'year': 4, 'net_cash_flow': -8000},
            {'year': 5, 'net_cash_flow': 25000}
        ],
        'rental_flows': [  # List format, not dict!
            {'year': 1, 'net_cash_flow': -18000},
            {'year': 2, 'net_cash_flow': -18500},
            {'year': 3, 'net_cash_flow': -19000},
            {'year': 4, 'net_cash_flow': -19500},
            {'year': 5, 'net_cash_flow': -20000}
        ],
        'inputs': {  # This is 'inputs', NOT 'session_data'
            'purchase_price': 500000,
            'current_annual_rent': 30000,
            'analysis_period': 25,
            'down_payment_percent': 20,
            'mortgage_rate': 6.5,
            'property_tax_rate': 1.2,
            'maintenance_cost_percent': 1.5,
            'rental_appreciation_rate': 3.0,
            'property_appreciation_rate': 4.0
        }
    }
    
    return export_data

async def test_excel_generator_direct():
    """Test ExcelGenerator directly with new data format"""
    logger.info("Testing ExcelGenerator directly...")
    
    export_data = create_test_data()
    
    # Test validation
    logger.info("Testing validation...")
    excel_generator = ExcelGenerator()
    validation_result = await excel_generator.validate_data(export_data)
    
    if not validation_result['is_valid']:
        logger.error(f"Validation failed: {validation_result['errors']}")
        return False
    
    if validation_result['warnings']:
        logger.warning(f"Validation warnings: {validation_result['warnings']}")
    
    logger.info("✅ Validation passed")
    
    # Test data preparation
    logger.info("Testing data preparation...")
    try:
        excel_data = await excel_generator.prepare_data(export_data)
        logger.info(f"✅ Data prepared successfully. Session data keys: {list(excel_data['session_data'].keys())}")
    except Exception as e:
        logger.error(f"❌ Data preparation failed: {e}")
        return False
    
    # Test Excel generation
    logger.info("Testing Excel generation...")
    try:
        output_path = await excel_generator.generate_workbook(excel_data, "detailed")
        
        if output_path and output_path.exists():
            file_size = output_path.stat().st_size
            logger.info(f"✅ Excel file generated successfully: {output_path}")
            logger.info(f"File size: {file_size:,} bytes")
            
            # Clean up
            output_path.unlink()
            return True
        else:
            logger.error("❌ Excel file not created")
            return False
            
    except Exception as e:
        logger.error(f"❌ Excel generation failed: {e}")
        return False

def test_streamlit_integration():
    """Test streamlit integration function"""
    logger.info("Testing streamlit integration...")
    
    export_data = create_test_data()
    
    # Extract the data components
    analysis_results = export_data['analysis_results']
    ownership_flows = export_data['ownership_flows']
    rental_flows = export_data['rental_flows']
    session_data = export_data['inputs']  # Use 'inputs' key
    
    try:
        # Call the generate_excel_report function
        excel_path = generate_excel_report(
            analysis_results=analysis_results,
            ownership_flows=ownership_flows,
            rental_flows=rental_flows,
            session_data=session_data,
            template_type="detailed"
        )
        
        if excel_path and excel_path.exists():
            file_size = excel_path.stat().st_size
            logger.info(f"✅ Streamlit integration test passed: {excel_path}")
            logger.info(f"File size: {file_size:,} bytes")
            
            # Clean up
            try:
                excel_path.unlink()
            except:
                pass
            return True
        else:
            logger.error(f"❌ Streamlit integration test failed - no file: {excel_path}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Streamlit integration test failed: {e}")
        return False

def test_export_validation():
    """Test export validation with both data formats"""
    logger.info("Testing export validation...")
    
    # Test with 'inputs' key
    export_data = create_test_data()
    
    validation_result = validate_export_data(export_data)
    if not validation_result['is_valid']:
        logger.error(f"❌ Validation failed for 'inputs' format: {validation_result['errors']}")
        return False
    
    logger.info("✅ Validation passed for 'inputs' format")
    
    # Test with 'session_data' key
    export_data_session = create_test_data()
    export_data_session['session_data'] = export_data_session.pop('inputs')
    
    validation_result = validate_export_data(export_data_session)
    if not validation_result['is_valid']:
        logger.error(f"❌ Validation failed for 'session_data' format: {validation_result['errors']}")
        return False
    
    logger.info("✅ Validation passed for 'session_data' format")
    
    # Test with missing data
    export_data_missing = create_test_data()
    del export_data_missing['inputs']  # Remove inputs
    
    validation_result = validate_export_data(export_data_missing)
    if validation_result['is_valid']:
        logger.error("❌ Validation should have failed for missing session/inputs data")
        return False
    
    logger.info("✅ Validation correctly failed for missing session/inputs data")
    
    return True

async def run_all_tests():
    """Run all tests"""
    logger.info("🚀 Starting Excel Export System Tests")
    logger.info("=" * 60)
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Export validation
    if test_export_validation():
        tests_passed += 1
        logger.info("✅ Test 1 PASSED: Export validation")
    else:
        logger.error("❌ Test 1 FAILED: Export validation")
    
    logger.info("-" * 40)
    
    # Test 2: ExcelGenerator direct
    if await test_excel_generator_direct():
        tests_passed += 1
        logger.info("✅ Test 2 PASSED: ExcelGenerator direct")
    else:
        logger.error("❌ Test 2 FAILED: ExcelGenerator direct")
    
    logger.info("-" * 40)
    
    # Test 3: Streamlit integration
    if test_streamlit_integration():
        tests_passed += 1
        logger.info("✅ Test 3 PASSED: Streamlit integration")
    else:
        logger.error("❌ Test 3 FAILED: Streamlit integration")
    
    logger.info("=" * 60)
    logger.info(f"FINAL RESULTS: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        logger.info("🎉 ALL TESTS PASSED! Excel export system is working correctly.")
        return True
    else:
        logger.error("💥 SOME TESTS FAILED! Excel export system needs more work.")
        return False

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)