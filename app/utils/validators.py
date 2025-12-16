from config import Config

def allowed_file(filename):
    """Vérifie si le fichier est autorisé"""
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def validate_search_params(search_term):
    """Valide les paramètres de recherche"""
    if not search_term:
        return True, None
    
    if len(search_term) > 500:
        return False, "Search term too long"
    
    return True, None