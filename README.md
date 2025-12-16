# 🛡️ Security Monitoring Platform

Plateforme complète d'analyse et de monitoring des logs de sécurité en temps réel.

## 📊 Stack Technique

- **Elasticsearch 8.15** : Indexation et recherche
- **Kibana 8.15** :  Dashboards
- **MongoDB 7.0** : Métadonnées
- **Redis 7-alpine** : Cache/Sessions
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

## 🔐 Sécurité

⚠️ **Important** :  En développement, la sécurité Elasticsearch est désactivée.  Activez-la avant d'utiliser en production. 

### Étapes Sécurité Production

1. Activer X-Pack Elasticsearch
2. Configurer authentification Kibana
3. Utiliser HTTPS/TLS
4. Secrets en variables d'env
5. Implémenter authentification API (Phase 8)

## 📈 Roadmap

**Phases 1-5** ✅ - Infrastructure de base (COMPLÈTE)
**Phases 6-7** 🔄 - Recherche avancée, uploads (EN COURS)
**Phases 8-15** ⬜ - Auth, ML, scalabilité (PLANIFIÉE)

## 🤝 Contributing

1. Fork → Feature branch → Pull request
2. Tests obligatoires
3. Documentation à jour

## 📄 Licence

MIT License

---

**Version** : 0.1.0-alpha (Phase 5)
**Dernière mise à jour** : 2025-12-16