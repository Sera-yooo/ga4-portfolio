import streamlit as st
from datetime import datetime

# 1. 분리된 탭 파일들 불러오기
# (src/tabs/ 폴더 안에 해당 파일들이 있어야 합니다)
try:
    from src.tabs import main_task, school_trial, school_contract, partner, process
except ImportError:
    st.error("src/tabs 폴더 내의 파일들을 찾을 수 없습니다. 파일명을 확인해주세요.")

# 페이지 설정 (전체 화면 넓게 사용)
st.set_page_config(page_title="독서화랑 B2G 통합 대시보드", layout="wide")

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
    if st.button("🔄 데이터 새로고침"):
        st.cache_data.clear()
        st.rerun()

# --- [메인 탭 구성] ---
# 5개의 탭 생성
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🕒 오늘 할 일", 
    "🏫 학교 체험", 
    "📜 계약 학교", 
    "🤝 총판 관리", 
    "📩 프로세스"
])

# 각 탭에 들어갈 내용 호출 (각 파일의 render() 함수 실행)
with tab1:
    main_task.render()

with tab2:
    school_trial.render()

with tab3:
    school_contract.render()

with tab4:
    partner.render()

with tab5:
    process.render()