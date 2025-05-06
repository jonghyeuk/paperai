import streamlit as st
import pandas as pd
from openai import OpenAI
from fpdf import FPDF
from difflib import SequenceMatcher

# --- 페이지 설정 ---
st.set_page_config(page_title="AI 기반 소논문 설계 가이드", layout="wide")

# --- API 키 ---
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- 데이터 불러오기 ---
@st.cache_data
def load_data():
    df = pd.read_excel("ISEF Final DB.xlsx")
    return df

df = load_data()

# --- 유사도 계산 ---
def find_similar_topics(input_keyword, db, top_n=3):
    def similarity(a, b):
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()
db["similarity"] = db["Project Title"].apply(lambda x: similarity(input_keyword, x))
    return db.sort_values(by="similarity", ascending=False).head(top_n)

# --- GPT 프롬프트 ---
def generate_topic_overview(keyword):
    prompt = f"""
    사용자가 제시한 관심 주제: {keyword}
    1. 이 주제의 주요 과학적 의미와 배경을 알려줘.
    2. 현재 이와 관련한 사회/환경적 이슈를 설명해줘.
    3. 이 주제에 대해 고등학생이 탐구 가능한 소논문 연구 주제 5개를 추천해줘.
    형식: 
    - 주제 제목
    - 연구 목적 (한 줄)
    - 예상 실험 방법 요약 (한 줄)
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# --- PDF 저장 ---
def save_as_pdf(title, content):
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("Nanum", '', fname="NanumGothic-Regular.ttf", uni=True)
    pdf.set_font("Nanum", size=12)
    for line in content.split("\n"):
        pdf.multi_cell(0, 8, txt=line)
    pdf_file = f"{title}.pdf"
    pdf.output(pdf_file)
    return pdf_file

# --- UI 흐름 ---
st.title("🔬 AI 기반 소논문 설계 가이드")
st.markdown("💬 **실제 보고서가 아닌, 참고용 분석 예시입니다**")

if "step" not in st.session_state:
    st.session_state.step = 1

if st.session_state.step == 1:
    keyword = st.text_input("🧠 탐구하고 싶은 주제를 입력하세요 (예: 온도와 효소 반응, 꿀벌 개체 수 감소 등)")
    if keyword:
        st.session_state.keyword = keyword
        st.session_state.step = 2
        st.rerun()

elif st.session_state.step == 2:
    st.subheader("🔍 주제 개요 및 이슈 분석")
    with st.spinner("AI가 주제를 분석하고 있습니다..."):
        overview = generate_topic_overview(st.session_state.keyword)
        st.session_state.overview = overview
        similar = find_similar_topics(st.session_state.keyword, df)
        st.session_state.similar = similar
    st.markdown(overview)
    st.subheader("📁 유사한 실제 과학 경진대회 주제")
    if similar["similarity"].iloc[0] < 0.4:
        st.warning("📌 유사한 실제 DB 주제를 찾을 수 없었습니다.")
    else:
        for idx, row in similar.iterrows():
            st.markdown(f"- {row['title']} ({row['year']}년 출품)")
    if st.button("➡️ 주제 선택하고 심층 분석 진행"):
        st.session_state.step = 3
        st.rerun()

elif st.session_state.step == 3:
    st.subheader("📄 주제 심층 분석 결과")
    st.markdown("(예시 분석 내용 표시. GPT 호출 결과 기반)\n\n- 연구 배경\n- 실험 목적\n- 실험 방법(3단계 요약)\n- 변수 설정\n- 예상 결과\n- 오차 요인\n- 결론 및 확장 가능성")
    st.markdown("✳️ GPT 추론 결과이므로 실제 보고서로 사용 시 보완이 필요합니다.")
    if st.button("📄 PDF 저장"):
        file_path = save_as_pdf(st.session_state.keyword, st.session_state.overview)
        with open(file_path, "rb") as f:
            st.download_button("📥 PDF 다운로드", f, file_name=file_path)
    if st.button("✨ 틈새 주제 제안 받아보기"):
        st.session_state.step = 4
        st.rerun()

elif st.session_state.step == 4:
    st.subheader("🧠 틈새 주제 제안 및 실험 가이드")
    st.markdown("(GPT가 유사 주제 분석 후 틈새 주제 2~3개 추천 + 실험 가이드 제시)")
    st.info("곧 실험 설계 추천 예시로 이어집니다. 🧪")
    if st.button("🔄 새 탐색 시작하기"):
        st.session_state.step = 1
        st.rerun()
