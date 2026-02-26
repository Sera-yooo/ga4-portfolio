import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="CS Manager Portfolio",
    page_icon="👩‍💻",
    layout="wide"
)

# --- [디자인] 커스텀 CSS ---
st.markdown("""
    <style>
    /* 카드 전체 스타일 */
    .project-card {
        padding: 25px;
        border-radius: 15px;
        background-color: #ffffff;
        border: 1px solid #e6e9ef;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin-bottom: 10px;
        min-height: 220px;
    }
    /* 카드 제목 스타일 */
    .card-title {
        color: #1f1f1f;
        font-size: 1.4rem;
        font-weight: bold;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    /* 카드 설명 스타일 */
    .card-text {
        color: #555;
        font-size: 0.95rem;
        line-height: 1.6;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 카드 생성 함수 ---
def render_card(emoji, title, description, page_name, btn_key):
    # HTML 카드 렌더링
    st.markdown(f"""
        <div class="project-card">
            <div class="card-title">{emoji} {title}</div>
            <div class="card-text">{description}</div>
        </div>
    """, unsafe_allow_html=True)
    
    # 실제 이동 버튼 (width='stretch' 사용으로 경고 해결)
    if st.button(f"{title} 바로가기", key=btn_key, width="stretch"):
        st.switch_page(f"pages/{page_name}.py")

# --- 사이드바 ---
with st.sidebar:
    st.image("https://api.dicebear.com/9.x/miniavs/svg?seed=csmanager", width=120)
    st.markdown("## 👩‍💻 Profile")
    st.info("**CS Manager & Analyst**\n\n'데이터와 기술로 고객 경험을 설계합니다.'")
    st.divider()
    st.markdown("### 📧 Contact")
    st.caption("your_email@example.com")

# --- 메인 영역 ---
st.title("🚀 CS & Data Intelligence Dashboard")
st.write("실무 경험에 데이터 분석과 AI 기술을 접목하여 구축한 포트폴리오입니다.")
st.divider()

# --- 프로젝트 섹션 (2단 구성) ---
col1, col2 = st.columns(2)

with col1:
    render_card("📊", "일반 CS 응답 분석", 
                "고객 응대 데이터를 심층 분석하여 서비스의 강점과 개선점을 파악하고 운영 효율을 높이는 인사이트를 도출합니다.", 
                "01_일반CS분석", "btn_01")

with col2:
    render_card("📈", "독서화랑 가입자 분석", 
                "신규 가입자 데이터를 다각도로 분석하여 유입 경로와 유저 특성을 파악하고 핵심 성장 지표를 관리합니다.", 
                "02_신규가입자분석", "btn_02")

st.markdown("<br>", unsafe_allow_html=True) # 줄바꿈 여백

col3, col4 = st.columns(2)

with col3:
    render_card("🤖", "독서화랑 AI CS 챗봇", 
                "Gemini 2.5 Flash 기반 RAG 시스템입니다. 독서화랑의 운영 정책을 학습하여 고객에게 정확하고 친절한 답변을 제공합니다.", 
                "03_AIChatbot", "btn_03")

with col4:
    render_card("🏫", "클래스 CS 분석", 
                "B2B 서비스인 '독서화랑 클래스'의 문의 패턴을 집중 분석하여 교육기관 맞춤형 대응 체계를 구축합니다.", 
                "04_클래스CS분석", "btn_04")

st.markdown("<br>", unsafe_allow_html=True)

col5, col6 = st.columns(2)

with col5:
    render_card("✉️", "학교 소통 메일 템플릿", 
                "학교 현장 소통을 위한 표준화된 예시문을 제공합니다. 상황별 템플릿을 통해 업무의 속도와 전문성을 높입니다.", 
                "06_학교_메일전송_템플릿", "btn_06")

with col6:
    st.empty()

st.divider()
st.caption("© 2026 CS Manager Portfolio. Built with Streamlit & Python.")