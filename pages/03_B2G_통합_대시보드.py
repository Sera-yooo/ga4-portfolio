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
try:
    # process 대신 message_work를 가져옵니다.
    from src.tabs import main_task, school_trial, school_contract, partner, message_work
except ImportError:
    st.error("src/tabs 폴더 내의 파일들을 찾을 수 없습니다. 파일명을 확인해주세요.")

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
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🕒 오늘 할 일", 
    "🏫 학교 체험", 
    "📜 계약 학교", 
    "🤝 총판 관리", 
    "📩 안내문 생성" # 탭 이름을 용도에 맞게 변경
])

with tab1:
    main_task.render()

with tab2:
    school_trial.render()

with tab3:
    school_contract.render()

with tab4:
    partner.render()

with tab5:
    # 이 부분에서 이전에 만든 message_work.py의 내용을 불러옵니다.
    message_work.render()