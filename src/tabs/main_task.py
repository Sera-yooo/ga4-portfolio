import streamlit as st
import pandas as pd
from datetime import date
from src.data_loader import load_school_trial_data

def render():
    st.subheader("🕒 학교 코드 만들기")

    # 공통 지역 데이터
    region_map = {
        "강원": "1", "경기": "2", "경남": "3", "경북": "4", "광주": "5",
        "대구": "6", "대전": "7", "부산": "8", "서울": "9", "세종": "10",
        "울산": "11", "인천": "12", "전남": "13", "전북": "14", "제주": "15",
        "충남": "16", "충북": "17", "소울북스": "S", "대교": "DK", "독문연": "D"
    }

# 2. 🏫 신규 학교 코드 및 계정(ID) 생성기
    st.markdown("### 🏫 신규 학교 코드 및 관리자 ID 생성")
    with st.container(border=True):
        type_map = {"체험": "E", "계약": "C"}
        
        # ID 생성을 위한 영문 지역 도메인 매핑 추가
        region_domain_map = {
            "강원": "gangwon", "경기": "gyeonggi", "경남": "gyeongnam", "경북": "gyeongbuk",
            "광주": "gwangju", "대구": "daegu", "대전": "daejeon", "부산": "busan",
            "서울": "seoul", "세종": "sejong", "울산": "ulsan", "인천": "incheon",
            "전남": "jeonnam", "전북": "jeonbuk", "제주": "jeju", "충남": "chungnam",
            "충북": "chungbuk", "소울북스": "soul", "대교": "daekyo", "독문연": "dmy"
        }

        c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
        with c1:
            sel_type = st.selectbox("구분", list(type_map.keys()), key="main_sch_type")
        with c2:
            sel_region = st.selectbox("지역명", list(region_map.keys()), key="main_sch_reg")
        with c3:
            sch_init = st.text_input("학교 초성(영문)", placeholder="예: WH", key="main_sch_init").upper()
        with c4:
            sch_num = st.number_input("넘버링", min_value=1, value=1, key="main_sch_num")

        # 1. 학교 코드 조합
        res_sch_code = f"{type_map[sel_type]}{region_map[sel_region]}{sch_init}{sch_num}"
        
        # 2. 관리자 ID 조합 ([학교코드]@[영문지역명].com)
        domain = region_domain_map.get(sel_region, "dmy")
        res_sch_id = f"{res_sch_code}@{domain}.com"

        st.divider()

        # 결과 출력 (나란히 배치하여 복사하기 쉽게 구성)
        res_col1, res_col2 = st.columns(2)
        with res_col1:
            st.markdown("**📌 생성된 학교 코드**")
            st.code(res_sch_code, language="plaintext")
        with res_col2:
            st.markdown("**📌 생성된 관리자 ID (체험교사계정)**")
            st.code(res_sch_id, language="plaintext")

        # 규칙 설명 추가
        res_col3, res_col4 = st.columns(2)
        with res_col3:
            st.caption(f"💡 코드 규칙: {sel_type}({type_map[sel_type]}) + {sel_region}({region_map[sel_region]}) + {sch_init if sch_init else '(초성)'} + {sch_num}")
        with res_col4:
            st.caption(f"💡 계정 규칙: [학교코드]@{domain}.com")

    # 3. 🤝 신규 총판(CP) 코드 생성기
    st.markdown("### 🤝 신규 총판(CP) 코드 생성")
    with st.container(border=True):
        cp_c1, cp_c2, = st.columns(2)
        with cp_c1:
            sel_cp_region = st.selectbox("지역 선택", list(region_map.keys()), key="main_cp_reg")
        with cp_c2:
            cp_num = st.number_input("넘버링(1~99)", min_value=1, max_value=99, value=1, key="main_cp_num")
    
        res_cp_code = f"{region_map[sel_cp_region]}CP{cp_num:02d}"
        st.write("생성된 총판 코드")
        st.code(res_cp_code, language=None)
        # 규칙 설명 추가
        st.caption(f"💡 규칙: {sel_cp_region}({region_map[sel_cp_region]}) + CP + {cp_num:02d}")