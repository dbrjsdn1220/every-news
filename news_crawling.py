import os
import feedparser
import requests
from bs4 import BeautifulSoup
import psycopg2
from datetime import datetime

# RSS 피드 URL
RSS_FEED_URL = "https://www.khan.co.kr/rss/rssdata/total_news.xml"

# PostgreSQL 연결 설정
conn = psycopg2.connect(
    host = "localhost",
    dbname = "news",
    user = os.getenv("DB_USERNAME"),
    password = os.getenv("DB_PASSWORD")
)
cur = conn.cursor()

def extract_article_data(link):
    try:
        response = requests.get(link)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # 예시 기준 (경향신문): 제목, 작성자, 날짜, 본문, 카테고리 추출
        title = soup.select_one("h1#article_title").get_text(strip=True)
        writer = soup.select_one("p.byline").get_text(strip=True).replace("기자", "").strip()
        date_str = soup.select_one("span.date01").get_text(strip=True)
        write_date = datetime.strptime(date_str, "%Y.%m.%d %H:%M")  # 날짜 포맷 확인 필요
        category = soup.select_one("div.location a:nth-of-type(2)").get_text(strip=True)
        content = "\n".join([p.get_text(strip=True) for p in soup.select("div.art_body > p")])

        return {
            "title": title,
            "writer": writer,
            "write_date": write_date,
            "category": category,
            "content": content
        }

    except Exception as e:
        print(f"[Error] {link} 파싱 실패: {e}")
        return None

def main():
    feed = feedparser.parse(RSS_FEED_URL)

    for entry in feed.entries:
        url = entry.link
        print(f"처리 중: {url}")

        article = extract_article_data(url)
        if not article:
            continue

        try:
            cur.execute("""
                INSERT INTO news_article (title, writer, write_date, category, content, url)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (url) DO NOTHING
            """, (
                article["title"],
                article["writer"],
                article["write_date"],
                article["category"],
                article["content"],
                url
            ))
            conn.commit()
        except Exception as e:
            print(f"[DB Error] 저장 실패: {e}")
            conn.rollback()

    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
