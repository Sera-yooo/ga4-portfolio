import streamlit as st
import src.style_utils as style
from datetime import date

# --- 0. 페이지 설정 ---
st.set_page_config(
    page_title="독서화랑 마케팅 통합 대시보드", 
    page_icon="👩‍💻", 
    layout="wide"
)

# 공통 스타일 및 기존 CSS 적용
style.apply_common_style(is_sidebar_page=False)

# --- 1. 로그인 로직 함수 ---
def check_password():
    def password_entered():
        correct_password = st.secrets.get("dashboard_password", "0001")
        if st.session_state["password_input"] == correct_password:
            st.session_state["password_correct"] = True
            del st.session_state["password_input"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    # [로그인 전 화면] 사이드바 숨김
    st.markdown("<style>[data-testid='stSidebar'] {display: none;}</style>", unsafe_allow_html=True)
    render_main_intro(logged_in=False)
    return False

# --- 2. 메인 안내 UI 함수 (로그인 전/후 공통 사용) ---
def render_main_intro(logged_in=False):
    # 상단 헤더
    st.markdown("# 🚀 독서화랑 마케팅 통합 데이터 엔진")
    st.markdown("##### 마케팅팀의 주력 사업인 **독서화랑 클래스 B2G 사업**과 운영 전반을 관리하는 전용 대시보드입니다.")
    st.divider()

    # 메인 레이아웃 (안내 박스 | 인증 박스)
    col_info, col_action = st.columns([1.2, 0.8], gap="large")

    with col_info:
        # 1. 시스템 활용 가이드 (닫는 태그 오류 수정)
        guide_text = (
            "이 페이지는 엑셀에 흩어져 있는 방대한 데이터를 시각화하고, "
            "현장에서의 빠른 데이터 입력을 지원하기 위해 구축되었습니다.<br><br>"
            "• <b>B2G 통합 대시보드</b>: 주력 사업의 실시간 현황 파악 및 학교 상담 이력 관리<br>"
            "• <b>CS 응답 및 가입자 분석</b>: 고객 접점 데이터 기반의 인사이트 도출<br>"
            "• <b>통합 리소스 조회</b>: 구글 챗봇 데이터 및 각 계정별 상세 정보 관리"
        )
        style.render_info_card("📋", "시스템 활용 가이드", guide_text)
        
        # ⚙️ 기술 안내 섹션
        with st.expander("⚙️ 이용 전 필수 참고 사항 (기술 안내)", expanded=True):
            st.info("**1. 데이터 동기화 (Caching)**: 엑셀 수정 시 시스템 반영까지 **약 10분 내외**가 소요됩니다.")
            st.warning("**2. 초기 접속 로딩 (Wake-up)**: 첫 접속 시 서버 가동을 위해 **10~20초** 정도 지연될 수 있습니다.")

    with col_action:
        if not logged_in:
            # 2. 보안 접속 (글자 노출 해결)
            style.render_info_card("🔐", "보안 접속", "민감한 정보 보호를 위해 마케팅팀 전용 비밀번호를 입력해 주세요.")
            
            # 입력창과 버튼은 카드 밖(바로 아래)에 배치하여 충돌 방지
            pw_input = st.text_input("비밀번호", type="password", key="password_input", label_visibility="collapsed", placeholder="비밀번호 입력")
            if st.button("입장하기", use_container_width=True):
                correct_password = st.secrets.get("dashboard_password", "0001")
                if pw_input == correct_password:
                    st.session_state["password_correct"] = True
                    st.rerun()
                else:
                    st.error("😕 비밀번호가 틀렸습니다.")
        else:
            # 3. 접속 승인됨 (일관된 디자인)
            status_text = f"오늘 날짜: <b>2026-05-13</b><br><br>마케팅팀 권한으로 접속 중입니다.<br>왼쪽 메뉴를 통해 페이지를 이동하세요."
            style.render_info_card("✅", "접속 승인됨", status_text)
            
            if st.button("로그아웃", use_container_width=True):
                st.session_state["password_correct"] = False
                st.rerun()

# --- 3. 본문 실행 ---
if check_password():
    # 사이드바 표시
    st.markdown("<style>[data-testid='stSidebar'] {display: block;}</style>", unsafe_allow_html=True)

    with st.sidebar:
        st.image("https://api.dicebear.com/9.x/miniavs/svg?seed=csmanager", width=120)
        st.markdown("<h2 style='text-align: center;'>👩‍💻 CS Manager</h2>", unsafe_allow_html=True)
        st.divider()
        st.markdown("### 📂 메뉴 바로가기")
        # 카드 대신 사이드바 메뉴 활용 (페이지 이동)
        st.page_link("pages/01_B2G_통합_대시보드.py", label="B2G 통합 대시보드", icon="📊")
        st.page_link("pages/14_B2C_CS분석.py", label="B2C CS 응답 분석", icon="📞")
        st.page_link("pages/14_신규가입자분석.py", label="가입자 지표 분석", icon="📈")
        st.page_link("pages/02_Excel_List.py", label="B2G 계정/시트 관리", icon="🏫")
        
    # 메인 화면에는 설명 페이지를 계속 보여줌
    render_main_intro(logged_in=True)
    
    style.render_footer_badge()