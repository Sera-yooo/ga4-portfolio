import streamlit as st
# ✨ 제작한 스타일 유틸리티에서 함수 가져오기
from src.style_utils import apply_purple_theme, render_project_card
from src.tabs import message_work  # <-- 안내문 생성 모듈 가져오기

# --- 0. 페이지 설정 ---
st.set_page_config(
    page_title="독서화랑 운영 전반 대시보드", 
    page_icon="👩‍💻", 
    layout="wide"
)

# --- 1. 로그인 로직 (기존 유지) ---
def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets.get("dashboard_password", "0001"):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("<style>[data-testid='stSidebar'] {display: none;}</style>", unsafe_allow_html=True)
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        col_l, col_m, col_r = st.columns([1, 2, 1])
        with col_m:
            st.markdown("### 🔒 보안 접속")
            st.info("이곳은 독서화랑 마케팅팀 전용 공간입니다.")
            st.text_input("비밀번호를 입력하세요", type="password", on_change=password_entered, key="password")
        return False
    return True

# --- 2. 본문 실행 ---
if check_password():
    apply_purple_theme()

    # --- 사이드바 메뉴 구성 ---
    with st.sidebar:
        st.image("https://api.dicebear.com/9.x/miniavs/svg?seed=csmanager", width=120)
        st.markdown("<h2 style='text-align: center;'>👩‍💻 CS Manager</h2>", unsafe_allow_html=True)
        
        # [추가] 사이드바 메뉴 선택창
        st.divider()
        menu = st.radio(
            "📍 바로가기 메뉴",
            ["🏠 홈 (대시보드)", "📩 안내문 생성기", "📊 CS 응답 분석", "📈 가입자 분석", "🏫 B2G 통합관리"],
            key="main_menu"
        )
        st.divider()
        
        if st.button("안전 로그아웃", use_container_width=True):
            del st.session_state["password_correct"]
            st.rerun()

    # --- [분기 로직] 선택된 메뉴에 따라 화면 렌더링 ---

    # 1. 홈 화면 (카드형 메뉴)
    if menu == "🏠 홈 (대시보드)":
        st.markdown("# 🚀 Data Intelligence Dashboard")
        st.markdown("<p style='color: #6c757d; font-size: 1.1rem;'>실무 데이터 분석과 기술을 접목하여 구축한 독서화랑 마케팅 관리자 대시보드입니다.</p>", unsafe_allow_html=True)
        st.divider()

        col1, col2, col3 = st.columns(3)
        with col1:
            # 카드를 클릭해도 해당 메뉴로 이동하게끔 구성 가능 (여기선 시각적 역할)
            render_project_card("📊", "[B2C] CS 응답 분석", "고객 응대 데이터를 심층 분석합니다.", "01_B2C_CS분석", "btn_01")
        with col2:
            render_project_card("📈", "가입자 분석", "유입 경로와 핵심 성장 지표를 관리합니다.", "02_신규가입자분석", "btn_02")
        with col3:
            # 안내문 생성기 카드를 클릭하면 사이드바 메뉴가 바뀌도록 세팅 가능
            render_project_card("📩", "CS 안내문 생성", "체험/계약 학교 안내문을 자동 생성합니다.", "message_work", "btn_msg")

        # 하단 배너
        st.markdown("""
            <div class="creator-badge">
                <div class="creator-badge-inner">
                    <div style='font-size: 1.2rem; font-weight: bold;'>🚀 Powered by 호연</div>
                    <div style='font-size: 0.8rem; opacity: 0.7;'>독서화랑 운영 효율화 프로젝트 2026</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    # 2. 메시지 생성기 화면
    elif menu == "📩 안내문 생성기":
        message_work.render() # message_work.py의 내용을 그대로 불러옴

    # 3. 기타 분석 화면들 (준비 중인 페이지 예시)
    else:
        st.title(f"{menu}")
        st.info("이 페이지는 현재 데이터 연동 작업 중입니다.")