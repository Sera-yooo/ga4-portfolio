import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import src.style_utils as style

# 1. 페이지 및 테마 설정
st.set_page_config(page_title="Morning Hub", layout="wide")
style.apply_common_style()
style.apply_morning_hub_style()

# 파일 경로를 pages 폴더 안으로 설정
FILE_PATH = 'pages/morning_log.csv'

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
    # 데이터 리스트를 다시 CSV 형식으로 변환하여 저장
    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        for t in tasks:
            line = f"{t['date']},{t['content']},{t['time']},{t['status']},{t['reg_date']},{t['reg_time']}\n"
            f.write(line)

def get_date_options():
    days = ['월', '화', '수', '목', '금', '토', '일']
    options = []
    for i in range(-3, 10): # 과거 3일부터 미래 10일까지
        d = datetime.now() + timedelta(days=i)
        label = d.strftime(f"%Y-%m-%d ({days[d.weekday()]})")
        options.append((d.strftime("%Y-%m-%d"), label))
    return options

# 세션 상태 초기화
if "emergency_tasks" not in st.session_state:
    st.session_state.emergency_tasks = load_data()
if "routine_done" not in st.session_state:
    st.session_state.routine_done = [False] * 5

# --- 레이아웃 ---
st.title("☀️ 업무 관제 센터")

tab_main, tab_cs = st.tabs(["📊 업무 루틴 & 메모 로그", "🏫 CS & 상시 업무"])

with tab_main:
    col_left, col_right = st.columns([1, 1.5], gap="large")

    with col_left:
        st.subheader("⚡ 업무 등록")
        
        with st.container(border=True):
            # 2. 변수 정의 위치: 버튼보다 위에 있어야 노란색 불이 사라집니다.
            task_input = st.text_area("무슨 일을 해야 하나요?", placeholder="예: 북원초 답변 메일 보내기")
            
            time_options = ["오전 10:00", "오전 11:00", "오후 02:00", "오후 04:00"]
            selected_time = st.radio("리마인드 시간", time_options, horizontal=True)

            # 3. 버튼 클릭 시점 로직 (여기가 사용자님이 질문하신 위치입니다)
            if st.button("📌 저장하기", type="primary"):
                if not task_input.strip():
                    st.warning("내용을 입력해주세요.")
                else:
                    now = datetime.utcnow() + timedelta(hours=9)
                    days = ['월', '화', '수', '목', '금', '토', '일']
                    weekday = days[now.weekday()]
                    
                    new_task = {
                        "date": now.strftime("%Y-%m-%d"), # 필터링 기준 날짜
                        "content": task_input,
                        "time": selected_time,
                        "status": "진행중",
                        "reg_date": now.strftime("%Y-%m-%d"),
                        "reg_time": now.strftime(f"%H:%M ({weekday})"),
                    }
                    
                    # 데이터 저장 및 리프레시
                    st.session_state.emergency_tasks.append(new_task)
                    save_data(st.session_state.emergency_tasks)
                    st.rerun()

with col_right:
    # --- [조회 영역] ---
    with col_right:
        st.subheader("📝 업무 히스토리")

        # 1. 날짜 선택
        selected_date = st.date_input("🗓️ 날짜 선택", value=datetime.now())

        # 2. 형식을 '2026-04-15'로 고정 (CSV 저장 형식과 일치)
        target_date_str = selected_date.strftime("%Y-%m-%d")

        # 3. 데이터 로드 (함수가 리스트를 반환하는지 확인)
        st.session_state.emergency_tasks = load_data()

        # 4. 필터링 (t['date']가 위에 load_data의 키와 정확히 같은지 확인)
        filtered_tasks = [
            (idx, t) for idx, t in enumerate(st.session_state.emergency_tasks) 
            if t.get('date') == target_date_str
        ]

    # 디버깅용 (데이터가 들어오는지 확인하고 싶다면 아래 주석 해제)
    # st.write(f"조회 대상: {target_date_str}")
    # st.write(f"전체 데이터 개수: {len(st.session_state.emergency_tasks)}")
    # 5. 화면 렌더링
    if not filtered_tasks:
        st.info(f"📅 {target_date_str}에는 등록된 업무가 없습니다.")
    else:
# --- [조회 영역 내 카드 렌더링 부분] ---
        for real_idx, task in reversed(filtered_tasks):
            is_done = task['status'] == "완료"
            
            with st.container(border=True):                        
                # 헤더 (시간 정보)
                c1, c2 = st.columns([1, 1])
                c1.markdown(f"**{'✅' if is_done else '⏳'} {task['time']}**")
                c2.markdown(f"<div style='text-align:right; font-size:11px; color:gray;'>기록: {task['reg_time']}</div>", unsafe_allow_html=True)
                
                # 본문
                content_style = "text-decoration: line-through; color: #adb5bd;" if is_done else ""
                st.markdown(f"<div style='margin:10px 0; {content_style}'>{task['content']}</div>", unsafe_allow_html=True)

                # 버튼 영역
                btn_col1, btn_col2, _ = st.columns([1, 1, 3])
                
                with btn_col1:
                    button_label = "복구" if is_done else "완료"
                    # key값에 real_idx를 사용하여 고유성 유지
                    if st.button(button_label, key=f"btn_status_{real_idx}"):
                        # 1. 세션 상태 업데이트
                        new_status = "진행중" if is_done else "완료"
                        st.session_state.emergency_tasks[real_idx]['status'] = new_status
                        # 2. 파일에 즉시 저장
                        save_data(st.session_state.emergency_tasks)
                        # 3. 화면 새로고침
                        st.rerun()

                with btn_col2:
                    if st.button("삭제", key=f"btn_del_{real_idx}"):
                        # 1. 세션 상태에서 해당 인덱스 삭제
                        st.session_state.emergency_tasks.pop(real_idx)
                        # 2. 파일에 즉시 저장
                        save_data(st.session_state.emergency_tasks)
                        # 3. 화면 새로고침
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