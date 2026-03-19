import streamlit as st

def render():
    st.subheader("📜 계약 학교 관리")
    
    st.success("현재 총 120개교가 서비스 이용 중입니다.")
    
    # 계약 기간 관리 중심의 테이블
    st.write("계약 만료 현황 (최근순)")
    st.info("계약 갱신 상담이 필요한 학교를 확인하세요.")