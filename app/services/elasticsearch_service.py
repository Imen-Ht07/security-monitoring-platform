"""
Service Elasticsearch - Support Docker et Local
"""
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError, NotFoundError
from datetime import datetime
import logging
import os
from dotenv import load_dotenv

# Charger .env
load_dotenv()

logger = logging.getLogger(__name__)

class ElasticsearchService:
    """Service Elasticsearch robuste pour Docker et local"""

    def __init__(self):
        # Lire depuis .env (priorité à ELASTICSEARCH_URL)
        self.es_url = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
        self.index = os.getenv("ELASTICSEARCH_INDEX", "logs_index")
        self.es = None
        self._connect()

    def _connect(self):
        """Établir la connexion Elasticsearch"""
        try:
            logger.info(f"🔗 Tentative de connexion à {self.es_url}...")
            
            # Configuration pour Docker et local
            self.es = Elasticsearch(
                [self.es_url],
                request_timeout=30,
                max_retries=3,
                verify_certs=False  # Pour développement (HTTPS)
            )
            
            # Test de connexion
            if self.es.ping():
                logger.info(f"✅ Connecté à Elasticsearch: {self.es_url}")
                logger.info(f"📊 Index: {self.index}")
                
                # Créer l'index automatiquement
                self.ensure_index()
            else:
                logger.error(f"⚠️ Elasticsearch ne répond pas: {self.es_url}")
                self.es = None
                
        except ConnectionError as e:
            logger.error(f"❌ Erreur de connexion Elasticsearch: {e}")
            logger.error(f"   Vérifiez que Elasticsearch est lancé sur {self.es_url}")
            self.es = None
        except Exception as e:
            logger.error(f"❌ Erreur inattendue: {type(e).__name__}: {e}")
            self.es = None

    def is_connected(self):
        """Vérifier si connecté"""
        if self.es is None:
            return False
        try:
            return self.es.ping()
        except Exception as e:
            logger.warning(f"⚠️ Connection check failed: {e}")
            return False

    def ensure_index(self):
        """Créer l'index s'il n'existe pas"""
        if not self.es:
            logger.error("❌ Elasticsearch n'est pas connecté")
            return False
        
        try:
            # Vérifier si l'index existe
            exists = self.es.indices.exists(index=self.index)
            
            if not exists:
                logger.info(f"📂 Création de l'index '{self.index}'...")
                self.es.indices.create(
                    index=self.index,
                    settings={
                        "number_of_shards": 1,
                        "number_of_replicas": 0
                    },
                    mappings={
                        "properties": {
                            "@timestamp": {"type": "date"},
                            "timestamp": {"type": "date"},
                            "event_type": {"type": "keyword"},
                            "severity": {"type": "keyword"},
                            "source_ip": {"type": "keyword"},
                            "destination_ip": {"type": "keyword"},
                            "country": {"type": "keyword"},
                            "username": {"type": "keyword"},
                            "message": {"type": "text"},
                            "description": {"type": "text"},
                            "source_system": {"type": "keyword"},
                            "blocked": {"type": "boolean"}
                        }
                    }
                )
                logger.info(f"✅ Index '{self.index}' créé avec succès")
            else:
                logger.info(f"✅ Index '{self.index}' existe déjà")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur création index: {e}")
            return False

    # ================= STATS DASHBOARD =================
    def get_stats(self):
        """Récupérer les stats globales"""
        if not self.is_connected():
            logger.error("❌ Elasticsearch n'est pas connecté")
            return {"total_logs": 0, "today_logs": 0, "error_logs": 0}
        
        try:
            total = self.es.count(index=self.index)["count"]

            today = datetime.now().strftime("%Y-%m-%d")
            today_logs = self.es.count(
                index=self.index,
                query={
                    "range": {
                        "@timestamp": {
                            "gte": f"{today}T00:00:00",
                            "lte": f"{today}T23:59:59"
                        }
                    }
                }
            )["count"]

            error_logs = self.es.count(
                index=self.index,
                query={"match": {"severity": "ERROR"}}
            )["count"]

            logger.info(f"📊 Stats: {total} logs total, {today_logs} aujourd'hui, {error_logs} erreurs")

            return {
                "total_logs": total,
                "today_logs": today_logs,
                "error_logs": error_logs
            }
        except Exception as e:
            logger.error(f"❌ Stats error: {e}")
            return {"total_logs": 0, "today_logs": 0, "error_logs": 0}

    # ================= BASIC SEARCH =================
    def search(self, query_text=None, page=0, size=50):
        """Recherche simple"""
        if not self.is_connected():
            logger.error("❌ Elasticsearch n'est pas connecté")
            return {"total": 0, "logs": []}
        
        try:
            must = []

            if query_text:
                must.append({
                    "multi_match": {
                        "query": query_text,
                        "fields": [
                            "event_type^2",
                            "message",
                            "username",
                            "source_ip"
                        ],
                        "fuzziness": "AUTO"
                    }
                })

            query = {"bool": {"must": must or [{"match_all": {}}]}}

            result = self.es.search(
                index=self.index,
                query=query,
                from_=page * size,
                size=size,
                sort=[{"@timestamp": {"order": "desc"}}]
            )

            return {
                "total": result["hits"]["total"]["value"],
                "logs": [hit["_source"] for hit in result["hits"]["hits"]]
            }
        except Exception as e:
            logger.error(f"❌ Search error: {e}")
            return {"total": 0, "logs": []}

    # ================= ADVANCED SEARCH =================
    def advanced_search(self, filters, page=0, size=50):
        """Recherche avancée avec filtres"""
        if not self.is_connected():
            logger.error("❌ Elasticsearch n'est pas connecté")
            return {"total": 0, "logs": []}
        
        try:
            must = []
            filter_clauses = []

            # Query text
            if filters.get("query_text"):
                must.append({
                    "multi_match": {
                        "query": filters["query_text"],
                        "fields": ["event_type", "username", "source_ip", "message"],
                        "fuzziness": "AUTO"
                    }
                })

            # Severity filter
            if filters.get("severity"):
                severities = filters["severity"] if isinstance(filters["severity"], list) else [filters["severity"]]
                filter_clauses.append({
                    "terms": {"severity": severities}
                })

            # Event type filter
            if filters.get("event_type"):
                event_types = filters["event_type"] if isinstance(filters["event_type"], list) else [filters["event_type"]]
                filter_clauses.append({
                    "terms": {"event_type": event_types}
                })

            # Country filter
            if filters.get("country"):
                countries = filters["country"] if isinstance(filters["country"], list) else [filters["country"]]
                filter_clauses.append({
                    "terms": {"country": countries}
                })

            # Source IP filter
            if filters.get("source_ip"):
                filter_clauses.append({
                    "term": {"source_ip": filters["source_ip"]}
                })

            # Date range filter
            if filters.get("date_from") or filters.get("date_to"):
                range_q = {}
                if filters.get("date_from"):
                    range_q["gte"] = f"{filters['date_from']}T00:00:00"
                if filters.get("date_to"):
                    range_q["lte"] = f"{filters['date_to']}T23:59:59"
                filter_clauses.append({"range": {"@timestamp": range_q}})

            # Build query
            query = {
                "bool": {
                    "must": must or [{"match_all": {}}],
                    "filter": filter_clauses or []
                }
            }

            result = self.es.search(
                index=self.index,
                query=query,
                from_=page * size,
                size=size,
                sort=[{"@timestamp": {"order": "desc"}}]
            )

            return {
                "total": result["hits"]["total"]["value"],
                "logs": [hit["_source"] for hit in result["hits"]["hits"]]
            }
        except Exception as e:
            logger.error(f"❌ Advanced search error: {e}")
            return {"total": 0, "logs": []}

    # ================= AGGREGATIONS =================
    def get_severity_distribution(self):
        """Distribution des sévérités"""
        if not self.is_connected():
            return []
        
        try:
            result = self.es.search(
                index=self.index,
                size=0,
                aggs={
                    "severity": {
                        "terms": {"field": "severity", "size": 100}
                    }
                }
            )

            return [
                {"severity": b["key"], "count": b["doc_count"]}
                for b in result["aggregations"]["severity"]["buckets"]
            ]
        except Exception as e:
            logger.error(f"❌ Severity aggregation error: {e}")
            return []

    def get_top_ips(self, limit=10):
        """Top IPs sources"""
        if not self.is_connected():
            return []
        
        try:
            result = self.es.search(
                index=self.index,
                size=0,
                aggs={
                    "top_ips": {
                        "terms": {"field": "source_ip", "size": limit}
                    }
                }
            )

            return [
                {"ip": b["key"], "count": b["doc_count"]}
                for b in result["aggregations"]["top_ips"]["buckets"]
            ]
        except Exception as e:
            logger.error(f"❌ Top IPs error: {e}")
            return []

    # ================= BULK INDEX =================
    def bulk_index_logs(self, logs):
        """Indexer plusieurs logs en une seule requête"""
        if not self.es:
            logger.error("❌ Elasticsearch n'est pas connecté")
            return {"indexed": 0, "failed": len(logs), "total": len(logs)}

        if not logs:
            return {"indexed": 0, "failed": 0, "total": 0}

        # Assurer l'existence de l'index
        self.ensure_index()

        try:
            actions = []
            for log in logs:
                actions.append({"index": {"_index": self.index}})
                actions.append(log)

            response = self.es.bulk(operations=actions, request_timeout=60)
            
            # Compter les erreurs
            failed = 0
            if response.get("errors"):
                for item in response.get("items", []):
                    if item.get("index", {}).get("error"):
                        failed += 1
                        logger.warning(f"⚠️ Index error: {item.get('index', {}).get('error')}")

            indexed = len(logs) - failed

            logger.info(f"✅ Bulk index: {indexed}/{len(logs)} logs indexés")

            return {
                "indexed": indexed,
                "failed": failed,
                "total": len(logs)
            }
        except Exception as e:
            logger.error(f"❌ Bulk index error: {e}")
            return {
                "indexed": 0,
                "failed": len(logs),
                "total": len(logs)
            }

    # ================= SINGLE INDEX =================
    def index_log(self, log):
        """Indexer un seul log"""
        if not self.es:
            logger.error("❌ Elasticsearch n'est pas connecté")
            return False

        try:
            self.ensure_index()
            self.es.index(index=self.index, body=log)
            return True
        except Exception as e:
            logger.error(f"❌ Index error: {e}")
            return False

    # ================= DELETE INDEX =================
    def delete_all_logs(self):
        """Supprimer tous les logs"""
        if not self.es:
            logger.error("❌ Elasticsearch n'est pas connecté")
            return False

        try:
            self.es.indices.delete(index=self.index, ignore_unavailable=True)
            logger.info(f"✅ Index '{self.index}' supprimé")
            return True
        except Exception as e:
            logger.error(f"❌ Delete index error: {e}")
            return False

    def ping(self):
        """Alias pour is_connected()"""
        return self.is_connected()

# ================= HELPER FUNCTIONS =================
def get_es_service():
    """Factory pour obtenir une instance ElasticsearchService"""
    return ElasticsearchService()