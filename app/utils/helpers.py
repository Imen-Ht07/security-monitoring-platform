def format_log_entry(log):
    return {
        "_id": log.get("_id"),
        "timestamp": log.get("@timestamp", ""),
        "event_type": log.get("event_type", ""),
        "username": log.get("username", "-"),
        "source_ip": log.get("source_ip", "-"),
        "severity": log.get("severity", log.get("log_level", "INFO")),
        "message": log.get("message", log.get("resource_accessed", "")),
    }
