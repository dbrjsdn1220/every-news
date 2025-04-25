# 📰 News RSS Crawler & PostgreSQL Saver

경향신문의 RSS 픽을 통해 최신 뉴스를 수집하고,  기사 제목·작성자·작성일·카테고리·부문 등을 PostgreSQL DB에 저장하는 Python 기반 크롤러입니다.

</br>

## 주요 기능

- `feedparser`: RSS 픽에서 뉴스 항목 추출
- `requests` + `BeautifulSoup`: 각 뉴스 페이지의 부문 크롤링
- `datetime`: 공개일 포맷 정리 (`ISO 8601 → YYYY-MM-DD HH:MM`)
- `psycopg2`: PostgreSQL DB에 데이터 저장
- `.env`: DB 정보 보안 관리

</br>

## 수집 데이터 항목

| 필드명       | 설명                                  |
|--------------|---------------------------------------|
| `title`      | 뉴스 제목                             |
| `writer`     | 기자 이름 (이메일 제거)                |
| `write_date` | 기사 작성 시간 (datetime 변환됨)       |
| `category`   | 뉴스 카테고리                          |
| `content`    | 기사 부문 (`<p>` 태그 기반)            |
| `url`        | 기사 고유 링크 (중복 방지 키로 활용)   |

 
</br>

## 실행 환경

### 1. 의존 패키지 설치
```bash
pip install feedparser requests beautifulsoup4 psycopg2-binary python-dotenv
```

### 2. PostgreSQL 테이블 생성

```sql
CREATE TABLE news_article (
    id SERIAL PRIMARY KEY,
    title TEXT,
    writer TEXT,
    write_date TIMESTAMP,
    category TEXT,
    content TEXT,
    url TEXT UNIQUE
);
```

> 시퀀스 에러 방지를 위해 시퀀스 권한도 부여해야 합니다:

```sql
GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA public TO your_user;
```

---

### 3. .env 설정 예시

```env
conn = psycopg2.connect(
    host = "localhost",
    dbname = 'news',
    user = os.getenv("DB_USERNAME"),
    password = os.getenv("DB_PASSWORD")
)
```

### 4. 주요 항목들 추출 방법 (중에 문제 있었던 것만)
- date
> dc:date -> date 로 수정   
2025-04-11T09:16:00+09:00 을 2025-04-11 09:16 과 같은 가공된 형태로 변경 (datetime) 라이브러리 사용


- writer
> "홍길동 기자 abcd123@kyunghyang.com" 에서 이름만 추출하고자 split("기자")[0].strip() 를 사용해 전처리 진행

- content
> 본문 내용은 feedparser 로 가져올 수가 없어서 BeautifulSoup을 활용해서 크롤링을 따로 해줌


</br>

## 중요 오류 정리

### ✅ 본문 내용을 적재하는 과정에서 for문으로 None을 돌리는 문제 발생
-  `soup.find()`는 태그를 못 찾으면 `None` 반환
- `None`에 `for` 문 도림 → `TypeError`
- 해결: `find_all()` 사용 + `if not content_tag`로 예외 처리해줌


### ✅ PostgreSQL 관련 권한 문제들
- `INSERT` 권한 불쇄 → `GRANT INSERT ON table TO user;`
- `SERIAL` 사용 시 → `GRANT USAGE, SELECT, UPDATE ON SEQUENCE ... TO user;`
- `write_date NOT NULL` 오류 → 날짜 포맷 변환 실패 시 `None` 방지 필요



Token Authentication 사용 안하면 CSRF 토큰이 필요함. CSRF는 교차 사이트 요청 위조라고 서버가 클라이언트에게 고유한 키를 줘서 <br>
위조된 사용자가 아닌지 확인하는 과정.