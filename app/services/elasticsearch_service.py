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
            return {"total_logs": 0, "critical_count": 0, "today_count": 0, "unique_ips": 0}
        
        try:
            total = self.es.count(index=self.index)["count"]

            today = datetime.now().strftime("%Y-%m-%d")
            today_count = self.es.count(
                index=self.index,
                query={
                    "range": {
                        "timestamp": {
                            "gte": f"{today}T00:00:00",
                            "lte": f"{today}T23:59:59"
                        }
                    }
                }
            )["count"]

            critical_count = self.es.count(
                index=self.index,
                query={"term": {"severity": "CRITICAL"}}
            )["count"]

            unique_ips = self.es.search(
                index=self.index,
                size=0,
                aggs={
                    "unique_ips": {
                        "cardinality": {"field": "source_ip"}
                    }
                }
            )["aggregations"]["unique_ips"]["value"]

            logger.info(f"📊 Stats: {total} logs total, {today_count} aujourd'hui, {critical_count} critical, {unique_ips} unique IPs")

            return {
                "total_logs": total,
                "critical_count": critical_count,
                "today_count": today_count,
                "unique_ips": unique_ips
            }
        except Exception as e:
            logger.error(f"❌ Stats error: {e}")
            return {"total_logs": 0, "critical_count": 0, "today_count": 0, "unique_ips": 0}

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
                sort=[{"timestamp": {"order": "desc"}}]
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
            query_text = filters.get("query", "*")
            inner_filters = filters.get("filters", {})

            if query_text and query_text != "*":
                must.append({
                    "multi_match": {
                        "query": query_text,
                        "fields": ["event_type^2", "message", "username", "source_ip"],
                        "fuzziness": "AUTO"
                    }
                })

            # Severity filter
            if inner_filters.get("severity"):
                severities = inner_filters["severity"] if isinstance(inner_filters["severity"], list) else [inner_filters["severity"]]
                filter_clauses.append({
                    "terms": {"severity": severities}
                })

            # Event type filter
            if inner_filters.get("event_type"):
                event_types = inner_filters["event_type"] if isinstance(inner_filters["event_type"], list) else [inner_filters["event_type"]]
                filter_clauses.append({
                    "terms": {"event_type": event_types}
                })

            # Country filter
            if inner_filters.get("country"):
                countries = inner_filters["country"] if isinstance(inner_filters["country"], list) else [inner_filters["country"]]
                filter_clauses.append({
                    "terms": {"country": countries}
                })

            # Source IP prefix filter
            if inner_filters.get("source_ip"):
                filter_clauses.append({
                    "prefix": {"source_ip": inner_filters["source_ip"]}
                })

            # Username filter - Changed to match for potential analyzed field or partial match
            if inner_filters.get("username"):
                filter_clauses.append({
                    "match": {"username": {
                        "query": inner_filters["username"],
                        "operator": "and"
                    }}
                })

            # Date range filter
            if inner_filters.get("date_from") or inner_filters.get("date_to"):
                range_q = {"range": {"timestamp": {}}}
                if inner_filters.get("date_from"):
                    range_q["range"]["timestamp"]["gte"] = f"{inner_filters['date_from']}T00:00:00"
                if inner_filters.get("date_to"):
                    range_q["range"]["timestamp"]["lte"] = f"{inner_filters['date_to']}T23:59:59.999"
                filter_clauses.append(range_q)

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
                sort=[{"timestamp": {"order": "desc"}}]
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