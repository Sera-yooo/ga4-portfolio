import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import src.style_utils as style

# 1. 페이지 및 테마 설정
st.set_page_config(page_title="Morning Hub", layout="wide")

# 스타일 적용 (함수가 존재할 때만 실행되도록 안전하게 호출)
try:
    style.apply_common_style()
    style.apply_morning_hub_style()
except AttributeError:
    st.error("스타일 함수를 찾을 수 없습니다. src/style_utils.py 파일을 확인해주세요.")

# 파일 경로 설정 (pages 폴더 내부)
FILE_PATH = 'pages/morning_log.csv'

# --- [데이터 로직 함수] ---
def load_data():
    tasks = []
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split(',')
                if len(parts) >= 6:
                    tasks.append({
                        "date": parts[0].strip(),
                        "content": parts[1].strip(),
                        "time": parts[2].strip(),
                        "status": parts[3].strip(),
                        "reg_date": parts[4].strip(),
                        "reg_time": parts[5].strip()
                    })
    return tasks

def save_data(tasks):
    # 폴더가 없을 경우를 대비해 pages 폴더가 있는지 체크 (선택 사항)
    if not os.path.exists('pages'):
        os.makedirs('pages')
        
    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        for t in tasks:
            # 각 항목을 쉼표로 연결하되, 데이터에 쉼표가 있을 경우를 대비해 공백 제거(strip)
            line = f"{t['date']},{t['content'].replace(',', ' ')},{t['time']},{t['status']},{t['reg_date']},{t['reg_time']}\n"
            f.write(line)

# 세션 상태 초기화
if "emergency_tasks" not in st.session_state:
    st.session_state.emergency_tasks = load_data()
if "routine_done" not in st.session_state:
    st.session_state.routine_done = [False] * 5

# --- [UI 레이아웃] ---
st.title("☀️ 업무 관제 센터")

tab_main, tab_cs = st.tabs(["📊 업무 루틴 & 메모 로그", "🏫 CS & 상시 업무"])

with tab_main:
    col_left, col_right = st.columns([1, 1.5], gap="large")

    # --- 왼쪽: 업무 등록 영역 ---
    with col_left:
        st.subheader("⚡ 업무 등록")
        
        with st.container(border=True):
            task_input = st.text_area("무슨 일을 해야 하나요?", placeholder="예: 북원초 답변 메일 보내기")
            
            time_options = ["오전 10:00","오전 11:00", "오전 12:00", "오후 02:00", "오후 03:00","오후 04:00","오후 05:00","오후 06:00"]
            selected_time = st.radio("리마인드 시간", time_options, horizontal=True)

            if st.button("📌 저장하기", type="primary"):
                if not task_input.strip():
                    st.warning("내용을 입력해주세요.")
                else:
                    # 한국 시간 계산
                    now = datetime.utcnow() + timedelta(hours=9)
                    days = ['월', '화', '수', '목', '금', '토', '일']
                    weekday = days[now.weekday()]
                    
                    new_task = {
                        "date": now.strftime("%Y-%m-%d"),
                        "content": task_input.strip(),
                        "time": selected_time,
                        "status": "진행중",
                        "reg_date": now.strftime("%Y-%m-%d"),
                        "reg_time": now.strftime(f"%H:%M ({weekday})"),
                    }
                    
                    # [중요] 1. 먼저 파일에서 최신 데이터를 읽어온 뒤 추가 (데이터 유실 방지)
                    current_tasks = load_data()
                    current_tasks.append(new_task)
                    
                    # [중요] 2. 세션과 파일에 동시에 업데이트
                    st.session_state.emergency_tasks = current_tasks
                    save_data(current_tasks)
                    
                    st.success("업무가 등록되었습니다!")
                    st.rerun() # 화면을 즉시 새로고침해서 반영

    # --- 오른쪽: 조회 및 히스토리 영역 ---
    with col_right:
        st.subheader("📝 업무 히스토리")

        # 1. 날짜 선택 및 필터링
        selected_date = st.date_input("🗓️ 날짜 선택", value=datetime.now())
        target_date_str = selected_date.strftime("%Y-%m-%d")

        # 실시간 데이터 동기화
        st.session_state.emergency_tasks = load_data()

        filtered_tasks = [
            (idx, t) for idx, t in enumerate(st.session_state.emergency_tasks) 
            if t.get('date') == target_date_str
        ]

        # 2. 화면 렌더링
        if not filtered_tasks:
            st.info(f"📅 {target_date_str}에는 등록된 업무가 없습니다.")
        else:
            for real_idx, task in reversed(filtered_tasks):
                is_done = task['status'] == "완료"
                
                with st.container(border=True):                        
                    # 헤더
                    c1, c2 = st.columns([1, 1])
                    c1.markdown(f"**{'✅' if is_done else '⏳'} {task['time']}**")
                    c2.markdown(f"<div style='text-align:right; font-size:11px; color:gray;'>기록: {task['reg_time']}</div>", unsafe_allow_html=True)
                    
                    # 본문
                    content_style = "text-decoration: line-through; color: #adb5bd;" if is_done else ""
                    st.markdown(f"<div style='margin:10px 0; {content_style}'>{task['content']}</div>", unsafe_allow_html=True)

                    # 조작 버튼
                    btn_col1, btn_col2, _ = st.columns([1, 1, 3])
                    
                    with btn_col1:
                        if st.button("복구" if is_done else "완료", key=f"btn_status_{real_idx}"):
                            new_status = "진행중" if is_done else "완료"
                            st.session_state.emergency_tasks[real_idx]['status'] = new_status
                            save_data(st.session_state.emergency_tasks)
                            st.rerun()

                    with btn_col2:
                        if st.button("삭제", key=f"btn_del_{real_idx}"):
                            st.session_state.emergency_tasks.pop(real_idx)
                            save_data(st.session_state.emergency_tasks)
                            st.rerun()

# --- Tab 2: CS & 상시 업무 ---
with tab_cs:
    st.subheader("🏫 학교 관리 및 CS")
    c1, c2 = st.columns(2)
    
    with c1:
        with st.container(border=True):
            st.markdown("**🏫 독서화랑 클래스**")
            st.code("ID: schooladm / PW: schoolpass")
            st.link_button("🔗 학교 체험 계정 생성", "https://school.dmy.co.kr/zSchoolAdm/?p=129&sitesession=hjhekmlsamjk3su1m99v51dsf6", use_container_width=True)
            st.link_button("📊 계약 학교 엑셀(B2G)", "https://docs.google.com/spreadsheets/d/1nmAhwBLloq6pFGFIWYahKh4vPQaw08xugCWHURJ076c/edit?gid=414849783#gid=414849783", use_container_width=True)

    with c2:
        with st.container(border=True):
            st.markdown("**📖 독서화랑 (재원생)**")
            st.write("실장님 협조 업무 및 일반 CS")
            st.link_button("📂 CS 처리 기록 시트", "https://docs.google.com/spreadsheets/d/1HbOG1FE2sAonh_xHsxHHJIiFGV0fdteY/edit?gid=698947679#gid=698947679", use_container_width=True)