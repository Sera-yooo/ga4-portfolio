import streamlit as st
import src.style_utils as style

# --- 0. 페이지 설정 (반드시 가장 상단에 1회만 호출) ---
st.set_page_config(
    page_title="독서화랑 운영 전반 대시보드", 
    page_icon="👩‍💻", 
    layout="wide"
)

# 공통 스타일 적용
style.apply_common_style()

# 안내문 생성 모듈 가져오기 (import 에러 방지를 위해 위쪽에서 선언)
try:
    from src.tabs import message_work
except ImportError:
    message_work = None

# --- 1. 로그인 로직 ---
def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets.get("dashboard_password", "0001"):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # 로그인 전에는 사이드바 숨김
        st.markdown("<style>[data-testid='stSidebar'] {display: none;}</style>", unsafe_allow_html=True)
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        col_l, col_m, col_r = st.columns([1, 2, 1])
        with col_m:
            st.markdown("### 🔒 보안 접속")
            st.info("이곳은 독서화랑 마케팅팀 전용 공간입니다.")
            st.text_input("비밀번호를 입력하세요", type="password", on_change=password_entered, key="password")
            
            if "password_correct" in st.session_state and not st.session_state["password_correct"]:
                st.error("😕 비밀번호가 틀렸습니다.")
        return False
    return True

# --- 2. 본문 실행 ---
# --- 2. 본문 실행 ---
if check_password():   

    # --- 사이드바 메뉴 구성 ---
    with st.sidebar:
        st.image("https://api.dicebear.com/9.x/miniavs/svg?seed=csmanager", width=120)
        st.markdown("<h2 style='text-align: center;'>👩‍💻 CS Manager</h2>", unsafe_allow_html=True)
        st.divider()
        
        # 라디오 버튼 제거 -> 대신 홈으로 돌아오는 명시적인 버튼 (다른 페이지에서 이동해 올 때 대비)
        st.info("💡 카드를 클릭하여 메뉴로 이동하세요.")
        
        if st.button("안전 로그아웃", use_container_width=True):
            del st.session_state["password_correct"]
            st.rerun()

    # --- 홈 화면 레이아웃 (카드형 메뉴) ---
    st.markdown("# 🚀 Data Intelligence Dashboard")
    st.markdown("<p style='color: #64748B; font-size: 1.1rem;'>실무 데이터 분석과 기술을 접목하여 구축한 독서화랑 마케팅 관리자 대시보드입니다.</p>", unsafe_allow_html=True)
    st.divider()

    # 3열 구성 카드 메뉴
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # [B2C] CS 응답 분석 페이지로 이동
        style.render_project_card("📊", "[B2C] CS 응답 분석", "고객 응대 데이터를 심층 분석합니다.", "01_B2C_CS분석", "btn_01")
    
    with col2:
        # 가입자 분석 페이지로 이동
        style.render_project_card("📈", "가입자 분석", "유입 경로와 핵심 성장 지표를 관리합니다.", "02_신규가입자분석", "btn_02")
    
    with col3:
        # 안내문 생성기 페이지로 이동 (pages/03_B2G_통합_대시보드.py 등으로 파일이 있어야 함)
        style.render_project_card("📩", "CS 안내문 생성", "체험/계약 학교 안내문을 자동 생성합니다.", "03_B2G_통합_대시보드", "btn_msg")

    # 추가 라인 (필요시)
    st.write("")
    col4, col5, col6 = st.columns(3)
    with col4:
        # B2G 통합관리 페이지 이동
        style.render_project_card("🏫", "B2G 통합관리", "팀 통합 리소스 및 계정을 관리합니다.", "14_Excel_List", "btn_14")

    style.render_footer_badge()