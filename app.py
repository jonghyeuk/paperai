# paperai/app.py

import streamlit as st
import pandas as pd
import openai
import os
from utils import generate_research_topics, load_db, search_similar_topics, generate_report, suggest_niche_topics, generate_experiment_plan, save_pdf

# → secrets.toml 또는 Streamlit Cloud 변수
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Set config MUST be at the top
st.set_page_config(page_title="AI 소논문 조사 가이드", layout="wide")

# Load DB
DB_PATH = "ISEF Final DB.xlsx"
df_db = load_db(DB_PATH)

# 프로워 가이드
st.title("🧪 AI 기반 소논문 조사 가이드")
st.markdown("""
→ 의미 가\uub2a5성이 많은 관심 향성을 입력해주세요.
""")

# 1. 관심사 포함 입력
prompt = st.text_input("**현재 관심이 가능성 있는 주제를 입력해주세요**", placeholder="예: 온도에 따른 협소 반응")

if prompt:
    with st.spinner("검색 중..."):
        overview, background, topic_list = generate_research_topics(prompt)
        st.subheader("현재 관심사 개요")
        st.markdown(overview)
        st.subheader("역론 경험/방향 설명")
        st.markdown(background)

        # DB 연관 논문 검색
        st.subheader("유사 논문 분석")
        similar = search_similar_topics(prompt, df_db)
        if similar:
            for row in similar:
                st.info(f"**{row['title_kr']}** ({row['year']}년 출판)\n\n— {row['abstract_kr']}")
        else:
            st.warning(":x: 관련 논문이 DB에서 검색되지 않았습니다.")

        st.subheader("AI 추천 주제")
        selected = st.radio("선택할 주제를 고르세요", topic_list)

        if st.button("주제 확정"):
            report = generate_report(selected)
            st.markdown(report, unsafe_allow_html=True)

            # 특혜 가능성 주제
            niche = suggest_niche_topics(selected)
            st.subheader(":mag_right: 넓은 가능성 주제")
            st.markdown(niche)

            if st.button("주제 선택과 시험 설계"):
                guide = generate_experiment_plan(selected)
                st.subheader(":triangular_ruler: 시험 가이드")
                st.markdown(guide)

                # PDF 저장 버튼
                if st.button("PDF 저장"):
                    file_path = save_pdf(selected, report, guide)
                    with open(file_path, "rb") as f:
                        st.download_button(label="파일 다운로드", data=f, file_name="소논문_조사.pdf")

            st.button("새 탐색 시작", on_click=lambda: st.session_state.clear())
