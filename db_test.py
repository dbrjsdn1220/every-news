import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host = "localhost",
    dbname = "news",
    user = os.getenv("DB_USERNAME"),
    password = os.getenv("DB_PASSWORD")
)

cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM news_article")
count = cur.fetchall()

print(count)

cur.close()
conn.close()