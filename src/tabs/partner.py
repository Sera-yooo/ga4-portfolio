import streamlit as st
import pandas as pd
from datetime import date
from src.data_loader import load_cp_trial_data

def render():
    # 퀵 링크
    c1, c2 = st.columns([3, 1]) # 비율을 조정해 버튼을 우측으로 밀었습니다.
    with c1:
        st.subheader("🤝 총판별 체험 계정 관리 (Live)")
    with c2:
        st.link_button("📂 구글 시트 원본 열기", "https://docs.google.com/spreadsheets/d/1ZL3p5WKL_c0h5DAbLoFgULx6_n3boF5M27nuKdMPrhM/edit?gid=0#gid=0", use_container_width=True)
    
    df = load_cp_trial_data()
    if df.empty:
        st.info("데이터를 불러오는 중입니다...")
        return
    
    # 최신 데이터 상단 배치
    df = df.iloc[::-1].reset_index(drop=True)

    # 1. 실시간 체험 상태 로직 (변수명 통일: 실시간상태)
    today = date.today()
    def check_cp_status(end_date_str):
        try:
            if not end_date_str or end_date_str in ['-', '']: return "확인필요"
            # 날짜 형식 정제 (. 제거)
            clean_date = str(end_date_str).replace('.', '-')
            end_dt = pd.to_datetime(clean_date).date()
            diff = (end_dt - today).days
            if diff < 0: return "❌ 종료"
            elif diff <= 7: return f"⚠️ 임박(D-{diff})"
            else: return "✅ 체험중"
        except: return "날짜형식오류"

    # ✨ 컬럼명을 '실시간상태'로 생성하여 아래 final_cols와 일치시킴
    df['실시간상태'] = df['체험종료일'].apply(check_cp_status)

    # 2. 상단 요약
    cp_summary = df.groupby('총판명').size().reset_index(name='관리학교수')
    st.write(f"📊 현재 **{len(cp_summary)}**개 총판이 **{len(df)}**개 학교를 관리 중입니다.")

    # 3. 검색 및 필터
    col1, col2 = st.columns(2)
    with col1:
        # fillna('')를 추가하여 데이터가 비어있을 때 발생하는 검색 에러 방지
        search_cp = st.text_input("🔍 총판명 또는 학교명 검색").strip()
    with col2:
        # 총판명이 비어있는 경우 제외하고 리스트업
        cp_options = sorted([x for x in df['총판명'].unique() if x])
        selected_cp = st.multiselect("🤝 총판 필터", options=cp_options)

    # 필터 적용
    filtered_df = df.copy().fillna('')
    if search_cp:
        filtered_df = filtered_df[
            filtered_df['총판명'].str.contains(search_cp, case=False) | 
            filtered_df['학교명'].str.contains(search_cp, case=False)
        ]
    if selected_cp:
        filtered_df = filtered_df[filtered_df['총판명'].isin(selected_cp)]

    # 4. 컬럼 최종 조정
    final_cols = [
        "지역", "총판명", "총판담당자", "학교명", "실시간상태",
        "관리교사계정", "관리계정배부일", "배포학교명", 
        "일반교사계정", "일반계정배부일", "체험종료일"
    ]

    # 5. 스타일링
    def style_rows(row):
        status = row['실시간상태']
        if "종료" in status:
            return ['color: #a0a0a0; background-color: #f9f9f9'] * len(row)
        if "임박" in status:
            return ['background-color: #fff9c4; font-weight: bold'] * len(row)
        return [''] * len(row)

    # 6. 데이터프레임 출력
    st.dataframe(
        filtered_df[final_cols].style.apply(style_rows, axis=1),
        use_container_width=True,
        hide_index=True
    )

    st.caption("💡 '실시간상태'는 오늘 날짜와 시트의 '체험종료일'을 비교하여 자동으로 표시됩니다.")