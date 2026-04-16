import streamlit as st

# 1. 페이지 설정
import src.style_utils as style
st.set_page_config(page_title="독서화랑 노션 위키 이동 페이지", layout="wide")
style.apply_common_style()

def display_guide():
    st.markdown("### 📘 독서화랑 노션 위키")
    
    # 노션 원본 주소
    notion_url = "https://www.notion.so/dsmynotification/f5762eafdd5c834e8e240196c951d6a4?v=8ca62eafdd5c82609305887da638776f"
    
    st.info("💡 보안 정책으로 인해 가이드는 노션(Notion) 링크로 접속해야 합니다.")

    # ---------------------------------------------------------
    # 🏝️ 상단 정보 카드 (퍼플 디자인)
    # ---------------------------------------------------------
    col1, col2 = st.columns(2)
    
    with col1:
        style.render_stat_card(
            emoji="🚀",
            title="실시간 가이드",
            value="WIKI",
            unit="",
            description="노션에서 수정된 최신 문서를 \n실시간으로 확인하실 수 있습니다."
        )
        
    with col2:
        style.render_stat_card(
            emoji="✍️",
            title="문서 수정 권한",
            value="Edit",
            unit="",
            description="권한이 필요한 경우 @이주영 님께 요청합니다."
        )

    st.write("")
    st.divider()

    # ---------------------------------------------------------
    # 🖱️ 중앙 메인 연결 버튼 (와이드형)
    # ---------------------------------------------------------
    st.write("")
    
    # 버튼 디자인을 위한 약간의 여백
    _, center_col, _ = st.columns([1, 2, 1])
    
    with center_col:
        # 버튼 텍스트 구성
        btn_label = "📖 독서화랑 노션 위키 열기 (새 창)"
        
        # 버튼 클릭 시 노션으로 연결
        if st.button(btn_label, key="go_to_notion", use_container_width=True):
            # 자바스크립트를 이용해 새 탭으로 열기
            js = f'window.open("{notion_url}")'
            st.components.v1.html(f'<script>{js}</script>', height=0)
            st.success("노션 페이지로 이동 중입니다...")

    st.write("")
    st.write("")

    # ---------------------------------------------------------
    # 📌 하단 안내 사항
    # ---------------------------------------------------------
    with st.expander("📌 노션 위키에서 확인 가능한 항목", expanded=False):
        st.markdown("""
            #### 1. 운영 현황

            * 부서별 작업 현황

            #### 2. 자료 및 링크 모음

            * 회의 관련 링크
            * QA 시트 모음
            * 설문 결과 모음
            * 독서화랑 가이드 모음

            #### 3. 정책 및 문서

            * 정책서
            * 개인정보처리방침 / 이용약관
            * 인증 / 실증 문서
            * 기타 문서
        """)

    st.divider()
    st.caption("독서화랑 B2G 통합 관리 시스템 - 업무 지원 가이드")

if __name__ == "__main__":
    display_guide()