import streamlit as st
import src.style_utils as style

# --- 0. 페이지 설정 ---
st.set_page_config(
    page_title="독서화랑 운영 전반 대시보드", 
    page_icon="👩‍💻", 
    layout="wide"
)

# 공통 스타일 적용
style.apply_common_style(is_sidebar_page=False)

# --- 1. 로그인 로직 함수 ---
def check_password():
    """로그인 성공 시 True를 반환합니다."""
    
    def password_entered():
        """입력된 비밀번호가 맞는지 검증합니다."""
        # secrets에 설정된 비번이 없으면 기본값 '0001' 사용
        correct_password = st.secrets.get("dashboard_password", "0001")
        
        if st.session_state["password_input"] == correct_password:
            st.session_state["password_correct"] = True
            del st.session_state["password_input"]  # 보안을 위해 입력값 삭제
        else:
            st.session_state["password_correct"] = False

    # 1. 이미 로그인에 성공한 경우
    if st.session_state.get("password_correct", False):
        return True

    # 2. 로그인 화면 구성
    # 사이드바 숨김
    st.markdown("<style>[data-testid='stSidebar'] {display: none;}</style>", unsafe_allow_html=True)
    
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col_l, col_m, col_r = st.columns([1, 2, 1])
    
    with col_m:
        st.markdown("### 🔒 보안 접속")
        st.info("이곳은 독서화랑 마케팅팀 전용 공간입니다.")
        
        # 비밀번호 입력창
        st.text_input(
            "비밀번호를 입력하세요", 
            type="password", 
            on_change=password_entered, 
            key="password_input"
        )
        
        # 틀렸을 때만 에러 메시지 표시
        if "password_correct" in st.session_state and not st.session_state["password_correct"]:
            st.error("😕 비밀번호가 틀렸습니다.")
            
    return False

# --- 2. 본문 실행 (로그인 통과 시에만 실행) ---
if check_password():
    
    # 🔓 로그인 성공 후 사이드바 다시 표시 (스타일 리셋)
    st.markdown("<style>[data-testid='stSidebar'] {display: block;}</style>", unsafe_allow_html=True)

    # --- 사이드바 메뉴 구성 ---
    with st.sidebar:
        st.image("https://api.dicebear.com/9.x/miniavs/svg?seed=csmanager", width=120)
        st.markdown("<h2 style='text-align: center;'>👩‍💻 CS Manager</h2>", unsafe_allow_html=True)
        st.divider()
        
        st.info("💡 카드를 클릭하여 메뉴로 이동하세요.")
        
        if st.button("안전 로그아웃", use_container_width=True):
            st.session_state["password_correct"] = False
            st.rerun()

    # --- 홈 화면 레이아웃 (카드형 메뉴) ---
    st.markdown("# 🚀 Data Intelligence Dashboard")
    st.markdown("<p style='color: #64748B; font-size: 1.1rem;'>실무 데이터 분석과 기술을 접목하여 구축한 독서화랑 마케팅 관리자 대시보드입니다.</p>", unsafe_allow_html=True)
    st.divider()

    # 3열 구성 카드 메뉴
    col1, col2, col3 = st.columns(3)
    
    with col1:
        style.render_project_card("📊", "[B2C] CS 응답 분석", "고객 응대 데이터를 심층 분석합니다.", "01_B2C_CS분석", "btn_01")
    with col2:
        style.render_project_card("📈", "가입자 분석", "유입 경로와 핵심 성장 지표를 관리합니다.", "02_신규가입자분석", "btn_02")
    with col3:
        style.render_project_card("📩", "CS 안내문 생성", "체험/계약 학교 안내문을 자동 생성합니다.", "03_B2G_통합_대시보드", "btn_msg")

    st.write("")
    col4, col5, col6 = st.columns(3)
    with col4:
        style.render_project_card("🏫", "B2G 통합관리", "팀 통합 리소스 및 계정을 관리합니다.", "14_Excel_List", "btn_14")

    style.render_footer_badge()