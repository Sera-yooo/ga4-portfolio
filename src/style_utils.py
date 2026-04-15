import streamlit as st

# ==========================================
# [중요] 테마 통합 색상 정의
# ==========================================
MAIN_PRIMARY = "#0EA5E9"
MAIN_GRADIENT = "linear-gradient(135deg, #0EA5E9 0%, #2563EB 100%)"
LIGHT_BG = "#FFFFFF"
SIDEBAR_BG = "#F8FAFC"
CARD_BG = "rgba(255, 255, 255, 0.9)"
BORDER_COLOR = "rgba(14, 165, 233, 0.15)"
TEXT_DARK = "#0F172A"
TEXT_SUB = "#64748B"

def apply_common_style():
    st.markdown(f"""
        <style>
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

        /* 1. 전체 기본 폰트 및 배경색 */
        html, body, [class*="css"] {{
            font-family: 'Pretendard', sans-serif;
            color: {TEXT_DARK};
        }}
        
        .stApp {{
            background-color: {LIGHT_BG};
        }}

        /* 2. 사이드바 디자인 */
        [data-testid="stSidebar"] {{
            background-color: {SIDEBAR_BG} !important;
            border-right: 1px solid #E2E8F0;
        }}

        /* 3. 기본 버튼 (메인 페이지 전용 커다란 카드 버튼) */
        /* 메인 페이지의 '이동' 버튼 등에만 적용되도록 범위를 좁힙니다 */
        div.stButton > button {{
            border-radius: 12px !important;
            transition: all 0.3s ease !important;
            font-weight: 600 !important;
        }}

        /* 4. 탭 디자인 */
        .stTabs [data-baseweb="tab"] {{
            background-color: #F1F5F9;
            border-radius: 10px;
            padding: 8px 16px;
            color: {TEXT_SUB};
            border: none !important;
        }}

        .stTabs [data-baseweb="tab"][aria-selected="true"] {{
            background: {MAIN_GRADIENT};
            color: white !important;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
        }}

        /* 5. 애니메이션 배지 */
        .creator-badge {{
            background: #0F172A; color: #F1F5F9; padding: 24px; border-radius: 24px;
            text-align: center; margin-top: 50px; position: relative; overflow: hidden;
        }}
        @keyframes rotate {{ 100% {{ transform: rotate(360deg); }} }}
        </style>
    """, unsafe_allow_html=True)

def apply_morning_hub_style():
    st.markdown(f"""
        <style>
            /* 1. 카드 컨테이너 스타일 (st.container용) */
            div[data-testid="stVerticalBlockBorderWrapper"] {{
                margin-bottom: 0px !important;
            }}
            
            /* 카드 내부의 컬럼 간격 조정 */
            div[data-testid="stHorizontalBlock"] {{
                gap: 0.5rem !important;
            }}

            /* 2. 카드 전용 버튼 (더 작고 파랗게) */
            /* 특정 키워드를 포함하는 버튼만 타겟팅하거나 모든 컬럼 내 버튼 타겟팅 */
            div[data-testid="stColumn"] button {{
                min-height: 30px !important;
                height: 30px !important;
                width: 100% !important; /* 컬럼 너비에 맞춤 */
                font-size: 12px !important;
                border-radius: 8px !important;
                background-color: #f0f9ff !important; /* 아주 연한 파랑 */
                border: 1px solid #e0f2fe !important;
                color: #0ea5e9 !important;
                padding: 0 !important;
            }}

            div[data-testid="stColumn"] button:hover {{
                background-color: #0ea5e9 !important;
                color: white !important;
                border: none !important;
            }}

            /* 3. 완료 텍스트 (취소선) */
            .done-text {{
                text-decoration: line-through !important;
                color: #94a3b8 !important;
                opacity: 0.6;
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

def apply_morning_hub_style():
    st.markdown("""
        <style>
            /* 1. 박제하기 버튼 - 파란색 강조 */
            div.stButton > button[kind="primary"] {
                background-color: #007bff !important;
                color: white !important;
                border: none !important;
                height: 40px !important;
                font-weight: bold !important;
            }

            /* 2. 카드 내부 버튼 스타일 */
            .task-card div.stButton > button {
                width: 50px !important;
                height: 25px !important;
                font-size: 11px !important;
                padding: 0px !important;
                background-color: #f0f4f8 !important;
                color: #555 !important;
                border: 1px solid #dce3eb !important;
            }
            
            /* 3. 완료된 항목 스타일 */
            .done-text {
                text-decoration: line-through !important;
                color: #a0a0a0 !important;
            }
            
            /* 4. 카드 디자인 보완 */
            .task-card {
                background-color: #ffffff;
                border: 1px solid #eef2f8;
                border-radius: 12px;
                padding: 12px 15px;
                margin-bottom: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.03);
            }
        </style>
    """, unsafe_allow_html=True)