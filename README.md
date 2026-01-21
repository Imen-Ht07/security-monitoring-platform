# 🛡️ Security Monitoring Platform

Plateforme complète d'analyse et de monitoring des logs de sécurité en temps réel.

## 📊 Stack Technique

- **Elasticsearch 8.15** : Indexation et recherche
- **Kibana 8.15** :  Dashboards
- **MongoDB 7.0** : Métadonnées
- **Flask 3.0.3** : API REST
- **Docker Compose** : Orchestration

## 🚀 Démarrage Rapide

```bash
# 1. Cloner
git clone https://github.com/Imen-Ht07/security-monitoring-platform.git
cd security-monitoring-platform

# 2. Configuration
cp .env.example .env
# Éditer .env avec vos credentials

# 3. Lancer
docker-compose up -d

# 4. Accès
# Dashboard:  http://localhost:8001
# API: http://localhost:8001/api
# Kibana: http://localhost:5601
```

## 📡 API Endpoints

### Health & Stats
```bash
GET /api/health              # Status global
GET /api/stats               # Statistiques
```

### Ingestion
```bash
POST /api/ingest             # Charger CSV/JSON
```

### Recherche
```bash
GET /api/search? q=<query>&severity=<LEVEL>&page=0&size=50
POST /api/search/advanced    # Filtres avancés
```

### Uploads
```bash
GET /api/uploads             # Historique
DELETE /api/uploads/<id>     # Supprimer
```

### Analytics
```bash
GET /api/analytics/top-ips
GET /api/analytics/timeline
GET /api/analytics/event-types
```
**Dernière mise à jour** : 2025-12-16
