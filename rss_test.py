import feedparser
import requests
from bs4 import BeautifulSoup

# RSS 피드 URL (예: Khan 뉴스 RSS)
RSS_FEED_URL = "https://www.khan.co.kr/rss/rssdata/total_news.xml"


def main():
    feed = feedparser.parse(RSS_FEED_URL)
    print(feed)


if __name__ == "__main__":
    main()
