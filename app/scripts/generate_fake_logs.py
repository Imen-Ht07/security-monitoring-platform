#!/usr/bin/env python3
# Script pour générer des logs factices pour les tests
# app/scripts/generate_fake_logs.py
import csv
import json
import random
from datetime import datetime, timedelta
import os

EVENT_TYPES = [
    "auth_success",
    "auth_fail",
    "intrusion_attempt",
    "access_sensitive",
    "firewall_block",
    "port_scan",
    "brute_force"
]

USERNAMES = ["admin", "user1", "user2", "user3", "analyst", "root", "service"]
IPS = [
    "192.168.1.100",
    "203.0.113.45",
    "198.51.100.7",
    "10.0.0.50",
    "203.0.113.200"
]
COUNTRIES = ["US", "FR", "DE", "CN", "RU", "Unknown"]
RESOURCES = ["database", "file_server", "api", "admin_panel", "user_data"]

def generate_csv_logs(filename="auth_logs.csv", num_logs=1000):
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "event_type", "username", "source_ip", "auth_result", "resource_accessed", "country", "severity"])
        now = datetime.utcnow()
        for i in range(num_logs):
            timestamp = (now - timedelta(hours=random.randint(0, 48))).isoformat()
            event_type = random.choice(EVENT_TYPES[:5])
            username = random.choice(USERNAMES)
            source_ip = random.choice(IPS)
            auth_result = "success" if random.random() > 0.3 else "fail"
            resource = random.choice(RESOURCES)
            country = random.choice(COUNTRIES)
            severity = "CRITICAL" if event_type == "intrusion_attempt" else "ERROR" if auth_result == "fail" else "INFO"
            writer.writerow([timestamp, event_type, username, source_ip, auth_result, resource, country, severity])
    print(f"Generated {num_logs} CSV logs in {filename}")

def generate_json_logs(filename="firewall_logs.json", num_logs=500):
    logs = []
    now = datetime.utcnow()
    for i in range(num_logs):
        timestamp = (now - timedelta(hours=random.randint(0, 48))).isoformat()
        event_type = random.choice(EVENT_TYPES[2:])
        source_ip = random.choice(IPS)
        country = random.choice(COUNTRIES)
        severity = "CRITICAL" if event_type in ["intrusion_attempt", "port_scan"] else "WARNING"
        log_entry = {
            "timestamp": timestamp,
            "event_type": event_type,
            "source_ip": source_ip,
            "destination_ip": "10.0.0.1",
            "country": country,
            "severity": severity,
            "message": f"{event_type} detected from {source_ip}",
            "blocked": random.choice([True, False])
        }
        logs.append(log_entry)
    with open(filename, "w") as f:
        for log in logs:
            f.write(json.dumps(log) + "\n")
    print(f"Generated {num_logs} JSON logs in {filename}")

if __name__ == "__main__":
    os.makedirs("/uploads", exist_ok=True)
    generate_csv_logs("/uploads/auth_logs_test.csv", 1000)
    generate_json_logs("/uploads/firewall_logs_test.json", 500)
    print("Test data generated successfully!")
