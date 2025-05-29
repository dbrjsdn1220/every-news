from django.core.management.base import BaseCommand
from elasticsearch import Elasticsearch

class Command(BaseCommand):
    help = 'Elasticsearch 인덱스 news를 생성합니다.'

    def handle(self, *args, **kwargs):
        es = Elasticsearch("http://localhost:9200")

        index_name = "news"
        settings = {
            "analysis": {
                "analyzer": {
                    "korean_analyzer": {
                        "type": "standard"
                    }
                }
            }
        }
        mappings = {
            "properties": {
                "id": { "type": "integer" },
                "title": { 
                    "type": "text", 
                    "analyzer": "korean_analyzer",
                    "fields": {
                        "suggest": {
                            "type": "completion",
                            "analyzer": "simple",
                            "preserve_separators": True,
                            "preserve_position_increments": True,
                            "max_input_length": 50
                        }
                    }
                },
                "content": { "type": "text", "analyzer": "korean_analyzer" },
                "writer": { "type": "keyword" },
                "category": { "type": "keyword" },
                "write_date": { "type": "date" },
                "keywords": { 
                    "type": "keyword",
                    "fields": {
                        "suggest": {
                            "type": "completion",
                            "analyzer": "simple",
                            "preserve_separators": True,
                            "preserve_position_increments": True,
                            "max_input_length": 50
                        }
                    }
                },
            }
        }

        if es.indices.exists(index=index_name):
            self.stdout.write(self.style.WARNING(f"{index_name} 인덱스를 삭제합니다."))
            es.indices.delete(index=index_name)

        es.indices.create(
            index=index_name,
            settings=settings,
            mappings=mappings
        )
        self.stdout.write(self.style.SUCCESS(f"{index_name} 인덱스 생성 완료!"))