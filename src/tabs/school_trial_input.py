import streamlit as st
import pandas as pd
import re
from datetime import date, timedelta
from src.data_loader import load_school_trial_data, append_new_school_data

def format_phone_number(phone):
    """전화번호를 010-0000-0000 형식으로 변환"""
    digits = re.sub(r'\D', '', phone)
    if len(digits) == 11:
        return f"{digits[:3]}-{digits[3:7]}-{digits[7:]}"
    elif len(digits) == 10:
        if digits.startswith('02'):
            return f"{digits[:2]}-{digits[2:6]}-{digits[6:]}"
        else:
            return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
    return phone

def render():
    st.subheader("➕ 신규 체험 학교 등록 시스템")
    
    # 1. 데이터 로드 및 순번 계산
    df = load_school_trial_data()
    if not df.empty:
        try:
            last_no = pd.to_numeric(df['순번'], errors='coerce').max()
            next_no = int(last_no + 1) if pd.notna(last_no) else len(df) + 1
        except:
            next_no = len(df) + 1
    else:
        next_no = 1

    # 매핑 데이터
    type_map = {"계약": "C", "체험": "E"}
    region_info = {
        "강원": ["gangwon", "1"], "경기": ["gyeonggi", "2"], "경남": ["gyeongnam", "3"],
        "경북": ["gyeongbuk", "4"], "광주": ["gwangju", "5"], "대구": ["daegu", "6"],
        "대전": ["daejeon", "7"], "부산": ["busan", "8"], "서울": ["seoul", "9"],
        "세종": ["sejong", "10"], "울산": ["ulsan", "11"], "인천": ["incheon", "12"],
        "전남": ["jeonnam", "13"], "전북": ["jeonbuk", "14"], "제주": ["jeju", "15"],
        "충남": ["chungnam", "16"], "충북": ["chungbuk", "17"],
        "소울북스": ["soul", "S"], "대교": ["daekyo", "DK"], "독문연": ["dmy", "D"]
    }

    # [중요] 날짜 실시간 연동을 위해 폼 외부에서 먼저 입력받음
    st.markdown("##### 📅 1. 일정 설정 (종료일 자동 계산)")
    date_col1, date_col2 = st.columns(2)
    with date_col1:
        start_date = st.date_input("체험 시작일", value=date.today())
    with date_col2:
        # 시작일을 바꾸면 종료일이 즉시 30일 뒤로 업데이트됨
        default_end_date = start_date + timedelta(days=30)
        end_date = st.date_input("체험 종료일", value=default_end_date)

    # 나머지 정보는 폼으로 묶어서 입력
    with st.form("new_school_form", clear_on_submit=True):
        st.markdown(f"#### 📋 2. 학교 및 코드 정보 (순번: {next_no})")
        
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            type_options = list(type_map.keys())
            sel_type = st.selectbox("구분", type_options, index=type_options.index("체험"))
        with col2:
            sel_region = st.selectbox("지역 선택", list(region_info.keys()))
        with col3:
            region2 = st.text_input("상세 지역명 (C열)", placeholder="예: 성남시 분당구")

        st.divider()

        # 학교 및 담당자 정보
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            school_name = st.text_input("학교명 (필수)")
        with c2:
            teacher_name = st.text_input("담당 교사명 (필수)")
        with c3:
            school_phone = st.text_input("학교연락처 (F열)", placeholder="숫자만 입력")
        with c4:
            teacher_phone = st.text_input("연락처 (E열)", placeholder="숫자만 입력")

        c5, c6, c7 = st.columns(3)
        with c5:
            teacher_email = st.text_input("이메일 (H열)")
        with c6:
            # H열: 유입경로 드롭박스 (기본값 빈칸)
            inflow_options = ["미분류", "총판소개", "직접유입"]
            inflow_path = st.selectbox("유입 경로 (I열)", inflow_options, index=inflow_options.index("미분류"))
        with c7:
            process_options = ["신청", "진행중", "종료"]
            process_status = st.selectbox("진행 여부 (S열)", process_options, index=process_options.index("진행중"))

        st.divider()

        # 코드 생성 관련 입력
        cc1, cc2 = st.columns(2)
        with cc1:
            sch_init = st.text_input("학교 영문 초성 (T열)", placeholder="예: WH").upper()
        with cc2:
            sch_num = st.number_input("넘버링 (T열)", min_value=1, value=1)

        # 코드 조합 로직
        type_code = type_map[sel_type]
        reg_domain = region_info[sel_region][0]
        reg_num = region_info[sel_region][1]
        res_sch_code = f"{type_code}{reg_num}{sch_init}{sch_num}"
        res_sch_id = f"{res_sch_code}@{reg_domain}.com"

        st.info(f"✨ **생성 코드:** {res_sch_code}  |  📧 **생성 계정:** {res_sch_id}")

        submit_btn = st.form_submit_button("🚀 구글 시트에 신규 등록", use_container_width=True)

    # 4. 데이터 전송 로직
    if submit_btn:
        if not school_name or not teacher_name or not sch_init:
            st.error("❌ 학교명, 담당자명, 영문 초성은 필수 입력 사항입니다.")
        else:
            formatted_phone = format_phone_number(teacher_phone) if teacher_phone else ""
            school_formatted_phone = format_phone_number(school_phone) if school_phone else ""
            
            # 시트 구조 A(0) ~ Z(25) ...
            new_row = [""] * 30 
            new_row[0] = next_no            # A: 순번
            new_row[1] = sel_region         # B: 지역1
            new_row[2] = region2            # C: 지역2
            new_row[3] = school_name        # D: 학교명
            new_row[4] = school_formatted_phone    # E: 학교연락처
            new_row[5] = teacher_name       # F: 교사명            
            new_row[6] = formatted_phone    # G: 연락처
            new_row[7] = teacher_email      # H: 이메일
            new_row[8] = inflow_path        # I: 유입경로 (선택값)
            
            new_row[15] = "부"               # P: 진행상태 (고정값)
            new_row[18] = process_status    # S: 진행여부
            new_row[19] = res_sch_code      # T: 학교코드
            new_row[20] = res_sch_id        # U: 체험교사계정
            new_row[21] = str(start_date)   # V: 시작일
            new_row[22] = str(end_date)     # W: 종료일
            new_row[23] = "부"               # X: 출력여부 (고정값)
            new_row[26] = "부"               # AA: 계약여부 (고정값)
            
            with st.spinner("구글 시트에 데이터를 기록 중..."):
                if append_new_school_data(new_row):
                    st.success(f"✅ {next_no}번 {school_name} 등록 성공!")
                    # st.balloons()
                    # st.cache_data.clear()