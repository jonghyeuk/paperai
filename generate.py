from openai import OpenAI
import streamlit as st

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# GPT에게 주제를 추천받는 함수
def generate_suggestions(keyword, niche=False):
    prompt = f"""
    중고등학생이 '{keyword}'와 관련된 주제로 진행할 수 있는 과학 소논문 실험 주제를 {"3개" if niche else "5개"} 추천해줘.
    각각은 실제 실험이 가능해야 하고, 한 줄짜리 제목 형식으로 제시해줘.
    {"다른 학생들이 잘 하지 않는 참신하고 틈새 아이디어 중심으로 추천해줘." if niche else ""}
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return [line.strip("-• ") for line in response.choices[0].message.content.strip().split("\n") if line.strip()]


# GPT로부터 보고서 구조 생성받는 함수
def generate_report(topic):
    prompt = f"""
    '{topic}'이라는 주제로 실험 보고서를 작성해줘. 아래 형식을 따라줘:
    
    1. 개요 (왜 이 주제를 선택했는가)
    2. 실험 목적
    3. 가설
    4. 실험 방법 (단계별로)
    5. 측정 변수 및 도구
    6. 예상 결과
    7. 오차 요인 및 보완 방안
    8. 결론
    9. 확장 가능성 또는 다른 방향 실험 제안

    말투는 친절하고 이해하기 쉽게 써줘. 각 항목에 대해 충분한 분량으로 써줘.
    마지막에 '이 내용은 GPT 추론 기반 참고 자료입니다.'라고 명시해줘.
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()
