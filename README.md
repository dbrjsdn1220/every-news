# 📰 RSS News Pipeline

경향신문의 RSS 피드를 기반으로 최신 뉴스를 수집하고, 기사 정보를 PostgreSQL에 저장하는 데이터 파이프라인 프로젝트다.  
Django 기반의 REST API로 데이터를 외부에 제공하고 React 프론트엔드도 포함되어 있다

---

## 🗃 수집 데이터 항목

| 필드명       | 설명                              |
|--------------|-----------------------------------|
| `title`      | 뉴스 제목                         |
| `writer`     | 기자 이름 (이메일 제거)           |
| `write_date` | 기사 작성 시간 (datetime 변환됨) |
| `category`   | 뉴스 카테고리                     |
| `content`    | 기사 본문 (`<p>` 태그 기반)       |
| `url`        | 기사 고유 링크 (중복 방지 키)     |

---

## 📁 프로젝트 구조

```
rss-news-pipeline/
├── batch/
├── data/
├── django_project/
├── front-pjt/
├── test/
├── news_consumer.py
├── news_crawling.py
├── news_producer.py
├── openapi.py
├── requirements.txt
├── requirements_django.txt
└── .gitignore
```

- `batch/`: 배치 작업 관련 스크립트
- `data/`: 수집된 데이터 저장 디렉토리
- `django_project/`: Django 백엔드 프로젝트
- `front-pjt/`: React 프론트엔드 프로젝트
- `test/`: 테스트 코드 및 자료
- `news_consumer.py`: Kafka 등 메시지 큐에서 데이터 소비
- `news_crawling.py`: RSS 및 뉴스 페이지 크롤링
- `news_producer.py`: 크롤링된 데이터 메시지 큐 전송
- `openapi.py`: OpenAPI 스펙 정의

---

## 🚀 실행 방법

1. 패키지 설치

```bash
pip install -r requirements.txt
pip install -r requirements_django.txt
```

2. `.env` 파일 생성 및 설정

```env
DB_USERNAME=<POSTGRE_SQL_USERNAME>
DB_PASSWORD=<POSTGRE_SQL_PASSWORD>
OPENAI_API_KEY=<YOUR_OPENAI_API_KEY>
KAFKA_CONNECTOR_PATH=/path/to/flink-sql-connector-kafka-3.3.0-1.20.jar
```

3. Kafka Broker 실행

```bash
cd /usr/local/kafka
bin/zookeeper-server-start.sh config/zookeeper.properties
bin/kafka-server-start.sh config/server.properties
```

4. 크롤링 스크립트 실행

```bash
python news_consumer.py
python news_producer.py
```

5. Django 서버 실행

```bash
cd django_project
python manage.py runserver
```

6. React 프론트엔드 실행

```bash
cd front-pjt
npm install
npm start
```

---

## 📌 참고 사항

- 기본 데이터베이스는 PostgreSQL이며, 다른 DBMS 사용 시 적절한 드라이버로 교체 필요
- 배포 시 환경 변수 및 보안 설정 반드시 확인할 것
