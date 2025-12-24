# app/models/__init__.py
# Import tous les modèles pour y accéder facilement
from .uploaded_file import UploadedFile
from .saved_search import SavedSearch

__all__ = ['UploadedFile', 'SavedSearch']