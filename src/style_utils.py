import streamlit as st

def apply_purple_theme():
    """배경색, 애니메이션, 일체형 카드 및 배지 빛 효과 CSS"""
    st.markdown("""
        <style>
        .stApp { background-color: #f8f9fe; }
        
        /* 1. 카드 전체 감싸는 컨테이너 */
        .card-wrapper {
            position: relative;
            transition: all 0.3s ease-in-out;
            margin-bottom: 20px;
            overflow: hidden;
            border-radius: 15px;
        }

        .card-wrapper:hover {
            transform: translateY(-8px);
            box-shadow: 0 12px 24px rgba(118, 75, 162, 0.15);
        }

        /* 2. 카드 몸체 및 하단 가짜 버튼 */
        .card-body {
            background: white;
            padding: 30px 25px;
            border-radius: 15px 15px 0 0;
            border: 1px solid #eaeaea;
            border-bottom: none;
        }
        .card-footer {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px;
            text-align: center;
            border-radius: 0 0 15px 15px;
            font-weight: bold;
            font-size: 0.9rem;
        }

        /* 3. 투명 스트림릿 버튼 (카드 전체 덮기) */
        .stButton button {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: transparent !important;
            border: none !important;
            color: transparent !important;
            z-index: 10;
            cursor: pointer;
        }

        /* 4. ✨ 제작자 배지 전용 애니메이션 (빛 효과 부활) */
        .creator-badge {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            margin-top: 30px;
            position: relative; /* 빛 효과의 기준 */
            overflow: hidden;   /* 빛이 밖으로 안 나가게 */
            transition: all 0.3s ease;
            box-shadow: 0 6px 15px rgba(118, 75, 162, 0.2);
        }

        .creator-badge:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 20px rgba(118, 75, 162, 0.3);
        }

        /* ✨ 배지 위를 지나가는 빛 레이어 */
        .creator-badge::after {
            content: '';
            position: absolute;
            top: -50%;
            left: -150%; /* 시작 위치 (왼쪽 밖) */
            width: 200%;
            height: 200%;
            background: rgba(255, 255, 255, 0.15); /* 투명한 흰색 빛 */
            transform: rotate(30deg); /* 빛을 살짝 기울임 */
            transition: all 0.6s ease; /* 빛이 지나가는 속도 */
            pointer-events: none;
        }

        /* 마우스 올리면 빛이 왼쪽에서 오른쪽으로 이동 */
        .creator-badge:hover::after {
            left: 100%;
        }
        </style>
    """, unsafe_allow_html=True)

def render_project_card(emoji, title, description, page_name, btn_key):
    """일체형 카드 렌더러"""
    st.markdown(f"""
        <div class="card-wrapper">
            <div class="card-body">
                <div style="font-size:1.4rem; font-weight:800; color:#2c3e50; margin-bottom:12px;">{emoji} {title}</div>
                <div style="color:#6c757d; font-size:0.92rem; line-height:1.6; min-height:80px;">{description}</div>
            </div>
            <div class="card-footer">
                {title} 분석 환경 바로가기
            </div>
    """, unsafe_allow_html=True)
    
    if st.button("Link", key=btn_key):
        st.switch_page(f"pages/{page_name}.py")
        
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("""
    <style>
    /* 탭 메뉴 강조색을 보라색으로 */
    button[data-baseweb="tab"] > div[aria-selected="true"] {
        color: #764ba2 !important;
        border-color: #764ba2 !important;
    }
    /* 데이터프레임 헤더 색상 보정 */
    .stDataFrame thead tr th {
        background-color: #f8f9fe !important;
        color: #764ba2 !important;
    }
    </style>
""", unsafe_allow_html=True)