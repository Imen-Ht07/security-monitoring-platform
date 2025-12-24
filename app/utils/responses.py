"""
app/utils/responses.py
Classe utilitaire pour les réponses API uniformes
"""
from flask import jsonify
from datetime import datetime

class APIResponse:
    """Classe pour formater les réponses API"""
    
    @staticmethod
    def success(data=None, message="OK", status=200):
        """Réponse succès"""
        return jsonify({
            "success": True,
            "message": message,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }), status
    
    @staticmethod
    def created(data=None, message="Created"):
        """Réponse création (201)"""
        return APIResponse.success(data, message, 201)
    
    @staticmethod
    def error(message, status=500, error_code=None):
        """Réponse erreur"""
        return jsonify({
            "success": False,
            "message": message,
            "error_code": error_code or "SERVER_ERROR",
            "timestamp": datetime.utcnow().isoformat()
        }), status
    
    @staticmethod
    def bad_request(message):
        """Erreur 400"""
        return APIResponse.error(message, 400, "BAD_REQUEST")
    
    @staticmethod
    def unauthorized(message="Unauthorized"):
        """Erreur 401"""
        return APIResponse.error(message, 401, "UNAUTHORIZED")
    
    @staticmethod
    def forbidden(message="Forbidden"):
        """Erreur 403"""
        return APIResponse.error(message, 403, "FORBIDDEN")
    
    @staticmethod
    def not_found(message="Not found"):
        """Erreur 404"""
        return APIResponse.error(message, 404, "NOT_FOUND")
    
    @staticmethod
    def conflict(message="Conflict"):
        """Erreur 409"""
        return APIResponse.error(message, 409, "CONFLICT")
    
    @staticmethod
    def server_error(message="Server error"):
        """Erreur 500"""
        return APIResponse.error(message, 500, "SERVER_ERROR")