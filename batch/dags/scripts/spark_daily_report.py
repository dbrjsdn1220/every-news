import os
import shutil
from datetime import datetime, timedelta

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, to_timestamp
from pyspark.sql.types import ArrayType, StringType
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.font_manager as fm


def main():
    # 1. 실행 시 기준 전날 날짜 계산
    report_date = datetime.today() - timedelta(days=1)
    report_date_str = report_date.strftime("%Y-%m-%d")
    print(f"[INFO] 리포트 기준 날짜: {report_date_str}")

    # 2. 날짜 범위 계산
    start_ts = report_date
    end_ts = report_date + timedelta(days=1)

    # 3. 경로 설정
    FONT_PATH = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"
    REALTIME_DIR = "/opt/airflow/data"
    ARCHIVE_DIR = "/opt/airflow/data/news_archive"
    REPORT_DIR = "/opt/airflow/data"

    INPUT_PATH = os.path.join(REALTIME_DIR, "*.json")
    REPORT_PATH = os.path.join(REPORT_DIR, f"daily_report_{report_date.strftime('%Y%m%d')}.pdf")
    ARCHIVE_TARGET = os.path.join(ARCHIVE_DIR)

    # 4. 한글 폰트 설정git 
    font_prop = fm.FontProperties(fname=FONT_PATH, size=12)

    # 5. Spark 세션 시작
    spark = SparkSession.builder.appName("DailyNewsReport").getOrCreate()

    try:
        # 6. JSON 데이터 로드
        df = spark.read.option("multiline", "true").json(INPUT_PATH)
        print(f"[INFO] 전체 로드된 기사 수: {df.count()}")

        # 7. 날짜 필터링
        df = df.withColumn("timestamp", to_timestamp("write_date"))
        df_filtered = df.filter((col("timestamp") >= start_ts) & (col("timestamp") < end_ts))
        print(f"[INFO] 분석 대상 기사 수: {df_filtered.count()}")

        # 8. 키워드 집계
        df_keywords = df_filtered.withColumn("keyword", explode(col("keywords").cast(ArrayType(StringType()))))
        keyword_counts = df_keywords.groupBy("keyword").count().orderBy(col("count").desc())
        top_keywords = keyword_counts.limit(10).toPandas()

        # 9. PDF 리포트 생성
        if not top_keywords.empty:
            with PdfPages(REPORT_PATH) as pdf:
                plt.figure(figsize=(10, 6))
                plt.bar(top_keywords['keyword'], top_keywords['count'], color='skyblue')
                plt.title(f"{report_date_str} 키워드 TOP 10", fontproperties=font_prop)
                plt.xlabel("키워드", fontproperties=font_prop)
                plt.ylabel("기사 수", fontproperties=font_prop)
                plt.xticks(rotation=45, fontproperties=font_prop)
                plt.tight_layout()
                pdf.savefig()
                plt.close()
            print(f"[INFO] 리포트 저장 완료: {REPORT_PATH}")
        else:
            print("[WARN] 키워드 데이터가 없습니다. 리포트 생성 생략.")

        # 10. JSON 아카이빙
        os.makedirs(ARCHIVE_TARGET, exist_ok=True)
        for file in os.listdir(REALTIME_DIR):
            if file.endswith(".json"):
                src_path = os.path.join(REALTIME_DIR, file)
                dst_path = os.path.join(ARCHIVE_TARGET, file)
                shutil.move(src_path, dst_path)
        print(f"[INFO] JSON 파일 {ARCHIVE_TARGET}로 이동 완료.")

    except Exception as e:
        print(f"[ERROR] 처리 중 오류 발생: {e}")
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
