# consumer/news_consumer.py

from pyflink.datastream import StreamExecutionEnvironment
from pyflink.common.serialization import SimpleStringSchema
from pyflink.datastream.connectors import FlinkKafkaConsumer
from pyflink.common.typeinfo import Types
from datetime import datetime
from dotenv import load_dotenv
import json
import os
import psycopg2
import subprocess
from elasticsearch import Elasticsearch
from openai_api import (
    transform_classify_category,
    transform_extract_keywords,
    transform_to_embedding,
)

# 1. 환경 설정
load_dotenv()
env = StreamExecutionEnvironment.get_execution_environment()

# Elasticsearch 클라이언트 초기화
es = Elasticsearch("http://localhost:9200")

# Kafka connector JAR 등록
kafka_connector_path = os.getenv("KAFKA_CONNECTOR_PATH")
env.add_jars(f"file://{kafka_connector_path}")

# Kafka Consumer 설정
kafka_props = {
    "bootstrap.servers": "localhost:9092",
    "group.id": "flink_consumer_group",
}

consumer = FlinkKafkaConsumer(
    topics="news", deserialization_schema=SimpleStringSchema(), properties=kafka_props
)


# 2. PostgreSQL 저장 함수
def save_to_postgres(data):
    conn = psycopg2.connect(
        host="localhost",
        dbname="news",
        user=os.getenv("DB_USERNAME"),
        password=os.getenv("DB_PASSWORD"),
        port=5432,
    )
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO news_article (title, writer, write_date, category, content, url, keywords, embedding, views)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (url) DO NOTHING RETURNING id
        """,
        (
            data["title"],
            data["writer"],
            data["write_date"],
            data["category"],
            data["content"],
            data["url"],
            json.dumps(data["keywords"], ensure_ascii=False),
            json.dumps(data["embedding"]),
            0,
        ),
    )
    row = cursor.fetchone()
    article_id = row[0] if row else -1

    conn.commit()
    cursor.close()
    conn.close()

    print(article_id, data["title"])
    if article_id != -1:
        print("PostgreSQL, ", end='')
    return article_id


def save_to_elasticsearch(id, data):
    es = Elasticsearch("http://localhost:9200")
    try:
        es.index(
            index="news",
            document={
                "id": id,
                "title": data["title"],
                "writer": data["writer"],
                "category": data["category"],
                "write_date": datetime.strptime(data["write_date"], "%Y-%m-%d %H:%M"),
                "content": data["content"],
                "url": data["url"],
                "keywords": data["keywords"],
            }
        )
        print("ElasticSearch, ", end='')
    except Exception as e:
        print(f"ElasticSearch 저장 중 오류 발생: {e}")


def save_to_json(data):
    write_date = datetime.now().strftime("%Y-%m-%d")
    file_path = f"./batch/data/{write_date}.json"
    os.makedirs("./batch/data", exist_ok=True)

    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            existing_data = json.load(f)
    else:
        existing_data = []

    # embedding 제거하고 저장
    data_to_save = data.copy()
    if "embedding" in data_to_save:
        del data_to_save["embedding"]

    existing_data.append(data_to_save)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=2)
    
    print("Json, ", end='')


def save_to_hdfs(data):
    write_date = datetime.now().strftime("%Y-%m-%d")
    file_path = f"./batch/data/{write_date}.json"
    hdfs_path = f"/news/{write_date}.json"

    if os.path.exists(file_path):
        subprocess.run(["hdfs", "dfs", "-mkdir", "-p", "/news"])
        subprocess.run(["hdfs", "dfs", "-put", "-f", file_path, hdfs_path])
    
    print("HDFS 저장 완료")



# 3. Kafka에서 가져온 데이터를 전처리하고 저장하는 함수
def process_and_save(news_json):
    news = json.loads(news_json)

    content = news.get("content", "")

    # 전처리 (OpenAI API 호출)
    keywords = transform_extract_keywords(content)
    category = transform_classify_category(content)
    embedding = transform_to_embedding(content)

    # DB에 저장할 데이터 구성
    data = {
        "title": news.get("title"),
        "writer": news.get("writer"),
        "write_date": news.get("write_date"),
        "category": category,
        "content": content,
        "url": news.get("url"),
        "keywords": keywords,
        "embedding": embedding,
    }
    article_id = save_to_postgres(data)
    if article_id != -1:
        save_to_elasticsearch(article_id, data)
        save_to_json(data)
        save_to_hdfs(data)


# 4. Flink 데이터 흐름 연결
stream = env.add_source(consumer)

# Kafka에서 읽은 데이터를 파싱 + 전처리 + DB 저장
stream.map(lambda x: process_and_save(x), output_type=Types.STRING())

# 5. Flink 작업 실행
env.execute("Flink Kafka Consumer Job")
