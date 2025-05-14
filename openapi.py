from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


def preprocess_content(content):
    """
    데이터 전처리 - 텍스트 길이 제한  (5000 토큰)
    토큰 수를 제한하여 처리 효율성 확보
    """
    import tiktoken

    if not content:
        return ""

    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(content)

    if len(tokens) > 5000:
        truncated_tokens = tokens[:5000]
        return encoding.decode(truncated_tokens)

    return content


def transform_extract_keywords(text):
    """
    텍스트 데이터 변환 - 키워드 5개 추출
    입력 텍스트에서 핵심 키워드를 추출하는 변환 로직
    """
    text = preprocess_content(text)

    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "아래의 뉴스 본문에서 주요 키워드를 5개 추출해 주세요. 키워드는 콤마(,)로 구분된 한 줄 문자열로만 답변하세요. (예: 경제, 시장, 금리, 주식, 소비자)",
            },  # 해당 위치에서 키워드 5개를 추출할 수 있도록 프롬프트 작성성
            {"role": "user", "content": text},
        ],
        max_tokens=100,
    )
    keywords = response.choices[0].message.content.strip()
    return keywords.split(",")


def transform_to_embedding(text: str) -> list[float]:
    """
    텍스트 데이터 변환 - 벡터 임베딩
    텍스트를 수치형 벡터로 변환하는 변환 로직
    """
    text = preprocess_content(text)

    client = OpenAI()
    response = client.embeddings.create(input=text, model="text-embedding-3-small")
    # print(response.data[0].embedding)
    return response.data[0].embedding


def transform_classify_category(content):
    """
    TODO: 해당 로직을 위의 코드와 아래의 category를 참고하여 openai 기반의 카테고리 분류가 가능한 형태로 구현하세요.

    텍스트 데이터 변환 - 카테고리 분류
    뉴스 내용을 기반으로 적절한 카테고리로 분류하는 변환 로직
    """
    content = preprocess_content(content)

    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """다음 뉴스 본문을 읽고 가장 적절한 카테고리를 하나 선택하세요.
카테고리 목록: IT_과학, 건강, 경제, 교육, 국제, 라이프스타일, 문화, 사건사고, 사회일반, 산업, 스포츠, 여성복지, 여행레저, 연예, 정치, 지역, 취미.
카테고리 이름만 답변하세요.""",
            },
            {"role": "user", "content": content},
        ],
        max_tokens=20,
    )
    model_output = response.choices[0].message.content.strip()

    allowed_categories = [
        "IT_과학",
        "건강",
        "경제",
        "교육",
        "국제",
        "라이프스타일",
        "문화",
        "사건사고",
        "사회일반",
        "산업",
        "스포츠",
        "여성복지",
        "여행레저",
        "연예",
        "정치",
        "지역",
        "취미",
    ]
    if model_output not in allowed_categories:
        model_output = "미분류"

    # print(model_output)
    return model_output
