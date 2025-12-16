from elasticsearch import Elasticsearch
from config import Config
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ElasticsearchService:
    """Service pour interagir avec Elasticsearch"""

    def __init__(self):
        self.es = Elasticsearch([Config.ELASTICSEARCH_URL])
        self.index = Config.ELASTICSEARCH_INDEX

    def get_stats(self):
        """Récupère des statistiques globales sur les logs"""
        try:
            # Total logs
            count_result = self.es.count(index=self.index)
            total = count_result.get("count", 0)

            # Logs d'aujourd'hui
            today = datetime.now().strftime("%Y-%m-%d")
            today_result = self.es.count(
                index=self.index,
                query={
                    "range": {
                        "@timestamp": {
                            "gte": f"{today}T00:00:00",
                            "lte": f"{today}T23:59:59"
                        }
                    }
                }
            )
            today_count = today_result.get("count", 0)

            # Logs ERROR
            error_result = self.es.count(
                index=self.index,
                query={"term": {"severity.keyword": "ERROR"}}
            )
            error_count = error_result.get("count", 0)

            return {
                "total_logs": total,
                "today_logs": today_count,
                "error_logs": error_count
            }

        except Exception as e:
            logger.error(f"Erreur stats Elasticsearch: {str(e)}")
            return {
                "total_logs": 0,
                "today_logs": 0,
                "error_logs": 0,
                "error": str(e)
            }

    def search_logs(self, query_term=None, filters=None, page=0, page_size=50):
        """Recherche des logs avec texte + filtres"""
        try:
            must_clauses = []

            # Recherche texte
            if query_term:
                must_clauses.append({
                    "multi_match": {
                        "query": query_term,
                        "fields": [
                            "message",
                            "event_type^2",
                            "username",
                            "source_ip",
                            "destination_ip"
                        ],
                        "fuzziness": "AUTO"
                    }
                })

            # Filtre severity
            if filters and filters.get("log_level"):
                must_clauses.append({
                    "term": {
                        "severity.keyword": filters["log_level"]
                    }
                })

            query = {
                "bool": {
                    "must": must_clauses if must_clauses else [{"match_all": {}}]
                }
            }

            result = self.es.search(
                index=self.index,
                query=query,
                size=page_size,
                from_=page * page_size,
                sort=[{"@timestamp": {"order": "desc"}}]
            )

            logs = [hit["_source"] for hit in result["hits"]["hits"]]

            logger.info(
                f"Recherche logs | term='{query_term}' | level='{filters.get('log_level') if filters else None}'"
            )

            return {
                "logs": logs,
                "total": result["hits"]["total"]["value"],
                "page": page
            }

        except Exception as e:
            logger.error(f"Erreur recherche Elasticsearch: {str(e)}")
            return {
                "logs": [],
                "total": 0,
                "error": str(e)
            }

    def bulk_index_logs(self, logs):
        """Indexation bulk des logs"""
        if not logs:
            return {"indexed": 0, "failed": 0, "total": 0}

        try:
            actions = []

            for log in logs:
                actions.append({
                    "index": {"_index": self.index}
                })
                actions.append(log)

            response = self.es.bulk(operations=actions)

            failed = len(response.get("items", [])) if response.get("errors") else 0
            indexed = len(logs) - failed

            logger.info(
                f"Bulk index terminé : {indexed} indexés, {failed} échoués"
            )

            return {
                "indexed": indexed,
                "failed": failed,
                "total": len(logs)
            }

        except Exception as e:
            logger.error(f"Erreur bulk Elasticsearch: {str(e)}")
            return {
                "indexed": 0,
                "failed": len(logs),
                "error": str(e)
            }
