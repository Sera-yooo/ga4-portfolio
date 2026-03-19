import streamlit as st

# --- 0. 페이지 설정 (최상단) ---
st.set_page_config(page_title="독서화랑 운영 전반 대시보드", page_icon="👩‍💻", layout="wide")

# --- 1. 로그인 로직 ---
def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets.get("dashboard_password", "0000"):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # 로그인 전에는 사이드바를 숨깁니다 (빈 공간 처리)
        st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;} [data-testid='stSidebar'] {display: none;}</style>", unsafe_allow_html=True)
        
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        col_l, col_m, col_r = st.columns([1, 2, 1])
        with col_m:
            st.markdown("### 🔒 보안 접속")
            st.text_input("비밀번호를 입력하세요", type="password", on_change=password_entered, key="password")
        return False
    
    elif not st.session_state["password_correct"]:
        st.markdown("<style>[data-testid='stSidebar'] {display: none;}</style>", unsafe_allow_html=True)
        st.error("❌ 비밀번호가 올바르지 않습니다.")
        # ... (재입력 로직)
        return False
    
    return True

# --- 로그인 성공 시 본문 실행 ---
if check_password():

    # --- 2. [디자인] 보라색 톤앤매너 커스텀 CSS (완전 새단장) ---
    st.markdown("""
        <style>
        /* 기본 배경화면을 아주 연한 보라색으로 */
        .stApp {
            background-color: #f8f9fe;
        }
        
        /* 프로젝트 카드 스타일 (보라색 포인트 & 그라데이션 배경) */
        .project-card {
            padding: 30px;
            border-radius: 20px;
            background: white;
            border: 1px solid #eaeaea;
            box-shadow: 0 4px 15px rgba(118, 75, 162, 0.05);
            transition: all 0.3s ease-in-out;
            margin-bottom: 15px;
            min-height: 250px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        
        /* 마우스 올렸을 때 애니메이션 (보라색 그림자 & 살짝 들림) */
        .project-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 12px 24px rgba(118, 75, 162, 0.15);
            border: 1px solid #dcd1ff;
        }

        /* 카드 제목 스타일 */
        .card-title {
            color: #2c3e50;
            font-size: 1.5rem;
            font-weight: 800;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        /* 카드 설명 스타일 */
        .card-text {
            color: #6c757d;
            font-size: 0.98rem;
            line-height: 1.7;
            margin-bottom: 25px;
            flex-grow: 1; /* 텍스트가 남은 공간 채우도록 */
        }

        /* 버튼 스타일 커스텀 (보라색 그라데이션) */
        div.stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border-radius: 12px !important;
            border: none !important;
            padding: 10px 20px !important;
            font-weight: bold !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 6px rgba(118, 75, 162, 0.2) !important;
        }
        
        div.stButton > button:hover {
            box-shadow: 0 7px 14px rgba(118, 75, 162, 0.3) !important;
            transform: scale(1.02) !important;
        }

        /* 제작자 배지 스타일 (그라데이션 & 테두리 애니메이션) */
        .creator-badge {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            font-weight: bold;
            margin-top: 30px;
            box-shadow: 0 6px 15px rgba(118, 75, 162, 0.25);
            position: relative;
            overflow: hidden;
        }
        
        .creator-badge::after {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: rgba(255,255,255,0.1);
            transform: rotate(30deg);
            transition: all 0.5s;
            visibility: hidden;
        }
        
        .creator-badge:hover::after {
            visibility: visible;
            left: 100%;
        }
        </style>
        """, unsafe_allow_html=True)

    # --- 카드 생성 함수 ---
    def render_card(emoji, title, description, page_name, btn_key):
        # HTML 카드 렌더링
        st.markdown(f"""
            <div class="project-card">
                <div>
                    <div class="card-title">{emoji} {title}</div>
                    <div class="card-text">{description}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # 실제 이동 버튼
        if st.button(f"{title} 분석 환경 바로가기", key=btn_key, width="stretch"):
            st.switch_page(f"pages/{page_name}.py")

    # --- 사이드바 (기존 유지하되 보라색 배지 강화) ---
    with st.sidebar:
        st.image("https://api.dicebear.com/9.x/miniavs/svg?seed=csmanager", width=120)
        st.markdown("<h2 style='text-align: center; color: #2c3e50;'>👩‍💻 Profile</h2>", unsafe_allow_html=True)
        st.info("**CS Manager & Analyst**\n\n'데이터와 기술로 고객 경험을 설계합니다.'")
        
        st.divider()
        
        # ✨ 제작자 정보 (사이드바 하단 - 더 세련되게)
        st.markdown("""
            <div style='background: white; padding: 15px; border-radius: 10px; border: 1px solid #eaeaea; border-left: 5px solid #764ba2; box-shadow: 0 2px 5px rgba(0,0,0,0.05);'>
                <div style='font-size: 0.8rem; color: #764ba2; font-weight: bold; margin-bottom: 5px;'>DEVELOPER</div>
                <div style='font-size: 1.2rem; color: #2c3e50; font-weight: 800;'>Engineer. 호연</div>
                <div style='font-size: 0.85rem; color: #6c757d; margin-top: 3px;'>B2G System Architecture & AI Logic</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        if st.button("안전 로그아웃"):
            del st.session_state["password_correct"]
            st.rerun()

    # --- 메인 영역 ---
    st.markdown("<h1 style='color: #2c3e50; font-weight: 900; font-size: 3rem; margin-bottom: 0px;'>🚀 Data Intelligence Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #6c757d; font-size: 1.2rem; margin-top: 5px;'>실무 데이터 분석과 기술을 접목하여 구축한 독서화랑 마케팅 관리자 대시보드입니다.</p>", unsafe_allow_html=True)
    
    # --- 프로젝트 섹션 (3단 구성) ---
    col1, col2, col3 = st.columns(3)

    with col1:
        render_card("📊", "[B2C] CS 응답 분석", 
                    "고객 응대 데이터를 심층 분석하여 서비스의 강점과 개선점을 파악하고 운영 효율을 높이는 인사이트를 도출합니다.", 
                    "01_B2C_CS분석", "btn_01")

    with col2:
        render_card("📈", "독서화랑 가입자 분석", 
                    "신규 가입자 데이터를 다각도로 분석하여 유입 경로와 유저 특성을 파악하고 핵심 성장 지표를 관리합니다.", 
                    "02_신규가입자분석", "btn_02")
    with col3:
        render_card("🏫", "[B2G] 통합 대시보드", 
            "체험 학교 코드 생성부터 총판 관리, 계약 학교 현황까지 한 곳에서 관리하는 올인원 시스템입니다.", 
            "09_B2G_통합_대시보드", "btn_09")
         
    render_card("🤖", "독서화랑 AI CS 챗봇", 
                "Gemini 1.5 Flash 기반 RAG 시스템입니다. 독서화랑 운영 정책을 RAG로 학습하여 정확하고 친절한 답변을 제공합니다.", 
                "03_독서화랑 AI CS 챗봇", "btn_03")        

    st.markdown("<br>", unsafe_allow_html=True)

    # ✨ 메인 우측 하단 빵빵한 기록 배지 (애니메이션 효과 추가)
    st.markdown("""
        <div class="creator-badge">
            <span style='font-size: 1.3rem;'>🚀 Powered by 호연</span><br>
            <span style='font-size: 0.85rem; font-weight: normal; opacity: 0.8;'>독서화랑 운영 효율화 프로젝트 2026</span>
        </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.caption("© 2026 독서화랑 운영 대시보드 시스템.")