from datetime import datetime

def format_log_entry(log):
    """Formate une entrée log pour l'affichage"""
    return {
        "_id": str(log.get("_id", "")),
        "timestamp": log.get("@timestamp", ""),
        "event_type": log.get("event_type", ""),
        "username": log.get("username", "-"),
        "source_ip": log.get("source_ip", "-"),
        "severity": log.get("severity", "INFO"),
        "message": log.get("message", ""),
    }

def parse_date_range(date_start, date_end):
    """Parse les dates du filtre"""
    try:
        if date_start and date_end:
            return {
                "start": date_start,
                "end": date_end
            }
    except:
        pass
    return None

def get_time_ago(timestamp):
    """Calcule le temps écoulé"""
    if isinstance(timestamp, str):
        timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    
    delta = datetime.now(timestamp.tzinfo) - timestamp
    
    if delta.days > 0:
        return f"{delta.days}d ago"
    elif delta.seconds > 3600:
        return f"{delta.seconds // 3600}h ago"
    elif delta.seconds > 60:
        return f"{delta.seconds // 60}m ago"
    else:
        return "just now"