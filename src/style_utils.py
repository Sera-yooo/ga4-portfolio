import streamlit as st

# ==========================================
# [중요] 마린 블루 & 화이트 테마 통합 색상 정의
# ==========================================
MAIN_PRIMARY = "#0EA5E9"     # 시원한 오션 블루
MAIN_GRADIENT = "linear-gradient(135deg, #0EA5E9 0%, #2563EB 100%)"
LIGHT_BG = "#FFFFFF"         # 깔끔한 순백색 배경
SIDEBAR_BG = "#F8FAFC"       # 사이드바 (아주 연한 회청색)
CARD_BG = "rgba(255, 255, 255, 0.8)" # 반투명 화이트 카드
BORDER_COLOR = "rgba(14, 165, 233, 0.1)" # 연한 블루 테두리

# 텍스트 색상
TEXT_DARK = "#0F172A"        # 메인 네이비 블랙 (가독성 최상)
TEXT_SUB = "#64748B"         # 보조 회청색

def apply_common_style():
    """시원한 바다 느낌의 마린 블루 테마 적용"""
    st.markdown(f"""
        <style>
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

        /* 1. 전체 기본 폰트 및 배경색 */
        html, body, [class*="css"] {{
            font-family: 'Pretendard', -apple-system, sans-serif;
            color: {TEXT_DARK};
        }}
        
        .stApp {{
            background-color: {LIGHT_BG};
        }}

        /* 2. 사이드바 디자인 (연한 회청색 배경) */
        [data-testid="stSidebar"] {{
            background-color: {SIDEBAR_BG} !important;
            border-right: 1px solid #E2E8F0;
        }}

        /* 3. 카드형 버튼 (블루 포인트) */
        div.stButton > button {{
            background: {CARD_BG} !important;
            backdrop-filter: blur(12px) !important;
            border: 1px solid {BORDER_COLOR} !important;
            border-radius: 20px !important;
            padding: 30px 25px !important;
            color: {TEXT_DARK} !important;
            text-align: left !important;
            box-shadow: 0 8px 32px 0 rgba(14, 165, 233, 0.05) !important;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
            width: 100% !important;
        }}

        div.stButton > button:hover {{
            transform: translateY(-10px) scale(1.02);
            border: 1px solid {MAIN_PRIMARY} !important;
            background: #ffffff !important;
            box-shadow: 0 20px 40px rgba(14, 165, 233, 0.15) !important;
        }}

        /* 4. 탭 디자인 - 마린 블루 스타일 */
        .stTabs [data-baseweb="tab"] {{
            background-color: #F1F5F9;
            border-radius: 10px;
            padding: 8px 16px;
            color: {TEXT_SUB};
            border: none !important;
            transition: 0.3s;
        }}

        .stTabs [data-baseweb="tab"]:hover {{
            background-color: #E0F2FE;
            color: {MAIN_PRIMARY};
        }}

        .stTabs [data-baseweb="tab"][aria-selected="true"] {{
            background: {MAIN_GRADIENT};
            color: white !important;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
        }}

        /* 5. 수평선 및 기타 요소 */
        hr {{
            border-color: #E2E8F0 !important;
        }}

        /* 6. 제작자 배지 애니메이션 (마린 블루 버전) */
        .creator-badge {{
            background: #0F172A; 
            color: #F1F5F9;
            padding: 24px;
            border-radius: 24px;
            text-align: center;
            margin-top: 50px;
            border: 1px solid #1E293B;
            position: relative;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}

        .creator-badge::before {{
            content: "";
            position: absolute;
            top: -50%; left: -50%;
            width: 200%; height: 200%;
            background: conic-gradient(from 0deg, transparent, #0EA5E9, transparent 30%, #22D3EE, transparent 70%);
            animation: rotate 6s linear infinite;
        }}

        .creator-badge-inner {{
            position: relative;
            background: #0F172A;
            padding: 20px;
            border-radius: 20px;
            z-index: 1;
        }}

        @keyframes rotate {{
            100% {{ transform: rotate(360deg); }}
        }}        
        </style>
    """, unsafe_allow_html=True)

def render_stat_card(emoji, title, value, unit, description):
    """마린 블루 지표 카드"""
    st.markdown(f"""
        <div style="
            background: {CARD_BG};
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 25px;
            border: 1px solid {BORDER_COLOR};
            box-shadow: 0 8px 32px 0 rgba(14, 165, 233, 0.05);
            height: 100%;
        ">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
                <span style="font-size: 22px;">{emoji}</span>
                <span style="font-size: 15px; font-weight: 600; color: #475569;">{title}</span>
            </div>
            <div>
                <span style="font-size: 36px; font-weight: 800; color: {MAIN_PRIMARY};">{value}</span>
                <span style="font-size: 16px; color: {TEXT_SUB}; margin-left: 4px;">{unit}</span>
            </div>
            <p style="font-size: 13px; color: {TEXT_SUB}; line-height: 1.5; margin-top: 10px;">{description}</p>
        </div>
    """, unsafe_allow_html=True)

def render_admin_card(title, url, accounts):
    """오션 블루 포인트가 적용된 관리자 카드"""
    st.markdown(f"""
        <div style="
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            margin-bottom: 15px;
            border-top: 4px solid {MAIN_PRIMARY};
        ">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <h5 style="margin: 0; color: {TEXT_DARK}; font-weight: 800; font-size: 16px;">{title}</h5>
                <a href="{url}" target="_blank" style="
                    text-decoration: none; 
                    font-size: 11px; 
                    color: white; 
                    background: {MAIN_GRADIENT}; 
                    padding: 4px 12px; 
                    border-radius: 20px;
                    font-weight: 600;
                ">접속하기</a>
            </div>
    """, unsafe_allow_html=True)
    
    for acc in accounts:
        st.markdown(f"<p style='color:{TEXT_SUB}; font-size:12px; margin-bottom:5px; font-weight:600;'>{acc['label']}</p>", unsafe_allow_html=True)
        st.code(f"ID: {acc['id']} / PW: {acc['pw']}", language=None)
    
    st.markdown("</div>", unsafe_allow_html=True)

def render_excel_link(title, url, description):
    """마린 블루 테마가 적용된 시트 링크 전용 카드"""
    st.markdown(f"""
        <div style="
            background: {CARD_BG};
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 18px;
            margin-bottom: 12px;
            border: 1px solid {BORDER_COLOR};
            box-shadow: 0 4px 12px rgba(0,0,0,0.03);
            display: flex;
            justify-content: space-between;
            align-items: center;
        ">
            <div style="flex: 1;">
                <h4 style="margin: 0; color: {TEXT_DARK}; font-size: 15px; font-weight: 700;">📄 {title}</h4>
                <p style="margin: 4px 0 0 0; color: {TEXT_SUB}; font-size: 12px;">{description}</p>
            </div>
            <a href="{url}" target="_blank" style="
                text-decoration: none;
                background: {MAIN_GRADIENT};
                color: white;
                padding: 7px 16px;
                border-radius: 8px;
                font-size: 12px;
                font-weight: 600;
                white-space: nowrap;
                margin-left: 15px;
                box-shadow: 0 4px 10px rgba(14, 165, 233, 0.2);
            ">시트 열기</a>
        </div>
    """, unsafe_allow_html=True)

def render_admin_card(title, url, accounts):
    """마린 블루 테마가 적용된 계정 관리 카드"""
    # 컬러 인자를 직접 받지 않고 메인 설정을 따르도록 수정
    st.markdown(f"""
        <div style="
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            margin-bottom: 20px;
            border-top: 4px solid {MAIN_PRIMARY};
        ">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <h5 style="margin: 0; color: {TEXT_DARK}; font-weight: 800; font-size: 16px;">{title}</h5>
                <a href="{url}" target="_blank" style="
                    text-decoration: none; 
                    font-size: 11px; 
                    color: white; 
                    background: {MAIN_PRIMARY}; 
                    padding: 4px 10px; 
                    border-radius: 20px;
                    font-weight: 600;
                ">접속하기</a>
            </div>
    """, unsafe_allow_html=True)
    
    for acc in accounts:
        st.markdown(f"""
            <div style="
                background: #f8f9fa;
                padding: 12px;
                border-radius: 8px;
                margin-bottom: 8px;
            ">
                <div style="font-size: 11px; color: {MAIN_PRIMARY}; font-weight: 700; margin-bottom: 4px;">{acc['label']}</div>
                <div style="display: flex; gap: 10px; font-family: 'Courier New', monospace; font-size: 13px; color: #444;">
                    <span style="opacity: 0.6;">ID:</span> <b>{acc['id']}</b>
                    <span style="opacity: 0.6; margin-left: 5px;">PW:</span> <b>{acc['pw']}</b>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    st.markdown("</div>", unsafe_allow_html=True)
def render_project_card(emoji, title, description, page_name, key):
    """클릭 시 해당 페이지 파일로 즉시 이동하는 카드"""
    st.markdown(f"""
        <div style="
            background: white;
            border-radius: 20px;
            padding: 30px 20px;
            border: 1px solid rgba(14, 165, 233, 0.1);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.02);
            text-align: center;
            height: 220px;
            margin-bottom: 10px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        ">
            <div style="font-size: 45px; margin-bottom: 15px;">{emoji}</div>
            <h3 style="margin: 0 0 10px 0; color: #0F172A; font-size: 18px; font-weight: 800;">{title}</h3>
            <p style="margin: 0; color: #64748B; font-size: 13px; line-height: 1.5;">{description}</p>
        </div>
    """, unsafe_allow_html=True)
    
    # 버튼 클릭 시 pages/폴더 내의 해당 파일로 이동
    if st.button(f"{title} 이동", key=key, use_container_width=True):
        st.switch_page(f"pages/{page_name}.py")
        
def render_footer_badge():
    """애니메이션이 포함된 하단 배너 렌더링"""
    st.markdown("""
        <div class="creator-badge">
            <div class="creator-badge-inner">
                <div style='font-size: 1.2rem; font-weight: bold;'>🚀 Powered by 호연</div>
                <div style='font-size: 0.8rem; color: #94A3B8; opacity: 0.8;'>독서화랑 운영 효율화 프로젝트 2026</div>
            </div>
        </div>
    """, unsafe_allow_html=True)        