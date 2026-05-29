import streamlit as st
from datetime import datetime

# ==========================================
# 1. 페이지 및 테마 설정 (최상단에 위치)
# ==========================================
import src.style_utils as style

# 1. 페이지 설정
st.set_page_config(page_title="독서화랑 팀 통합 리소스", layout="wide")
style.apply_common_style()

# 2. 분리된 탭 파일들 불러오기
from src.tabs import (
    main_task,
    message_work, 
    school_trial, 
    school_contract, 
    partner, 
    mail_Templates,
    school_trial_input 
)

# --- [공통 헤더 영역] ---
st.title("📚 독서화랑 B2G 통합 관리 시스템")
st.caption(f"접속 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# --- [사이드바 바로가기 구성] ---
with st.sidebar:
    st.header("🔗 빠른 연결")
    st.link_button("🌐 독서화랑 클래스", "https://school.dmy.co.kr/")
    st.link_button("⚙️ 클래스 관리자(Adm)", "https://school.dmy.co.kr/zSchoolAdm/login.php")
    st.divider()
    
    st.subheader("📝 원본 시트 수정")
    st.markdown("[학교 체험/계약 시트](https://docs.google.com/spreadsheets/d/1nmAhwBLloq6pFGFIWYahKh4vPQaw08xugCWHURJ076c/)")
    st.markdown("[메일/명단 프로세스](https://docs.google.com/spreadsheets/d/1RUKAv5IqgcIv-2-H8sU5JVrusMfGwjpHswU55kg8k30/)")
    st.markdown("[총판 관리 시트](https://docs.google.com/spreadsheets/d/1ZL3p5WKL_c0h5DAbLoFgULx6_n3boF5M27nuKdMPrhM/)")
    
    st.divider()
    if st.button("🔄 데이터 새로고침", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# --- [메인 탭 구성] ---
tabs = st.tabs([
    "➕ 체험 학교 등록" ,    
    "🏫 학교 체험", 
    "📜 계약 학교", 
    "🤝 총판 관리", 
    "📩 안내문 생성",
    "✉️ 표준 문구(Mail)",
    "🕒 코드 생성기"    
])

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = tabs

with tab1:
    school_trial_input.render()

with tab2:
    school_trial.render()

with tab3:
    school_contract.render()

with tab4:
    partner.render()

with tab5:    
    message_work.render()
with tab6:    
    mail_Templates.render()
with tab7:    
    main_task.render()