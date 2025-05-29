import psycopg2
from elasticsearch import Elasticsearch
import json
from dotenv import load_dotenv
import os

# 저장되어 있는 데이터를 Elasticsearch로 마이그레이션
# 환경 변수 로드
load_dotenv()

# PostgreSQL 연결
conn = psycopg2.connect(
    host="localhost",
    dbname="news",
    user=os.getenv("DB_USERNAME"),
    password=os.getenv("DB_PASSWORD"),
    port=5432,
)
cursor = conn.cursor()

# Elasticsearch 클라이언트 초기화
es = Elasticsearch("http://localhost:9200")

# PostgreSQL에서 데이터 조회
cursor.execute("""
    SELECT id, title, writer, write_date, category, content, url, keywords, views
    FROM news_article
""")

# 데이터를 Elasticsearch로 마이그레이션
for row in cursor.fetchall():
    try:
        # PostgreSQL row를 딕셔너리로 변환
        doc = {
            "id": row[0],
            "title": row[1],
            "writer": row[2],
            "write_date": row[3],
            "category": row[4],
            "content": row[5],
            "url": row[6],
            "keywords": row[7],
        }
        
        # Elasticsearch에 저장
        es.index(index="news", document=doc)
        print(f"문서 저장 완료: {doc['title']}")
        
    except Exception as e:
        print(f"문서 저장 중 오류 발생: {e}")

# 연결 종료
cursor.close()
conn.close()

print("마이그레이션 완료!") 