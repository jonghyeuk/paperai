import streamlit as st
import openai
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import tempfile
from fpdf import FPDF

# GPT API 설정
openai.api_key = st.secrets["OPENAI_API_KEY"]

# DB 로딩
@st.cache_data
def load_data():
    df = pd.read_excel("ISEF Final DB.xlsx")
    return df.dropna(subset=["Project Title"])

df = load_data()

# 앱 시작
st.title("🧪 AI 기반 소논문 설계 가이드")
st.markdown("""
이 앱은 관심 키워드를 입력하면 관련된 실험 주제를 추천하고, 실제 과학 경진대회 데이터를 기반으로 분석과 실험 설계를 도와드립니다.

:warning: **주의**: 이 문서는 실제 논문 제목과 초록에 기반한 GPT의 **추론 결과**입니다. 정식 인용 자료로 사용할 수 없습니다.
""")

# 새 탐색 초기화 기능
if st.button("🔄 새 탐색 시작하기"):
    st.experimental_rerun()

# 사용자 입력
keyword = st.text_input("🔍 관심 있는 키워드를 입력하세요 (예: enzyme, temperature, plant)")

if keyword:
    # GPT 주제 추천
    with st.spinner("GPT가 주제를 생성 중입니다..."):
        prompt = f"""
        '{keyword}'라는 관심사를 가진 중고등학생에게 적합한 과학 소논문 주제 5개를 추천해줘.
        각 주제는 실험이 가능해야 하며, 1줄씩 써줘.
        """
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "당신은 창의적인 과학 주제를 추천하는 AI입니다."},
                {"role": "user", "content": prompt}
            ]
        )
        gpt_topics = response['choices'][0]['message']['content'].split("\n")

    st.subheader("📌 GPT 추천 주제")
    selected_gpt = st.radio("GPT 추천 중 선택하거나 아래 DB 기반 주제를 참고하세요:", gpt_topics)

    # 유사 논문 검색
    with st.spinner("DB에서 유사 논문을 찾는 중입니다..."):
        vectorizer = TfidfVectorizer()
        tfidf = vectorizer.fit_transform(df["Project Title"].values.astype("U"))
        user_vec = vectorizer.transform([keyword])
        similarities = cosine_similarity(user_vec, tfidf).flatten()
        top_indices = similarities.argsort()[::-1][:3]
        top_projects = df.iloc[top_indices][["Year", "Project Title", "Awards Won"]].copy()
        top_projects.reset_index(drop=True, inplace=True)

    st.subheader("📚 유사 논문 (실제 제출된 과학 경진대회 결과)")
    for i, row in top_projects.iterrows():
        st.markdown(f"**{i+1}. {row['Project Title']}** ({row['Year']}) – 수상: {row.get('Awards Won', '정보 없음')}")

    selected_db_index = st.radio("유사 논문 중 선택하려면 번호를 선택하세요:", options=["None"] + [str(i+1) for i in range(3)])

    # 선택된 주제 확정
    if st.button("이 주제로 실험 설계 생성하기"):
        chosen_topic = selected_gpt if selected_db_index == "None" else top_projects.iloc[int(selected_db_index)-1]['Project Title']

        with st.spinner("GPT가 실험 설계를 생성 중입니다..."):
            analysis_prompt = f"""
            아래 주제를 바탕으로 다음 내용을 포함한 실험 설계 문서를 작성해줘:
            - 서론 (왜 이 주제를 다루는지 배경)
            - 실험 목적
            - 가설
            - 방법 (단계별)
            - 변수 설정
            - 결과 예측
            - 오차 요인
            - 결론
            - 확장 가능성 (틈새 전략 제안 포함)
            - 마지막에 이건 GPT 추론이며 참고용임을 명시

            주제: {chosen_topic}
            """
            guide = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "당신은 과학 연구 설계 전문가입니다."},
                    {"role": "user", "content": analysis_prompt}
                ]
            )
            full_text = guide['choices'][0]['message']['content']
            st.success("✅ 실험 설계 문서 생성 완료!")
            st.text_area("✍️ 결과 (복사해서 사용 가능)", full_text, height=500)

            # PDF 저장 기능
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.set_font("Arial", size=12)
            for line in full_text.split('\n'):
                pdf.multi_cell(0, 10, line)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
                pdf.output(tmpfile.name)
                st.download_button(
                    label="📄 PDF로 다운로드",
                    data=open(tmpfile.name, "rb").read(),
                    file_name="science_experiment_guide.pdf",
                    mime="application/pdf"
                )

        st.markdown("""
        :warning: 이 내용은 실제 논문의 제목 또는 관심 키워드를 바탕으로 한 GPT의 **추론 결과**입니다. 정식 인용 자료로 사용하지 마세요.
        """)
