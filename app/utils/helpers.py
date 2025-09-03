from flask import jsonify

def success_response(data=None, message="Success", status_code=200):
    """Create a standardized success response"""
    response = {
        'success': True,
        'message': message
    }
    if data is not None:
        response['data'] = data
    
    return jsonify(response), status_code

def error_response(message="An error occurred", status_code=400, details=None):
    """Create a standardized error response"""
    response = {
        'success': False,
        'message': message
    }
    if details:
        response['details'] = details
    
    return jsonify(response), status_code

def validate_required_fields(data, required_fields):
    """Validate that all required fields are present in data"""
    missing_fields = []
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == '':
            missing_fields.append(field)
    
    if missing_fields:
        return error_response(
            message="Missing required fields",
            details={'missing_fields': missing_fields},
            status_code=400
        )
    
    return None
