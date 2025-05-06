import streamlit as st
st.set_page_config(page_title="소논문 AI", layout="wide")
from openai import OpenAI
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fpdf import FPDF
import tempfile
from deep_translator import GoogleTranslator

# OpenAI 클라이언트 설정
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# DB 불러오기
@st.cache_data
def load_data():
    df = pd.read_excel("ISEF Final DB.xlsx")
    return df.dropna(subset=["Project Title"])

# 데이터 로딩
df = load_data()

# 페이지 설정

# 레이아웃 구성
left, right = st.columns([2, 1])

with left:
    st.title("🧠 AI 기반 소논문 설계 가이드")
    keyword = st.text_input("🔍 관심 키워드를 입력하세요 (예: enzyme, temperature, bacteria)")

    if keyword:
        with st.spinner("GPT가 주제를 생성 중입니다..."):
            prompt = f"""
            '{keyword}'를 주제로 할 수 있는 중·고등학생용 과학 소논문 실험 주제를 5개 추천해줘. 한 줄 제목 형식으로.
            """
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            gpt_topics = [t.strip("- ") for t in response.choices[0].message.content.strip().split("\n") if t.strip()]

        st.subheader("📌 GPT 추천 주제")
        selected_gpt = st.radio("아래 추천 주제 중 선택하거나, DB 기반 주제를 아래에서 확인하세요:", gpt_topics)

        # 유사 논문 검색
        vectorizer = TfidfVectorizer()
        tfidf = vectorizer.fit_transform(df["Project Title"].astype(str))
        user_vec = vectorizer.transform([keyword])
        similarities = cosine_similarity(user_vec, tfidf).flatten()
        top_indices = similarities.argsort()[::-1][:3]
        top_projects = df.iloc[top_indices][["Year", "Project Title", "Awards Won"]].copy().reset_index(drop=True)

        st.subheader("📚 유사 논문 (실제 대회 제출)")
        options = [f"{i+1}. {GoogleTranslator(source='en', target='ko').translate(row['Project Title'])} ({row['Year']}) - 수상: {row.get('Awards Won', '없음')}" for i, row in top_projects.iterrows()]
        selected_db = st.radio("유사 논문 중 선택할 것이 있다면 고르세요:", options=["None"] + options)

        if st.button("이 주제로 실험 설계 생성"):
            chosen_topic = selected_gpt if selected_db == "None" else top_projects.iloc[int(selected_db[0])-1]['Project Title']
            analysis_prompt = f"""
            아래 주제를 바탕으로 실험 설계 문서를 작성해줘:
            - 서론 (배경과 필요성)
            - 실험 목적, 가설, 방법, 변수 설정, 예상 결과, 오차 요인
            - 결론 및 확장 가능성 (틈새 제안 포함)
            - 마지막에 '이 내용은 GPT 추론 기반의 예시입니다' 명시
            주제: {chosen_topic}
            """
            analysis = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": analysis_prompt}]
            ).choices[0].message.content

            st.success("✅ 실험 설계 생성 완료")
            st.text_area("📄 결과 요약", analysis, height=400)

            # PDF 저장
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            for line in analysis.split("\n"):
                pdf.multi_cell(0, 10, line)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
                pdf.output(tmpfile.name)
                st.download_button("📥 PDF로 저장", data=open(tmpfile.name, "rb").read(), file_name="experiment_guide.pdf", mime="application/pdf")

with right:
    st.markdown("""
    ### 🧭 진행 흐름 안내
    1️⃣ 관심 키워드 입력 → GPT 주제 추천 + DB 검색<br>
    2️⃣ 주제 선택 → GPT 기반 실험 설계 생성<br>
    3️⃣ 실험 목적/가설/방법 등 자동 구성<br>
    4️⃣ PDF로 저장하거나 다시 탐색 가능<br>

    💬 **실제 보고서가 아닌, 참고용 분석 예시입니다**
    """)
