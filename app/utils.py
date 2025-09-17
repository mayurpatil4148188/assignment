from flask import jsonify
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ResponseUtils:
    """Utility class for standardized API responses"""
    
    @staticmethod
    def success_response(data=None, message="Success", status_code=200):
        """Create a success response"""
        response = {
            "success": True,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if data is not None:
            response["data"] = data
        
        return jsonify(response), status_code
    
    @staticmethod
    def created_response(data=None, message="Resource created successfully", status_code=201):
        """Create a created response"""
        response = {
            "success": True,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if data is not None:
            response["data"] = data
        
        return jsonify(response), status_code
    
    @staticmethod
    def updated_response(data=None, message="Resource updated successfully", status_code=200):
        """Create an updated response"""
        response = {
            "success": True,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if data is not None:
            response["data"] = data
        
        return jsonify(response), status_code
    
    @staticmethod
    def deleted_response(message="Resource deleted successfully", status_code=200):
        """Create a deleted response"""
        response = {
            "success": True,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return jsonify(response), status_code
    
    @staticmethod
    def error_response(message="An error occurred", errors=None, status_code=400, error_code="ERROR"):
        """Create an error response"""
        response = {
            "success": False,
            "message": message,
            "error_code": error_code,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if errors:
            response["errors"] = errors
        
        return jsonify(response), status_code
    
    @staticmethod
    def validation_error_response(errors, message="Validation failed"):
        """Create a validation error response"""
        return ResponseUtils.error_response(
            message=message,
            errors=errors,
            status_code=400,
            error_code="VALIDATION_ERROR"
        )
    
    @staticmethod
    def not_found_response(resource_name="Resource"):
        """Create a not found response"""
        return ResponseUtils.error_response(
            message=f"{resource_name} not found",
            status_code=404,
            error_code="NOT_FOUND"
        )
    
    @staticmethod
    def internal_error_response(message="An internal server error occurred"):
        """Create an internal server error response"""
        return ResponseUtils.error_response(
            message=message,
            status_code=500,
            error_code="INTERNAL_ERROR"
        )
    
    @staticmethod
    def paginated_response(items, page, per_page, total, message="Data retrieved successfully"):
        """Create a paginated response"""
        response = {
            "success": True,
            "message": message,
            "data": items,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page,
                "has_next": page * per_page < total,
                "has_prev": page > 1
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return jsonify(response), 200
