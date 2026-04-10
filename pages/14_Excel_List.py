import streamlit as st
from src.style_utils import apply_purple_theme, render_stat_card

# 1. 페이지 설정
st.set_page_config(page_title="독서화랑 팀 통합 엑셀", layout="wide")
apply_purple_theme()

def render_excel_link(title, url, description):
    """시트 링크 전용 카드 디자인"""
    st.markdown(f"""
        <div style="
            background: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 18px;
            margin-bottom: 12px;
            border: 1px solid rgba(118, 75, 162, 0.1);
            box-shadow: 0 4px 12px rgba(0,0,0,0.03);
            display: flex;
            justify-content: space-between;
            align-items: center;
        ">
            <div style="flex: 1;">
                <h4 style="margin: 0; color: #4b2c71; font-size: 15px; font-weight: 700;">📄 {title}</h4>
                <p style="margin: 4px 0 0 0; color: #64748b; font-size: 12px;">{description}</p>
            </div>
            <a href="{url}" target="_blank" style="
                text-decoration: none;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 7px 16px;
                border-radius: 8px;
                font-size: 12px;
                font-weight: 600;
                white-space: nowrap;
                margin-left: 15px;
            ">시트 열기</a>
        </div>
    """, unsafe_allow_html=True)

def display_excel_list():
    st.markdown("### 🗂️ 팀 통합 엑셀 리스트 관리")
    st.info("💡 업무에 필요한 모든 구글 시트를 카테고리별로 확인할 수 있습니다.")

    # 탭을 활용하여 복잡한 리스트 분리
    tab1, tab2, tab3 = st.tabs(["🏛️ 내부 운영/회의", "🏫 B2G 관리", "🏠 B2C/재원생"])

    # --- 카테고리 1: 내부 운영 및 회의 ---
    with tab1:
        st.write("")
        col1, col2 = st.columns(2)
        with col1:
            render_excel_link("내부 오류 요청 리스트", "https://docs.google.com/spreadsheets/d/1rkynolHXlzVDqwJMG3iNmd3Dze3KnzZHStcNCT2_sTI/", "시스템 및 서비스 내부 오류 리포트")
            render_excel_link("정기 회의록", "https://docs.google.com/spreadsheets/d/1r3QI_pHDA9eKyQTiUXnNl5rveAV0bkhDvbm1P-Thbm4/", "팀 주간/정기 회의 기록")
        with col2:
            render_excel_link("2026 마케팅본부 주간업무", "https://docs.google.com/spreadsheets/d/1cbbdK1jZlay460Q5DFnzncPCtIR-q3zN1_IjiPJf4Qc/", "마케팅 본부 전체 주간 현황")
            render_excel_link("연구도서 지원 관리", "https://docs.google.com/spreadsheets/d/1fRD_NAG8ucp0lUA8dPHk8GljYMNgpZ6V_Fuhm6s0kwk/", "연구 목적 도서 지원 히스토리")

    # --- 카테고리 2: B2G 관리 ---
    with tab2:
        st.write("")
        c1, c2 = st.columns(2)
        with c1:
            render_excel_link("교육청 공고 관리", "https://docs.google.com/spreadsheets/d/118azg5IUjsGcfnguKK9Bc2dDUUXvt_AFpFHRNU4dL9w/", "지역별 교육청 공고 모니터링")
            render_excel_link("26년 AI 선도학교", "https://docs.google.com/spreadsheets/d/1ktjLxG5IJuu1QiQXQpC2Tynd-3J65KwK/", "26년 타겟 선도학교 명단")
            render_excel_link("총판 관리 시트", "https://docs.google.com/spreadsheets/d/1LoiiCRBT9XjAPhT-38RlVk3k8hJaz52Zc4TivtawhgQ/", "파트너사 및 총판별 계약 현황")
            render_excel_link("학교 관리 시트", "https://docs.google.com/spreadsheets/d/1nmAhwBLloq6pFGFIWYahKh4vPQaw08xugCWHURJ076c/", "B2G 전체 학교 통합 관리")
            render_excel_link("도입문의 설문 데이터", "https://docs.google.com/spreadsheets/d/1nrQe-mI4kHWQ1JItIS-WDypEaDX88sDy-CjrH5_nXCo/", "홈페이지/채널 도입문의 결과")
            render_excel_link("체험신청 설문 데이터", "https://docs.google.com/spreadsheets/d/1q_hB7JzWUC9_1Vx_q8nVeHfekZeD3h-0A-MFPi7XKBo/", "학교 체험 신청서 인입 현황")
        with c2:
            render_excel_link("체험계정 발급 (총판/본사)", "https://docs.google.com/spreadsheets/d/1ZL3p5WKL_c0h5DAbLoFgULx6_n3boF5M27nuKdMPrhM/", "B2G 전용 체험 ID 관리")
            render_excel_link("독서화랑 클래스 CS 가이드", "https://docs.google.com/spreadsheets/d/1RUKAv5IqgcIv-2-H8sU5JVrusMfGwjpHswU55kg8k30/", "클래스 관련 CS 응대 매뉴얼")
            render_excel_link("연구부-디딤유 소통 (B2G)", "https://docs.google.com/spreadsheets/d/1YOBP7gulI7JFTsSWe35wW_0rmSN4p3C2Xee7hSUEzQw/", "B2G 관련 부서간 협업 소통")
            render_excel_link("독서화랑 클래스 도서", "https://docs.google.com/spreadsheets/d/1TDnfp_64YSviZNp96_WwrZ4pqC5q6TqtvgsTLZYqlyI/", "클래스 운영 도서 리스트")

    # --- 카테고리 3: B2C/재원생 관리 ---
    with tab3:
        st.write("")
        cl1, cl2 = st.columns(2)
        with cl1:
            render_excel_link("CS 운영 관리", "https://docs.google.com/spreadsheets/d/1HbOG1FE2sAonh_xHsxHHJIiFGV0fdteY/", "B2C 고객 상담 및 운영 관리")
            render_excel_link("체험계정 발급 (B2C)", "https://docs.google.com/spreadsheets/d/1fRD_NAG8ucp0lUA8dPHk8GljYMNgpZ6V_Fuhm6s0kwk/", "개인 체험 회원 계정 관리")
        with cl2:
            render_excel_link("연구부-디딤유 소통 (B2C)", "https://docs.google.com/spreadsheets/d/1ez_xh5TKmfZcS2yw-uU56dAg-ZcyNvo-gh-3Ie-xF0g/", "B2C 관련 부서간 협업 소통")

    st.divider()
    st.caption("새로운 업무 시트가 생성되면 리스트에 추가해 주세요.")

if __name__ == "__main__":
    display_excel_list()