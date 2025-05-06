import streamlit as st
from fpdf import FPDF
import tempfile

# PDF 생성 함수 (한글은 대체 문자로 출력)
def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

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

# 상태 초기화 함수 (재탐색용)
def reset_state():
    for key in st.session_state.keys():
        del st.session_state[key]
