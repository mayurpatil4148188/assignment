"""
Centralized response utilities for consistent API responses
"""

from flask import jsonify
from typing import Any, Dict, List, Optional, Union
import logging

logger = logging.getLogger(__name__)

class ResponseUtils:
    """Utility class for standardized API responses"""
    
    @staticmethod
    def success_response(
        data: Any = None, 
        message: str = "Success", 
        status_code: int = 200,
        meta: Optional[Dict] = None
    ) -> tuple:
        """
        Create a standardized success response
        
        Args:
            data: Response data
            message: Success message
            status_code: HTTP status code
            meta: Additional metadata (pagination, etc.)
        
        Returns:
            tuple: (jsonify response, status_code)
        """
        response = {
            "success": True,
            "message": message,
            "data": data
        }
        
        if meta:
            response["meta"] = meta
            
        logger.info(f"Success response: {message} (Status: {status_code})")
        return jsonify(response), status_code
    
    @staticmethod
    def error_response(
        message: str = "An error occurred",
        errors: Optional[List[str]] = None,
        status_code: int = 400,
        error_code: Optional[str] = None
    ) -> tuple:
        """
        Create a standardized error response
        
        Args:
            message: Error message
            errors: List of specific errors
            status_code: HTTP status code
            error_code: Custom error code
        
        Returns:
            tuple: (jsonify response, status_code)
        """
        response = {
            "success": False,
            "message": message
        }
        
        if errors:
            response["errors"] = errors
            
        if error_code:
            response["error_code"] = error_code
            
        logger.error(f"Error response: {message} (Status: {status_code})")
        return jsonify(response), status_code
    
    @staticmethod
    def validation_error_response(
        errors: List[str],
        message: str = "Validation failed"
    ) -> tuple:
        """
        Create a standardized validation error response
        
        Args:
            errors: List of validation errors
            message: Error message
        
        Returns:
            tuple: (jsonify response, 400)
        """
        return ResponseUtils.error_response(
            message=message,
            errors=errors,
            status_code=400,
            error_code="VALIDATION_ERROR"
        )
    
    @staticmethod
    def not_found_response(
        resource: str = "Resource",
        message: Optional[str] = None
    ) -> tuple:
        """
        Create a standardized not found response
        
        Args:
            resource: Name of the resource that was not found
            message: Custom message
        
        Returns:
            tuple: (jsonify response, 404)
        """
        if not message:
            message = f"{resource} not found"
            
        return ResponseUtils.error_response(
            message=message,
            status_code=404,
            error_code="NOT_FOUND"
        )
    
    @staticmethod
    def created_response(
        data: Any = None,
        message: str = "Resource created successfully"
    ) -> tuple:
        """
        Create a standardized created response
        
        Args:
            data: Created resource data
            message: Success message
        
        Returns:
            tuple: (jsonify response, 201)
        """
        return ResponseUtils.success_response(
            data=data,
            message=message,
            status_code=201
        )
    
    @staticmethod
    def updated_response(
        data: Any = None,
        message: str = "Resource updated successfully"
    ) -> tuple:
        """
        Create a standardized updated response
        
        Args:
            data: Updated resource data
            message: Success message
        
        Returns:
            tuple: (jsonify response, 200)
        """
        return ResponseUtils.success_response(
            data=data,
            message=message,
            status_code=200
        )
    
    @staticmethod
    def deleted_response(
        message: str = "Resource deleted successfully"
    ) -> tuple:
        """
        Create a standardized deleted response
        
        Args:
            message: Success message
        
        Returns:
            tuple: (jsonify response, 200)
        """
        return ResponseUtils.success_response(
            data=None,
            message=message,
            status_code=200
        )
    
    @staticmethod
    def paginated_response(
        items: List[Any],
        page: int,
        per_page: int,
        total: int,
        message: str = "Data retrieved successfully"
    ) -> tuple:
        """
        Create a standardized paginated response
        
        Args:
            items: List of items for current page
            page: Current page number
            per_page: Items per page
            total: Total number of items
            message: Success message
        
        Returns:
            tuple: (jsonify response, 200)
        """
        pages = (total + per_page - 1) // per_page  # Calculate total pages
        
        pagination_meta = {
            "pagination": {
                "page": page,
                "pages": pages,
                "per_page": per_page,
                "total": total,
                "has_next": page < pages,
                "has_prev": page > 1
            }
        }
        
        return ResponseUtils.success_response(
            data=items,
            message=message,
            meta=pagination_meta,
            status_code=200
        )
    
    @staticmethod
    def internal_error_response(
        message: str = "Internal server error",
        error_code: str = "INTERNAL_ERROR"
    ) -> tuple:
        """
        Create a standardized internal error response
        
        Args:
            message: Error message
            error_code: Error code
        
        Returns:
            tuple: (jsonify response, 500)
        """
        return ResponseUtils.error_response(
            message=message,
            status_code=500,
            error_code=error_code
        )
    
    @staticmethod
    def unauthorized_response(
        message: str = "Unauthorized access",
        error_code: str = "UNAUTHORIZED"
    ) -> tuple:
        """
        Create a standardized unauthorized response
        
        Args:
            message: Error message
            error_code: Error code
        
        Returns:
            tuple: (jsonify response, 401)
        """
        return ResponseUtils.error_response(
            message=message,
            status_code=401,
            error_code=error_code
        )
    
    @staticmethod
    def forbidden_response(
        message: str = "Access forbidden",
        error_code: str = "FORBIDDEN"
    ) -> tuple:
        """
        Create a standardized forbidden response
        
        Args:
            message: Error message
            error_code: Error code
        
        Returns:
            tuple: (jsonify response, 403)
        """
        return ResponseUtils.error_response(
            message=message,
            status_code=403,
            error_code=error_code
        )
    
    @staticmethod
    def conflict_response(
        message: str = "Resource conflict",
        error_code: str = "CONFLICT"
    ) -> tuple:
        """
        Create a standardized conflict response
        
        Args:
            message: Error message
            error_code: Error code
        
        Returns:
            tuple: (jsonify response, 409)
        """
        return ResponseUtils.error_response(
            message=message,
            status_code=409,
            error_code=error_code
        )
