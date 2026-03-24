import streamlit as st
# ✨ 제작한 스타일 유틸리티에서 함수 가져오기
from src.style_utils import apply_purple_theme, render_project_card

# --- 0. 페이지 설정 (최상단 고정) ---
st.set_page_config(
    page_title="독서화랑 운영 전반 대시보드", 
    page_icon="👩‍💻", 
    layout="wide"
)

# --- 1. 로그인 로직 ---
def check_password():
    def password_entered():
        # secrets에 설정된 비밀번호 또는 기본값 '0000'
        if st.session_state["password"] == st.secrets.get("dashboard_password", "0001"):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # 로그인 전에는 사이드바 숨김
        st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} [data-testid='stSidebar'] {display: none;}</style>", unsafe_allow_html=True)
        
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        col_l, col_m, col_r = st.columns([1, 2, 1])
        with col_m:
            st.markdown("### 🔒 보안 접속")
            st.info("이곳은 독서화랑 마케팅팀 전용 공간입니다.")
            st.text_input("비밀번호를 입력하세요", type="password", on_change=password_entered, key="password")
        return False
    
    elif not st.session_state["password_correct"]:
        st.error("❌ 비밀번호가 올바르지 않습니다.")
        st.text_input("비밀번호를 입력하세요", type="password", on_change=password_entered, key="password")
        return False
    
    return True

# --- 2. 로그인 성공 시 본문 실행 ---
if check_password():
    # 🎨 보라색 테마 및 투명 버튼 레이어 적용
    apply_purple_theme()

    # --- 사이드바 구성 ---
    with st.sidebar:
        st.image("https://api.dicebear.com/9.x/miniavs/svg?seed=csmanager", width=120)
        st.markdown("<h2 style='text-align: center;'>👩‍💻 Profile</h2>", unsafe_allow_html=True)
        st.info("**CS Manager & Analyst**\n\n'데이터와 기술로 고객 경험을 설계합니다.'")
        
        st.divider()
        
        # 제작자 정보 배지
        st.markdown("""
            <div style='background: white; padding: 15px; border-radius: 10px; border: 1px solid #eaeaea; border-left: 5px solid #764ba2;'>
                <div style='font-size: 0.8rem; color: #764ba2; font-weight: bold;'>DEVELOPER</div>
                <div style='font-size: 1.1rem; font-weight: 800;'>Engineer. 호연</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        if st.button("안전 로그아웃"):
            del st.session_state["password_correct"]
            st.rerun()

    # --- 메인 영역 헤더 ---
    st.markdown("# 🚀 Data Intelligence Dashboard")
    st.markdown("<p style='color: #6c757d; font-size: 1.1rem;'>실무 데이터 분석과 기술을 접목하여 구축한 독서화랑 마케팅 관리자 대시보드입니다.</p>", unsafe_allow_html=True)
    st.divider()

    # --- 3. 프로젝트 섹션 (일체형 카드 렌더링) ---
    col1, col2, col3 = st.columns(3)

    with col1:
        render_project_card(
            "📊", "[B2C] CS 응답 분석", 
            "고객 응대 데이터를 심층 분석하여 서비스의 강점과 개선점을 파악하고 운영 효율을 높이는 인사이트를 도출합니다.", 
            "01_B2C_CS분석", "btn_01"
        )

    with col2:
        render_project_card(
            "📈", "독서화랑 가입자 분석", 
            "신규 가입자 데이터를 다각도로 분석하여 유입 경로와 유저 특성을 파악하고 핵심 성장 지표를 관리합니다.", 
            "02_신규가입자분석", "btn_02"
        )

    with col3:
        render_project_card(
            "🏫", "[B2G] 통합 대시보드", 
            "체험 학교 코드 생성부터 총판 관리, 계약 학교 현황까지 한 곳에서 관리하는 올인원 시스템입니다.", 
            "09_B2G_통합_대시보드", "btn_09"
        )

    # 챗봇은 하단에 별도 배치 (필요시 3열 중 하나로 옮겨도 됩니다)
    st.write("")
    render_project_card(
        "🤖", "독서화랑 AI CS 챗봇", 
        "Gemini 1.5 Flash 기반 RAG 시스템입니다. 독서화랑 운영 정책을 학습하여 정확하고 친절한 답변을 제공합니다.", 
        "03_독서화랑 AI CS 챗봇", "btn_03"
    )

# --- 4. 하단 제작자 배지 (애니메이션 통합 적용) ---    
    st.markdown("""
        <div class="creator-badge">
            <div style='font-size: 1.4rem; font-weight: bold;'>🚀 Powered by 호연</div>
            <div style='font-size: 0.85rem; font-weight: normal; opacity: 0.9; margin-top:5px;'>
                독서화랑 운영 효율화 프로젝트 2026
            </div>
        </div>
    """, unsafe_allow_html=True)