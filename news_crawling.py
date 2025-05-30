import psycopg2
import os
from dotenv import load_dotenv
import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# 환경변수 불러오기
load_dotenv()

conn = psycopg2.connect(
    host="localhost",
    dbname="news",
    user=os.getenv("DB_USERNAME"),
    password=os.getenv("DB_PASSWORD"),
)
cur = conn.cursor()

# RSS 피드 URL (예: Khan 뉴스 RSS)
RSS_FEED_URL1 = "https://www.khan.co.kr/rss/rssdata/total_news.xml"
RSS_FEED_URL2 = "https://rss.ohmynews.com/rss/ohmynews.xml"


# 뉴스 데이터를 db로 저장하는 함수
def save_to_db(data):
    insert_query = """
    INSERT INTO news_article (title, writer, write_date, category, content, url)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON CONFLICT (url) DO NOTHING;
    """
    cur.execute(
        insert_query,
        (
            data["title"],
            data["writer"],
            data["write_date"],
            data["category"],
            data["content"],
            data["url"],
        ),
    )
    conn.commit()


# 작성자 정보 전처리하는 함수
def clean_writer(raw_writer):
    # '기자'를 기준으로 자르고 공백 제거
    if "선임기자" in raw_writer:
        raw_writer = raw_writer.split("선임기자")[0].strip()
    if "기자" in raw_writer:
        raw_writer = raw_writer.split("기자")[0].strip()
    if "특파원" in raw_writer:
        if "|" in raw_writer:
            raw_writer = raw_writer.split("|")[1].strip()
        raw_writer = raw_writer.split("특파원")[0].strip()
    return raw_writer.strip()


# 날짜 형식 전처리하는 함수
def format_date(iso_date_str):
    try:
        dt = datetime.fromisoformat(iso_date_str)
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return "날짜 형식 오류"


# description을 깔끔하게 글자만 추출하는 함수
def clean_description(raw_html):
    soup = BeautifulSoup(raw_html, "html.parser")
    text = soup.get_text(strip=True)
    trimmed_text = text.split("전체 내용보기")[0].strip()
    return trimmed_text


# 뉴스 내용 크롤링
def crawl_article(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    content_tag = soup.find_all("p", class_="content_text text-l")
    if not content_tag:
        return "본문 없음"  # ← 예외 처리 추가

    content_text = "\n\n".join([tag.text.strip() for tag in content_tag])
    return content_text


# 메인 함수
def main():
    print("경향신문 RSS 피드를 확인하는 중 ...")
    feed = feedparser.parse(RSS_FEED_URL1)

    for entry in feed.entries:
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
            "category": category,
            "content": content,
            "url": url,
        }
        save_to_db(data)

    print("오 마이 뉴스 RSS 피드를 확인하는 중 ...")
    feed = feedparser.parse(RSS_FEED_URL2)

    for entry in feed.entries:
        title = entry.get("title", "제목없음")
        writer = entry.get("author", "작성자 없음")
        write_date = format_date(entry.get("published", "날짜 없음"))
        category = entry.get("category", "카테고리 없음")
        content = clean_description(entry.get("description", ""))
        url = entry.link

        # DB에 저장
        data = {
            "title": title,
            "writer": writer,
            "write_date": write_date if write_date != "날짜 형식 오류" else None,
            "category": category,
            "content": content,
            "url": url,
        }
        save_to_db(data)

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
