"""
Export Validation
Data validation and integrity checks for export system

Ensures all required data is present and valid before beginning
export generation process.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime


# Configure logging
logger = logging.getLogger(__name__)


class ExportValidationError(Exception):
    """Raised when export data validation fails"""
    pass


def validate_export_data(export_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Comprehensive validation of export data
    
    Args:
        export_data: Complete export data package
        
    Returns:
        Dictionary with validation results: {'is_valid': bool, 'errors': list, 'warnings': list}
    """
    logger.info("Starting export data validation")
    
    validation_result = {
        'is_valid': True,
        'errors': [],
        'warnings': []
    }
    
    try:
        # Validate core data components
        _validate_analysis_results(export_data.get('analysis_results'))
        
        # Check cash flow format and validate accordingly
        ownership_flows = export_data.get('ownership_flows')
        rental_flows = export_data.get('rental_flows')
        
        # Handle both list and dict formats for cash flows
        if isinstance(ownership_flows, list):
            _validate_cash_flows(ownership_flows, "ownership")
        elif isinstance(ownership_flows, dict):
            _validate_cash_flows_dict(ownership_flows, "ownership")
        else:
            raise ExportValidationError("Ownership cash flows must be either a list or dictionary")
            
        if isinstance(rental_flows, list):
            _validate_cash_flows(rental_flows, "rental")  
        elif isinstance(rental_flows, dict):
            _validate_cash_flows_dict(rental_flows, "rental")
        else:
            raise ExportValidationError("Rental cash flows must be either a list or dictionary")
        
        # Handle flexible session data format (could be 'session_data' or 'inputs')
        session_data = export_data.get('session_data') or export_data.get('inputs')
        _validate_session_data(session_data)
        
        # Validate data consistency based on detected format
        if isinstance(ownership_flows, list) and isinstance(rental_flows, list):
            _validate_data_consistency(export_data)
        else:
            _validate_data_consistency_dict(export_data)
        
        logger.info("Export data validation completed successfully")
        
    except ExportValidationError as e:
        validation_result['is_valid'] = False
        validation_result['errors'].append(str(e))
        logger.error(f"Export data validation failed: {str(e)}")
    except Exception as e:
        validation_result['is_valid'] = False
        validation_result['errors'].append(f"Unexpected validation error: {str(e)}")
        logger.error(f"Unexpected export data validation error: {str(e)}")
    
    return validation_result


def validate_export_data_strict(export_data: Dict[str, Any]) -> None:
    """
    Comprehensive validation of export data (raises exceptions)
    
    Args:
        export_data: Complete export data package
        
    Raises:
        ExportValidationError: If validation fails
    """
    validation_result = validate_export_data(export_data)
    if not validation_result['is_valid']:
        raise ExportValidationError("; ".join(validation_result['errors']))


def _validate_analysis_results(analysis_results: Optional[Dict[str, Any]]) -> None:
    """Validate analysis results data"""
    if not analysis_results:
        raise ExportValidationError("Analysis results are required")
    
    if not isinstance(analysis_results, dict):
        raise ExportValidationError("Analysis results must be a dictionary")
    
    # Check for required analysis fields
    required_fields = [
        'ownership_npv',
        'rental_npv', 
        'npv_difference',
        'recommendation',
        'confidence'
    ]
    
    missing_fields = []
    for field in required_fields:
        if field not in analysis_results:
            missing_fields.append(field)
    
    if missing_fields:
        raise ExportValidationError(f"Missing required analysis fields: {', '.join(missing_fields)}")
    
    # Validate numeric fields
    numeric_fields = ['ownership_npv', 'rental_npv', 'npv_difference']
    for field in numeric_fields:
        value = analysis_results.get(field)
        if not isinstance(value, (int, float)):
            raise ExportValidationError(f"Analysis field '{field}' must be numeric, got {type(value)}")
    
    # Validate recommendation
    recommendation = analysis_results.get('recommendation')
    if recommendation not in ['BUY', 'RENT', 'MARGINAL']:
        raise ExportValidationError(f"Invalid recommendation: {recommendation}")
    
    # Validate confidence
    confidence = analysis_results.get('confidence')
    if confidence not in ['High', 'Medium', 'Low']:
        raise ExportValidationError(f"Invalid confidence level: {confidence}")


def _validate_cash_flows(cash_flows: Optional[List[Dict[str, float]]], flow_type: str) -> None:
    """Validate cash flow data"""
    if not cash_flows:
        raise ExportValidationError(f"{flow_type.title()} cash flows are required")
    
    if not isinstance(cash_flows, list):
        raise ExportValidationError(f"{flow_type.title()} cash flows must be a list")
    
    if len(cash_flows) == 0:
        raise ExportValidationError(f"{flow_type.title()} cash flows cannot be empty")
    
    # Validate each cash flow entry
    required_fields = ['year', 'net_cash_flow']
    
    for i, flow in enumerate(cash_flows):
        if not isinstance(flow, dict):
            raise ExportValidationError(f"{flow_type.title()} cash flow entry {i} must be a dictionary")
        
        # Check required fields
        for field in required_fields:
            if field not in flow:
                raise ExportValidationError(f"Missing field '{field}' in {flow_type} cash flow entry {i}")
        
        # Validate year
        year = flow.get('year')
        if not isinstance(year, (int, float)) or year <= 0:
            raise ExportValidationError(f"Invalid year in {flow_type} cash flow entry {i}: {year}")
        
        # Validate net cash flow
        net_flow = flow.get('net_cash_flow')
        if not isinstance(net_flow, (int, float)):
            raise ExportValidationError(f"Invalid net_cash_flow in {flow_type} cash flow entry {i}: {net_flow}")
    
    # Validate year sequence
    years = [flow['year'] for flow in cash_flows]
    expected_years = list(range(1, len(cash_flows) + 1))
    
    if years != expected_years:
        raise ExportValidationError(f"Invalid year sequence in {flow_type} cash flows. Expected {expected_years}, got {years}")


def _validate_session_data(session_data: Optional[Dict[str, Any]]) -> None:
    """Validate session data (user inputs)"""
    if not session_data:
        raise ExportValidationError("Session data is required")
    
    if not isinstance(session_data, dict):
        raise ExportValidationError("Session data must be a dictionary")
    
    # Check for critical input fields
    critical_fields = [
        'purchase_price',
        'current_annual_rent',
        'analysis_period'
    ]
    
    missing_critical = []
    for field in critical_fields:
        if field not in session_data and not _find_nested_field(session_data, field):
            missing_critical.append(field)
    
    if missing_critical:
        raise ExportValidationError(f"Missing critical session data fields: {', '.join(missing_critical)}")


def _validate_cash_flows_dict(cash_flows: Optional[Dict[str, Any]], flow_type: str) -> None:
    """Validate cash flow data when it's in dictionary format"""
    if not cash_flows:
        raise ExportValidationError(f"{flow_type.title()} cash flows are required")
    
    if not isinstance(cash_flows, dict):
        raise ExportValidationError(f"{flow_type.title()} cash flows must be a dictionary")
    
    # Extract annual cash flows array
    annual_flows = cash_flows.get('annual_cash_flows', [])
    if not isinstance(annual_flows, list):
        raise ExportValidationError(f"{flow_type.title()} annual_cash_flows must be a list")
    
    if len(annual_flows) == 0:
        raise ExportValidationError(f"{flow_type.title()} annual_cash_flows cannot be empty")
    
    # Validate each cash flow value
    for i, flow in enumerate(annual_flows):
        if not isinstance(flow, (int, float)):
            raise ExportValidationError(f"Invalid cash flow value in {flow_type} entry {i}: {flow}")


def _validate_data_consistency_dict(export_data: Dict[str, Any]) -> None:
    """Validate consistency between different data components (dict format)"""
    analysis = export_data.get('analysis_results', {})
    ownership_flows = export_data.get('ownership_flows', {})
    rental_flows = export_data.get('rental_flows', {})
    session_data = export_data.get('session_data', {}) or export_data.get('inputs', {})
    
    # Check analysis period consistency
    analysis_period = analysis.get('analysis_period') or session_data.get('analysis_period') or _find_nested_field(session_data, 'analysis_period')
    
    ownership_annual = ownership_flows.get('annual_cash_flows', [])
    rental_annual = rental_flows.get('annual_cash_flows', [])
    
    if analysis_period:
        if len(ownership_annual) != analysis_period:
            raise ExportValidationError(f"Ownership cash flows ({len(ownership_annual)} years) don't match analysis period ({analysis_period} years)")
        
        if len(rental_annual) != analysis_period:
            raise ExportValidationError(f"Rental cash flows ({len(rental_annual)} years) don't match analysis period ({analysis_period} years)")
    
    # Check NPV calculation consistency
    ownership_npv = analysis.get('ownership_npv')
    rental_npv = analysis.get('rental_npv')
    npv_difference = analysis.get('npv_difference')
    
    if all(x is not None for x in [ownership_npv, rental_npv, npv_difference]):
        calculated_difference = ownership_npv - rental_npv
        if abs(calculated_difference - npv_difference) > 1:  # Allow small rounding differences
            raise ExportValidationError(f"NPV difference inconsistency: calculated {calculated_difference:.2f}, stored {npv_difference:.2f}")
    
    # Validate recommendation logic
    recommendation = analysis.get('recommendation')
    if recommendation and npv_difference is not None:
        if recommendation == 'BUY' and npv_difference <= 0:
            raise ExportValidationError("Recommendation is BUY but NPV difference is not positive")
        elif recommendation == 'RENT' and npv_difference >= 0:
            raise ExportValidationError("Recommendation is RENT but NPV difference is not negative")


def _validate_data_consistency(export_data: Dict[str, Any]) -> None:
    """Validate consistency between different data components"""
    analysis = export_data.get('analysis_results', {})
    ownership_flows = export_data.get('ownership_flows', [])
    rental_flows = export_data.get('rental_flows', [])
    session_data = export_data.get('session_data', {}) or export_data.get('inputs', {})
    
    # Check analysis period consistency
    analysis_period = analysis.get('analysis_period') or session_data.get('analysis_period') or _find_nested_field(session_data, 'analysis_period')
    
    if analysis_period:
        if len(ownership_flows) != analysis_period:
            raise ExportValidationError(f"Ownership cash flows ({len(ownership_flows)} years) don't match analysis period ({analysis_period} years)")
        
        if len(rental_flows) != analysis_period:
            raise ExportValidationError(f"Rental cash flows ({len(rental_flows)} years) don't match analysis period ({analysis_period} years)")
    
    # Check NPV calculation consistency
    ownership_npv = analysis.get('ownership_npv')
    rental_npv = analysis.get('rental_npv')
    npv_difference = analysis.get('npv_difference')
    
    if all(x is not None for x in [ownership_npv, rental_npv, npv_difference]):
        calculated_difference = ownership_npv - rental_npv
        if abs(calculated_difference - npv_difference) > 1:  # Allow small rounding differences
            raise ExportValidationError(f"NPV difference inconsistency: calculated {calculated_difference:.2f}, stored {npv_difference:.2f}")
    
    # Validate recommendation logic
    recommendation = analysis.get('recommendation')
    if recommendation and npv_difference is not None:
        if recommendation == 'BUY' and npv_difference <= 0:
            raise ExportValidationError("Recommendation is BUY but NPV difference is not positive")
        elif recommendation == 'RENT' and npv_difference >= 0:
            raise ExportValidationError("Recommendation is RENT but NPV difference is not negative")


def _find_nested_field(data: Dict[str, Any], field_name: str) -> Any:
    """
    Recursively search for a field in nested dictionary structure
    
    Args:
        data: Dictionary to search in
        field_name: Field name to search for
        
    Returns:
        Field value if found, None otherwise
    """
    if field_name in data:
        return data[field_name]
    
    for value in data.values():
        if isinstance(value, dict):
            result = _find_nested_field(value, field_name)
            if result is not None:
                return result
    
    return None


def validate_chart_data(chart_data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate chart data for export
    
    Args:
        chart_data: Chart data to validate
        
    Returns:
        Tuple of (is_valid: bool, error_message: str)
    """
    try:
        if not chart_data:
            return False, "No chart data provided"
        
        if not isinstance(chart_data, dict):
            return False, "Chart data must be a dictionary"
        
        # Check for required chart data
        required_charts = ['npv_comparison', 'cash_flow_timeline']
        missing_charts = [chart for chart in required_charts if chart not in chart_data]
        
        if missing_charts:
            return False, f"Missing required chart data: {', '.join(missing_charts)}"
        
        return True, "Valid chart data"
        
    except Exception as e:
        return False, f"Chart validation error: {str(e)}"


def validate_file_requirements(file_size_mb: float, max_size_mb: float = 50) -> Tuple[bool, str]:
    """
    Validate file size requirements
    
    Args:
        file_size_mb: File size in megabytes
        max_size_mb: Maximum allowed file size
        
    Returns:
        Tuple of (is_valid: bool, error_message: str)
    """
    if file_size_mb <= 0:
        return False, "File size must be positive"
    
    if file_size_mb > max_size_mb:
        return False, f"File size ({file_size_mb:.2f} MB) exceeds maximum allowed ({max_size_mb} MB)"
    
    return True, "Valid file size"