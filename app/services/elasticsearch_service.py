from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import os


class ElasticsearchService:
    def __init__(self):
        self.es_url = os.getenv("ELASTICSEARCH_URL", "http://elasticsearch:9200")
        self.es = Elasticsearch([self.es_url])

    def search_logs(self, query_term="", filters=None, page=0, page_size=50):
        if filters is None:
            filters = {}

        es_query = {
            "bool": {
                "must": [],
                "filter": []
            }
        }

        if query_term:
            es_query["bool"]["must"].append({
                "multi_match": {
                    "query": query_term,
                    "fields": ["message", "username", "source_ip", "resource_accessed"]
                }
            })

        if filters.get("log_level"):
            es_query["bool"]["filter"].append({
                "terms": {"log_level": filters["log_level"]}
            })

        if filters.get("event_type"):
            es_query["bool"]["filter"].append({
                "terms": {"event_type": filters["event_type"]}
            })

        if filters.get("date_range"):
            es_query["bool"]["filter"].append({
                "range": {
                    "@timestamp": {
                        "gte": filters["date_range"]["start"],
                        "lte": filters["date_range"]["end"]
                    }
                }
            })

        try:
            result = self.es.search(
                index="security-logs-*",
                query=es_query,
                from_=page * page_size,
                size=page_size,
                sort=[{"@timestamp": {"order": "desc"}}]
            )

            hits = result["hits"]["hits"]
            total = result["hits"]["total"]["value"]

            logs = []
            for hit in hits:
                log = hit["_source"]
                log["_id"] = hit["_id"]
                logs.append(log)

            return {
                "logs": logs,
                "total": total,
                "page": page,
                "page_size": page_size,
                "num_pages": (total + page_size - 1) // page_size
            }
        except Exception as e:
            return {"error": str(e), "logs": [], "total": 0}

    def get_stats(self):
        try:
            total_result = self.es.count(index="security-logs-*")
            total_logs = total_result["count"]

            today_result = self.es.count(
                index="security-logs-*",
                query={
                    "range": {"@timestamp": {"gte": "now/d", "lt": "now/d+1d"}}
                }
            )
            today_logs = today_result["count"]

            error_result = self.es.count(
                index="security-logs-*",
                query={"terms": {"log_level": ["ERROR", "CRITICAL"]}}
            )
            error_logs = error_result["count"]

            return {
                "total_logs": total_logs,
                "today_logs": today_logs,
                "error_logs": error_logs
            }
        except Exception as e:
            return {
                "error": str(e),
                "total_logs": 0,
                "today_logs": 0,
                "error_logs": 0
            }

    def bulk_index_logs(self, logs_list):
        from datetime import datetime
        try:
            actions = []
            for log in logs_list:
                actions.append({
                    "_index": f"security-logs-{datetime.utcnow().strftime('%Y.%m.%d')}",
                    "_source": log
                })

            success, _ = bulk(self.es, actions)
            return {"indexed": success, "failed": 0}
        except Exception as e:
            return {"error": str(e), "indexed": 0, "failed": len(logs_list)}
