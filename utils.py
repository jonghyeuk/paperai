import streamlit as st
from fpdf import FPDF
import tempfile
import os

# PDF 생성 함수 (한글도 제대로 출력되도록 수정)
def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()

    # 한글 폰트 등록 (같은 폴더에 있어야 함)
    font_path = os.path.join(os.path.dirname(__file__), "NanumGothic-Regular.ttf")
    pdf.add_font("Nanum", "", font_path, uni=True)
    pdf.set_font("Nanum", size=12)

    for line in text.split("\n"):
        try:
            pdf.multi_cell(0, 10, line)
        except:
            pdf.multi_cell(0, 10, "[출력 오류: 한글 또는 특수문자 포함]")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
        pdf.output(tmpfile.name)
        with open(tmpfile.name, "rb") as f:
            st.download_button(
                label="📄 PDF 다운로드",
                data=f.read(),
                file_name="소논문_설계_가이드.pdf",
                mime="application/pdf"
            )

# 상태 초기화 함수
def reset_state():
    for key in st.session_state.keys():
        del st.session_state[key]
