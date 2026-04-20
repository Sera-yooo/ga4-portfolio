import streamlit as st
import pandas as pd
from src.data_loader import load_distributor_monitoring_data

def render():
    st.title("🕵️ 총판 활동 감시 대시보드")
    
    df = load_distributor_monitoring_data()
    if df.empty:
        st.warning("데이터를 불러올 수 없습니다.")
        return

    # 1. 시계열 데이터 처리 보정
    # 이미 data_loader에서 컬럼명을 "누적방문"으로 고정했으므로 
    # 숫자로 변환하여 계산 로직을 단순화합니다.
    df['누적방문'] = pd.to_numeric(df['누적방문'], errors='coerce').fillna(0)
    
    # 현재 구조에서는 '이전 데이터'를 따로 컬럼으로 가져오지 않으므로 
    # 증감 계산을 위해선 누적방문 숫자 자체를 보여주거나 
    # 나중에 데이터로더에서 '이전방문' 컬럼을 추가로 정의해야 합니다.
    # 우선 에러 방지를 위해 '이번주_증감'을 '누적방문' 값으로 대체합니다.
    df['이번주_증감'] = df['누적방문']

    # 2. 상단 핵심 요약 (KPI)
    # 누적방문이 0인 계정을 '미활동'으로 간주
    inactivity_count = len(df[df['누적방문'] == 0])
    
    col1, col2, col3 = st.columns(3)
    col1.metric("전체 모니터링 계정", f"{len(df)}개")
    col2.metric("미활동 계정 (누적 0회)", f"{inactivity_count}개", delta="-위험", delta_color="inverse")
    col3.metric("최신 기준일", "시트 최신열")

    # 3. 필터 및 검색
    st.divider()
    f_col1, f_col2, f_col3 = st.columns([1, 1, 1])
    with f_col1:
        selected_cp = st.multiselect("🤝 총판명 필터", options=df['총판명'].unique())
    with f_col2:
        selected_role = st.multiselect("👤 교사구분", options=df['교사구분'].unique())
    with f_col3:
        search_school = st.text_input("🔍 학교명 검색")

    # 필터 적용
    filtered_df = df.copy()
    if selected_cp:
        filtered_df = filtered_df[filtered_df['총판명'].isin(selected_cp)]
    if selected_role:
        filtered_df = filtered_df[filtered_df['교사구분'].isin(selected_role)]
    if search_school:
        filtered_df = filtered_df[filtered_df['학교명'].str.contains(search_school, case=False)]

    # 4. 감시 전용 스타일링
    def highlight_inactivity(row):
        # 누적 방문이 0이면 빨간색 강조
        if row['누적방문'] == 0:
            return ['background-color: #ffebee'] * len(row)
        # 많이 사용(예: 10회 이상)하면 초록색 강조
        elif row['누적방문'] >= 10:
            return ['background-color: #e8f5e9'] * len(row)
        return [''] * len(row)
            
    # 5. 출력할 컬럼 리스트 (data_loader의 fixed_columns와 일치)
    display_cols = [
        "지역", "총판명", "학교명", "교사구분", 
        "관리교사계정", "누적방문", "마지막로그인"
    ]
    
    # 존재하는 컬럼만 필터링
    available_cols = [col for col in display_cols if col in filtered_df.columns]

    st.subheader("📋 계정별 활동 현황")
    st.caption("🔍 표에서 행을 클릭(선택)하면 하단에 상세 리포트가 나타납니다.")

    # 1. 출력할 컬럼 정의
    display_cols = [
        "지역", "총판명", "학교명", "교사구분", 
        "관리교사계정", "누적방문", "마지막로그인"
    ]
    available_cols = [col for col in display_cols if col in filtered_df.columns]

    # 2. 데이터프레임 출력 (선택 모드 활성화)
    # on_select="rerun"을 설정하면 표 앞에 체크박스와 비슷한 선택 UI가 활성화됩니다.
    selection_event = st.dataframe(
        filtered_df[available_cols].style.apply(highlight_inactivity, axis=1),
        use_container_width=True,
        hide_index=True,
        on_select="rerun",  # 사용자가 행을 클릭하면 스크립트 재실행
        selection_mode="single-row" #나만 선택 가능
    )

    # 3. 하단 상세 정보창 (선택되었을 때만 등장)
    # selection_event에서 선택된 행 인덱스를 가져옵니다.
    if selection_event and "selection" in selection_event and len(selection_event["selection"]["rows"]) > 0:
        selected_index = selection_event["selection"]["rows"][0]
        selected_row = filtered_df.iloc[selected_index]
        
        st.write("") # 간격 조절
 
    if selection_event and "selection" in selection_event and len(selection_event["selection"]["rows"]) > 0:
        selected_index = selection_event["selection"]["rows"][0]
        selected_row = filtered_df.iloc[selected_index]
        target_school = selected_row['학교명']
        
        st.divider()
        st.subheader(f"🔍 {target_school} 계정 활동 가계도")
        
        # 해당 학교의 모든 계정 데이터 추출 (위계 분석용)
        school_data = df[df['학교명'] == target_school].copy()
        school_data['누적방문'] = pd.to_numeric(school_data['누적방문'], errors='coerce').fillna(0)

        # 1. 시각적 트리 뷰 생성
        tree_text = ""
        
        # 관리교사와 일반교사 분리
        admins = school_data[school_data['교사구분'].str.contains('관리', na=False)]
        regulars = school_data[~school_data['교사구분'].str.contains('관리', na=False)]

        # 관리교사 출력
        for _, admin in admins.iterrows():
            status = "🟢" if admin['누적방문'] > 0 else "🔴"
            tree_text += f"**{status} 👑 관리교사 ({admin['관리교사계정']})** : {admin['누적방문']}회 방문 / {admin['마지막로그인']}\n\n"
            
            # 해당 관리교사 아래에 일반교사들 들여쓰기 출력
            if not regulars.empty:
                for _, reg in regulars.iterrows():
                    r_status = "🟢" if reg['누적방문'] > 0 else "🔴"
                    tree_text += f"&nbsp;&nbsp;&nbsp;&nbsp;┗━ {r_status} 👤 일반교사 ({reg['관리교사계정']}) : {reg['누적방문']}회 / {reg['마지막로그인']}\n\n"
            else:
                tree_text += "&nbsp;&nbsp;&nbsp;&nbsp;┗━ ⚠️ 등록된 일반교사 계정이 없습니다.\n\n"

        # 화면 표시
        with st.container(border=True):
            st.markdown(tree_text, unsafe_allow_html=True)

        # 2. 총판 담당자 피드백 자동 생성
        st.info(f"📍 **{selected_row['총판명']} ({selected_row['총판담당자']})** 담당자에게 전달할 내용:")
        
        active_regs = len(regulars[regulars['누적방문'] > 0])
        total_regs = len(regulars)
        
        if total_regs > 0 and active_regs == 0:
            st.error(f"❌ {target_school}: 관리교사는 활동 중이나 일반교사({total_regs}명)의 접속이 전무합니다. 교육 지원이 필요합니다.")
        elif total_regs == 0:
            st.warning(f"⚠️ {target_school}: 현재 관리교사 계정만 존재합니다. 추가 계정 배부가 필요한지 확인하세요.")
        else:
            st.success(f"✅ {target_school}: 일반교사 {active_regs}/{total_regs}명이 정상적으로 활용 중입니다.")

    elif not filtered_df.empty:
        st.info("👆 위 표에서 학교를 클릭하면 관리교사-일반교사 간의 '활동 위계'를 확인할 수 있습니다.")