"""
app/routes/api_history.py
Gestion de l'historique des recherches sauvegardées
"""
from flask import Blueprint, request, jsonify
from app.models.saved_search import SavedSearch
import logging

logger = logging.getLogger(__name__)

bp_history = Blueprint("api_history", __name__, url_prefix="/api/search-history")

# ================= GET HISTORY =================
@bp_history.route("", methods=["GET"])
def get_search_history():
    """Récupère l'historique des recherches (10 dernières)"""
    try:
        limit = request.args.get('limit', 10, type=int)
        history = SavedSearch.get_all()[:limit]  # ✅ Utiliser la méthode static
        return jsonify({
            "success": True,
            "data": history
        }), 200
    except Exception as e:
        logger.error(f"History error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# ================= GET BY ID =================
@bp_history.route("/<search_id>", methods=["GET"])
def get_search_by_id(search_id):
    """Récupère une recherche sauvegardée par ID"""
    try:
        search = SavedSearch.get_by_id(search_id)
        if not search:
            return jsonify({
                "success": False,
                "error": "Search not found"
            }), 404
        
        return jsonify({
            "success": True,
            "data": {
                "id": search_id,
                "name": search.name,
                "description": search.description,
                "filters": search.filters,
                "created_at": search.created_at.isoformat()
            }
        }), 200
    except Exception as e:
        logger.error(f"Get search error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# ================= CREATE =================
@bp_history.route("", methods=["POST"])
def save_search():
    """Crée une nouvelle recherche sauvegardée"""
    try:
        data = request.get_json() or {}
        
        # Validation
        if not data.get('name'):
            return jsonify({
                "success": False,
                "error": "Name is required"
            }), 400
        
        # Créer la recherche
        search = SavedSearch(
            name=data.get('name'),
            description=data.get('description', ''),
            filters=data.get('filters', {})
        )
        search.save()
        
        logger.info(f"Search '{search.name}' created")
        
        return jsonify({
            "success": True,
            "id": str(search.id),
            "message": "Search saved successfully"
        }), 201
    except Exception as e:
        logger.error(f"Save search error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# ================= DELETE =================
@bp_history.route("/<search_id>", methods=["DELETE"])
def delete_search(search_id):
    """Supprime une recherche sauvegardée"""
    try:
        SavedSearch.delete_by_id(search_id)
        logger.info(f"Search '{search_id}' deleted")
        
        return jsonify({
            "success": True,
            "message": "Search deleted"
        }), 200
    except Exception as e:
        logger.error(f"Delete search error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500