# app.py
import streamlit as st
from generate import generate_suggestions, generate_report
from db_search import search_similar_papers
from utils import create_pdf, reset_state

# 페이지 설정 (UTF-8에서 제일 앞에 오고 st.set_page_config 가운데 가졌어야함)
st.set_page_config(page_title="AI 소노문 진료 가이드", layout="wide")

st.title("🧪 AI 기반 소노문 진료 가이드")
st.markdown("""
이 앱은 관심 키워드를 입력하면 관련된 실험 주제를 추천하고, 실제 과학 경진대회 데이터를 기반으로 분석과 실험 설계를 도와드립니다.  
🔍 **GPT 추론 기반** + **실제 제출 논문 DB 기반 유사 사례 제안** + **틈새 주제 가이드** 포함.
""")

# 1. 관심 키워드 입력 단계
with st.form(key="keyword_form"):
    user_input = st.text_input("**1단계. 관심 있는 키워드를 입력하세요** (예: 효소, 온도, pH)")
    submitted = st.form_submit_button("투배 시작")

# 초기화 버튼
st.sidebar.button("🔄 새 탐색 시작하기", on_click=reset_state)

if submitted and user_input:
    # GPT 기반 추천 주제 생성
    suggestions = generate_suggestions(user_input)

    st.subheader("🧠 AI 추천 실험 주제")
    for i, s in enumerate(suggestions, 1):
        st.markdown(f"**{i}. {s}**")

    # 유사 논문 탐색 (내부 DB)
    similar = search_similar_papers(user_input)

    st.subheader("📂 유사 주제 논문 (출품 데이터 기반)")
    if similar:
        for item in similar:
            st.markdown(f"- **{item['title_ko']}**  \
                        (출품 연도: {item['year']})\n> {item['abstract_ko'][:150]}...")
    else:
        st.info("유사한 논문이 DB에 없습니다. GPT가 생성한 주제를 참고해주세요.")

    # 주제 선택
    st.markdown("---")
    all_choices = suggestions + [x['title_ko'] for x in similar]
    selected = st.selectbox("선택할 주제를 골라주세요:", options=all_choices)

    if st.button("📄 실험 보고서 생성하기"):
        # 보고서 생성
        report = generate_report(selected)
        st.success("완성된 보고서를 아래에서 확인하세요!")
        st.markdown(report, unsafe_allow_html=True)

        # PDF 저장
        if st.button("📥 PDF로 저장"):
            create_pdf(report)

        # 틈새 제안도 함께
        st.markdown("""
        ---
        🤖 **팁: 선택한 주제 외에도 이런 실험 주제는 어떠신가요?** (GPT가 틈새 가능성 중심으로 추천)
        """)
        alt = generate_suggestions(user_input, niche=True)
        for i, idea in enumerate(alt, 1):
            st.markdown(f"- {idea}")

    st.markdown("💬 **실제 보고서가 아닌, 참고용 분석 예시입니다**")
    """)
