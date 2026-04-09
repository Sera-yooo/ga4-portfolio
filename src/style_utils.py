import streamlit as st

def apply_purple_theme():
    """프리미엄 퍼플 & 미니멀리즘 테마 적용"""
    st.markdown("""
        <style>
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

        /* 전체 기본 폰트 및 배경색 */
        html, body, [class*="css"] {
            font-family: 'Pretendard', -apple-system, sans-serif;
        }
        
        .stApp {
            background: linear-gradient(135deg, #f5f7ff 0%, #ffffff 100%);
        }

        /* 1. 사이드바 디자인 커스텀 */
        [data-testid="stSidebar"] {
            background-color: #ffffff !important;
            border-right: 1px solid #f0f2f6;
        }

        /* 2. 카드형 버튼 (핵심 디자인) */
        div.stButton > button {
            background: rgba(255, 255, 255, 0.7) !important;
            backdrop-filter: blur(10px) !important;
            border: 1px solid rgba(118, 75, 162, 0.1) !important;
            border-radius: 20px !important;
            padding: 30px 25px !important;
            color: #1e293b !important;
            text-align: left !important;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.05) !important;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
            width: 100% !important;
            height: auto !important;
            display: block !important;
        }

        div.stButton > button:hover {
            transform: translateY(-10px) scale(1.02);
            border: 1px solid #764ba2 !important;
            background: #ffffff !important;
            box-shadow: 0 20px 40px rgba(118, 75, 162, 0.15) !important;
        }

        /* 버튼 텍스트 스타일링 */
        div.stButton > button p {
            white-space: pre-wrap !important;
            font-size: 1rem !important;
            line-height: 1.5 !important;
        }

        /* 3. 탭 디자인 - 현대적인 스타일 */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            background-color: transparent;
        }

        .stTabs [data-baseweb="tab"] {
            background-color: #f1f5f9;
            border-radius: 10px;
            padding: 8px 16px;
            color: #64748b;
            border: none !important;
            transition: 0.3s;
        }

        .stTabs [data-baseweb="tab"]:hover {
            background-color: #e2e8f0;
            color: #764ba2;
        }

        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white !important;
            box-shadow: 0 4px 12px rgba(118, 75, 162, 0.3);
        }

        /* 4. 제작자 배지 애니메이션 (더 세련되게) */
        .creator-badge {
            background: #1e1e2e;
            color: #cdd6f4;
            padding: 24px;
            border-radius: 24px;
            text-align: center;
            margin-top: 40px;
            border: 1px solid #313244;
            position: relative;
            overflow: hidden;
        }

        .creator-badge::before {
            content: "";
            position: absolute;
            top: -50%; left: -50%;
            width: 200%; height: 200%;
            background: conic-gradient(from 0deg, transparent, #764ba2, transparent 30%);
            animation: rotate 4s linear infinite;
        }

        .creator-badge-inner {
            position: relative;
            background: #1e1e2e;
            padding: 20px;
            border-radius: 20px;
            z-index: 1;
        }

        @keyframes rotate {
            100% { transform: rotate(360deg); }
        }
        </style>
    """, unsafe_allow_html=True)

def render_project_card(emoji, title, description, page_name, btn_key):
    """더 전문적인 느낌의 카드 텍스트 구성"""
    display_text = f"{emoji} {title}\n\n{description}\n\n"
    display_text += "────────────────────\n"
    display_text += "자세히 보기 →"
    
    if st.button(display_text, key=btn_key, use_container_width=True):
        st.info(f"[{title}] 화면으로 이동합니다.")
        # 실제 이동 로직은 app.py에서 메뉴 세션값을 바꾸는 방식으로 구현 권장

def apply_marine_theme():
    """푸른 바다 탐험 (Marine Explorer) 테마 적용"""
    st.markdown("""
        <style>
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

        /* 1. 배경: 깊은 바다에서 수면으로 올라오는 듯한 그라데이션 */
        .stApp {
            background: linear-gradient(180deg, #e0f2fe 0%, #ffffff 100%);
        }

        /* 2. 카드형 버튼: 파도와 거품처럼 부드럽고 투명한 느낌 */
        div.stButton > button {
            background: rgba(255, 255, 255, 0.6) !important;
            backdrop-filter: blur(12px) !important;
            border: 1px solid rgba(14, 165, 233, 0.2) !important;
            border-radius: 24px !important;
            color: #0369a1 !important; /* 진한 바다색 */
            box-shadow: 0 10px 25px rgba(0, 119, 182, 0.05) !important;
            transition: all 0.4s ease-in-out !important;
        }

        div.stButton > button:hover {
            transform: translateY(-8px);
            border: 1px solid #0ea5e9 !important; /* 밝은 하늘색 */
            background: #ffffff !important;
            box-shadow: 0 15px 35px rgba(14, 165, 233, 0.2) !important;
        }

        /* 3. 제작자 배지: 심해의 신비로운 빛 애니메이션 */
        .creator-badge {
            background: #0c4a6e; /* Deep Ocean Blue */
            color: #e0f2fe;
            border: 1px solid #0ea5e9;
        }

        .creator-badge::before {
            background: conic-gradient(from 0deg, transparent, #38bdf8, transparent 30%);
            animation: rotate 6s linear infinite;
        }
        
        /* 4. 사이드바 이미지 공간 확보 */
        [data-testid="stSidebar"] {
            background-color: #f8fafc !important;
            border-right: 2px solid #e0f2fe;
        }
        </style>
    """, unsafe_allow_html=True)

def render_sidebar_logo():
    # 사이드바 상단에 바다 탐험 느낌의 이미지 배치
    # 예: 고래나 돛단배 아이콘 등
    st.sidebar.markdown("""
        <div style="text-align: center; padding: 20px 0;">
            <h1 style="font-size: 40px; margin: 0;">🐳</h1>
            <p style="color: #0369a1; font-weight: bold; margin-top: 10px;">독서화랑: 바다 탐험대</p>
        </div>
    """, unsafe_allow_html=True)
    st.sidebar.divider()

def render_stat_card(emoji, title, value, unit, description):
    """퍼플 테마 정보 표시용 카드 (버튼 아님)"""
    st.markdown(f"""
        <div style="
            background: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 25px;
            border: 1px solid rgba(118, 75, 162, 0.1);
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.05);
            height: 100%;
            transition: transform 0.3s ease;
        ">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
                <span style="font-size: 22px;">{emoji}</span>
                <span style="font-size: 15px; font-weight: 600; color: #475569;">{title}</span>
            </div>
            <div style="margin-bottom: 8px;">
                <span style="font-size: 36px; font-weight: 800; color: #764ba2;">{value}</span>
                <span style="font-size: 16px; color: #64748b; margin-left: 4px;">{unit}</span>
            </div>
            <p style="font-size: 13px; color: #94a3b8; line-height: 1.5; margin: 0; white-space: pre-line;">
                {description}
            </p>
            <div style="
                margin-top: 15px;
                height: 3px;
                width: 30px;
                background: linear-gradient(90deg, #667eea, #764ba2);
                border-radius: 2px;
            "></div>
        </div>
    """, unsafe_allow_html=True)