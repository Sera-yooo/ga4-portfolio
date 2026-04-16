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
        try:
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
        except Exception as e:
            st.error(f"파일 로드 오류: {e}")
    return tasks

def save_data(tasks):
    """전체 리스트를 파일에 저장 (완료/삭제 시 사용)"""
    if not os.path.exists('pages'):
        os.makedirs('pages')
    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        for t in tasks:
            clean_content = t['content'].replace(',', ' ')
            line = f"{t['date']},{clean_content},{t['time']},{t['status']},{t['reg_date']},{t['reg_time']}\n"
            f.write(line)

def append_data(task):
    """새로운 업무 하나만 끝에 추가 (등록 시 사용 - 덮어쓰기 방지)"""
    if not os.path.exists('pages'):
        os.makedirs('pages')
    with open(FILE_PATH, 'a', encoding='utf-8') as f:
        clean_content = task['content'].replace(',', ' ')
        line = f"{task['date']},{clean_content},{task['time']},{task['status']},{task['reg_date']},{task['reg_time']}\n"
        f.write(line)

# 세션 상태 초기화
if "emergency_tasks" not in st.session_state:
    st.session_state.emergency_tasks = load_data()
if "routine_done" not in st.session_state:
    st.session_state.routine_done = [False] * 5
if "editing_idx" not in st.session_state:
    st.session_state.editing_idx = None
if st.session_state.editing_idx is not None:
    # 현재 수정하려는 데이터 가져오기
    if "emergency_tasks" in st.session_state:
        task_to_edit = st.session_state.emergency_tasks[st.session_state.editing_idx]
        st.session_state["task_input_area"] = task_to_edit['content']    

# 1. 페이지 제목 및 기본 설정
st.title("☀️ 업무 관제 센터")

# 2. [핵심] 날짜 선택기를 상단으로 이동 (여기서 변수가 정의되어야 아래에서 쓸 수 있음)
# 모든 탭과 컬럼에서 공통으로 사용할 날짜입니다.
selected_date = st.date_input("🗓️ 조회 및 등록 날짜 선택", value=datetime.now())
target_date_str = selected_date.strftime("%Y-%m-%d")

# 3. 탭 구성
tab_main, tab_cs = st.tabs(["📊 업무 루틴 & 메모 로그", "🏫 CS & 상시 업무"])

with tab_main:
    col_left, col_right = st.columns([1, 1.5], gap="large")

    # --- 왼쪽: 업무 등록 영역 ---
    with col_left:
        edit_idx = st.session_state.get("editing_idx", None)
        st.subheader("⚡ 업무 " + ("수정" if edit_idx is not None else "등록"))
        
        with st.container(border=True):
            # [핵심] 수정 모드일 때와 아닐 때의 key를 다르게 줍니다.
            # 이렇게 하면 Streamlit이 위젯 충돌 에러를 내지 않습니다.
            if edit_idx is not None:
                task_to_edit = st.session_state.emergency_tasks[edit_idx]
                task_input = st.text_area("무슨 일을 해야 하나요?", 
                                        value=task_to_edit['content'], # 수정할 내용 주입
                                        key=f"edit_area_{edit_idx}") # 유니크한 키값
            else:
                task_input = st.text_area("무슨 일을 해야 하나요?", 
                                        value="", # 등록 모드일 땐 비우기
                                        key="register_area")
            
            # [변경] 시간 라디오 버튼도 수정 시 기존 시간으로 인덱스 맞추기
            time_options = ["오전 10:00","오전 11:00", "오전 12:00", "오후 02:00", "오후 03:00","오후 04:00","오후 05:00","오후 06:00"]
            curr_time_idx = 0
            if edit_idx is not None:
                try:
                    curr_time_idx = time_options.index(st.session_state.emergency_tasks[edit_idx]['time'])
                except:
                    curr_time_idx = 0

            selected_time = st.radio("리마인드 시간", time_options, index=curr_time_idx, horizontal=True)

            if edit_idx is not None:
                col_btn1, col_btn2 = st.columns(2)
                if col_btn1.button("✅ 수정 완료", type="primary", use_container_width=True):
                    if not task_input.strip():
                        st.warning("내용을 입력해주세요.")
                    else:
                        # 데이터 업데이트
                        st.session_state.emergency_tasks[edit_idx]['content'] = task_input.strip()
                        st.session_state.emergency_tasks[edit_idx]['time'] = selected_time
                        save_data(st.session_state.emergency_tasks)
                        
                        # [변경] 수정 완료 후 입력창 비우기
                        st.session_state.editing_idx = None
                        st.session_state["task_input_area"] = "" 
                        st.success("수정되었습니다!")
                        st.rerun()
                
                if col_btn2.button("❌ 취소", use_container_width=True):
                    st.session_state.editing_idx = None
                    # [변경] 취소 시에도 입력창 비우기
                    st.session_state["task_input_area"] = ""
                    st.rerun()
            
            else:
                if st.button("📌 저장하기", type="primary", use_container_width=True):
                    if not task_input.strip():
                        st.warning("내용을 입력해주세요.")
                    else:
                        now = datetime.utcnow() + timedelta(hours=9)
                        days = ['월', '화', '수', '목', '금', '토', '일']
                        weekday = days[now.weekday()]
                        save_date_str = selected_date.strftime("%Y-%m-%d")
                        
                        new_task = {
                            "date": save_date_str,
                            "content": task_input.strip(),
                            "time": selected_time,
                            "status": "진행중",
                            "reg_date": now.strftime("%Y-%m-%d"),
                            "reg_time": now.strftime(f"%H:%M ({weekday})"),
                        }
                        
                        append_data(new_task)
                        # [변경] 등록 후에도 입력창 비우기
                        st.session_state["task_input_area"] = ""
                        st.session_state.emergency_tasks = load_data()
                        st.rerun()

    # --- 오른쪽: 조회 및 히스토리 영역 ---
    with col_right:        
        if "emergency_tasks" not in st.session_state:
            st.session_state.emergency_tasks = load_data()
            
        filtered_tasks = [
            (idx, t) for idx, t in enumerate(st.session_state.emergency_tasks) 
            if t.get('date') == target_date_str
        ]

        # 3. 화면 렌더링
        if not filtered_tasks:
            st.info(f"📅 {target_date_str}에는 등록된 업무가 없습니다.")
        else:
            # 최신순 정렬 (reversed)
            for real_idx, task in reversed(filtered_tasks):
                is_done = task['status'] == "완료"
                
                with st.container(border=True):                        
                    # 헤더 영역
                    header_col1, header_col2 = st.columns([1, 1])
                    header_col1.markdown(f"**{'✅' if is_done else '⏳'} {task['time']}**")
                    header_col2.markdown(
                        f"<div style='text-align:right; font-size:11px; color:gray;'>기록: {task['reg_time']}</div>", 
                        unsafe_allow_html=True
                    )
                    
                    # 본문 영역
                    content_style = "text-decoration: line-through; color: #adb5bd;" if is_done else ""
                    st.markdown(
                        f"<div style='margin:10px 0; {content_style}'>{task['content']}</div>", 
                        unsafe_allow_html=True
                    )

                    # 조작 버튼 영역
                    btn_col1, btn_col2, btn_col3, _ = st.columns([1, 1, 1, 2.5])
                    
                    with btn_col1:
                        label = "복구" if is_done else "완료"
                        if st.button(label, key=f"btn_status_{real_idx}"):
                            # 세션 데이터 수정
                            st.session_state.emergency_tasks[real_idx]['status'] = "진행중" if is_done else "완료"
                            # 파일 저장 및 반영
                            save_data(st.session_state.emergency_tasks)
                            st.rerun()

                    with btn_col2:
                        if st.button("삭제", key=f"btn_del_{real_idx}"):
                            # 데이터 삭제
                            st.session_state.emergency_tasks.pop(real_idx)
                            save_data(st.session_state.emergency_tasks)
                            st.rerun()
                    with btn_col3:
                        if st.button("✏️", key=f"edit_{real_idx}"):
                            st.session_state.editing_idx = real_idx
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