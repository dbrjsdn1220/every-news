from kafka import KafkaProducer
import feedparser
import json
import time
from news_crawling import clean_writer, format_date, crawl_article

# Kafka 브로커 주소
KAFKA_BROKER = "localhost:9092"
# Kafka 토픽 이름
TOPIC = "news"

# Kafka Producer 생성 (value는 JSON 직렬화)
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

RSS_FEED_URL = "https://www.khan.co.kr/rss/rssdata/total_news.xml"

collected_url = []

while True:
    print("경향신문 RSS 피드를 확인하는 중 ...")
    feed = feedparser.parse(RSS_FEED_URL)

    for entry in feed.entries:
        # 중복 확인
        if entry.link not in collected_url:
            title = entry.get("title", "제목없음")
            writer = clean_writer(entry.get("author", "작성자 없음"))
            write_date = format_date(entry.get("date", "날짜 없음"))
            category = entry.get("category", "카테고리 없음")
            content = crawl_article(entry.link)
            url = entry.link

            # DB에 저장
            data = {
                "title": title,
                "writer": writer,
                "write_date": write_date if write_date != "날짜 형식 오류" else None,
                # "category": category,
                "content": content,
                "url": url,
            }
            producer.send(TOPIC, data)

            print(title)
            collected_url.append(url)  # url 저장

    producer.flush()
    time.sleep(60)
