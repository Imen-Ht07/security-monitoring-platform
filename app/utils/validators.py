"""
app/utils/validators.py
Classe utilitaire pour valider les inputs
"""
import re
from datetime import datetime

class Validators:
    """Classe pour valider les données"""
    
    @staticmethod
    def validate_email(email):
        """Valide une adresse email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_ip(ip):
        """Valide une adresse IP"""
        pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if not re.match(pattern, ip):
            return False
        parts = ip.split('.')
        return all(0 <= int(part) <= 255 for part in parts)
    
    @staticmethod
    def validate_date(date_str):
        """Valide une date au format ISO"""
        try:
            datetime.fromisoformat(date_str)
            return True
        except:
            return False
    
    @staticmethod
    def validate_severity(severity):
        """Valide une sévérité"""
        valid = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]
        return severity.upper() in valid
    
    @staticmethod
    def validate_event_type(event_type):
        """Valide un type d'événement"""
        valid = [
            "auth_success", "auth_fail", "intrusion_attempt",
            "access_sensitive", "firewall_block", "port_scan",
            "brute_force", "malware_detection"
        ]
        return event_type.lower() in valid
    
    @staticmethod
    def validate_country(country):
        """Valide un code pays ISO"""
        return len(country) == 2 and country.isalpha()
    
    @staticmethod
    def validate_search_filters(filters):
        """Valide l'objet filters complet"""
        if not isinstance(filters, dict):
            return False, "Filters must be an object"
        
        # Valider date_from
        if filters.get('date_from') and not Validators.validate_date(filters['date_from']):
            return False, "Invalid date_from format"
        
        # Valider date_to
        if filters.get('date_to') and not Validators.validate_date(filters['date_to']):
            return False, "Invalid date_to format"
        
        # Valider severity
        if filters.get('severity'):
            if not isinstance(filters['severity'], list):
                return False, "Severity must be an array"
            for sev in filters['severity']:
                if not Validators.validate_severity(sev):
                    return False, f"Invalid severity: {sev}"
        
        # Valider event_type
        if filters.get('event_type'):
            if not isinstance(filters['event_type'], list):
                return False, "Event type must be an array"
        
        # Valider country
        if filters.get('country'):
            if not isinstance(filters['country'], list):
                return False, "Country must be an array"
        
        return True, "Valid"