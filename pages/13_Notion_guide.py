import streamlit as st
from src.style_utils import apply_purple_theme, render_stat_card

# 1. 페이지 설정
st.set_page_config(page_title="독서화랑 업무 가이드", layout="wide")
apply_purple_theme()

def display_guide():
    st.markdown("### 📘 업무 SOP 및 가이드")
    
    # 노션 원본 주소
    notion_url = "https://placid-wishbone-f63.notion.site/B2G-B2C-SOP-33d4ee74bdba804fb5e3c36035942b95"
    
    st.info("💡 보안 정책으로 인해 가이드는 노션(Notion) 원본 페이지에서 확인하실 수 있습니다.")

    # ---------------------------------------------------------
    # 🏝️ 상단 정보 카드 (퍼플 디자인)
    # ---------------------------------------------------------
    col1, col2 = st.columns(2)
    
    with col1:
        render_stat_card(
            emoji="🚀",
            title="실시간 가이드",
            value="Notion",
            unit="",
            description="노션에서 수정된 최신 매뉴얼을\n실시간으로 확인하실 수 있습니다."
        )
        
    with col2:
        render_stat_card(
            emoji="✍️",
            title="문서 수정 권한",
            value="Edit",
            unit="",
            description="가이드 수정이 필요한 경우\n노션 로그인 후 직접 편집이 가능합니다."
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
        btn_label = "📖 독서화랑 SOP 가이드북 열기 (새 창)"
        
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
    with st.expander("❓ 가이드 이용 안내", expanded=False):
        st.markdown("""
        - **로그인 권한:** 노션 계정 권한에 따라 읽기 또는 편집이 가능합니다.
        - **검색 팁:** 노션 페이지 내부의 검색(Ctrl+P) 기능을 활용하면 원하는 매뉴얼을 빨리 찾을 수 있습니다.
        - **문의:** 내용 수정이 필요하거나 권한이 없는 경우 팀장님께 문의해 주세요.
        """)

    st.divider()
    st.caption("독서화랑 B2G 통합 관리 시스템 - 업무 지원 가이드")

if __name__ == "__main__":
    display_guide()