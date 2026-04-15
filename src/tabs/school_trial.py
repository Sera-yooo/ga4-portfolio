import streamlit as st
import pandas as pd
from datetime import datetime, date
from src.data_loader import load_school_trial_data
from src.style_utils import render_stat_card

def render():
    # 1. 데이터 로드 (오류 방지를 위해 가장 먼저 실행)
    df_raw = load_school_trial_data()
    
    if df_raw.empty:
        st.info("데이터를 불러오는 중입니다...")
        return

    # 2. 상태 계산 로직 (데이터 로드 직후 실행)    
    df = df_raw.copy()# 1) 원본 복사
    df = df.iloc[::-1].reset_index(drop=True) # 2) 행 순서 뒤집기 (최신 데이터 상단)
    today = date.today()                     # 3) 오늘 날짜 설정
    

    def calculate_status(row):
        # 최우선 순위: 계약 완료 여부 체크
        if row.get('계약여부') == '여':
            return "🎉 계약완료"
            
        try:
            end_dt = pd.to_datetime(row['종료일']).date()
            diff = (end_dt - today).days
            if diff < 0: return "❌ 종료"
            elif diff == 0: return "🚨 오늘종료"
            elif diff <= 7: return f"⚠️ 임박(D-{diff})"
            else: return "✅ 체험중"
        except: 
            return "정보없음"

    df['체험진행여부'] = df.apply(calculate_status, axis=1)

    # ---------------------------------------------------------
    # 🎨 [개선] 상단 요약 카드 (부드러운 색상 + 학교명 표시)
    # ---------------------------------------------------------
    # 6. 퀵 링크
    c1, c2  = st.columns(2)
    with c1:
        st.markdown("### 📢 실시간 업무 요약")
    with c2:
        st.link_button("📂 구글 시트 원본 열기", "https://docs.google.com/spreadsheets/d/1nmAhwBLloq6pFGFIWYahKh4vPQaw08xugCWHURJ076c/edit?usp=sharing")

    st.divider()    
    
    # 데이터 추출
    today_schools = df[df['체험진행여부'] == "🚨 오늘종료"]['학교명'].tolist()
    urgent_schools = df[df['체험진행여부'].str.contains("임박")]['학교명'].tolist()
    contracted_schools = df[df['계약여부'] == '여']['학교명'].tolist() 

    col1, col2, col3 = st.columns(3)
    
    today_count = len(today_schools)
    urgent_count = len(urgent_schools)
    # ---------------------------------------------------------
    # 🏝️ 상단 요약 카드
    # ---------------------------------------------------------
    col1, col2, col3 = st.columns(3)

    with col1:
        # 오늘 종료 리스트 정리
        today_list = [f"• {s}" for s in today_schools[:2]]
        today_desc = "\n".join(today_list) if today_list else "오늘 종료되는 학교가 없습니다."
        if today_count > 2: today_desc += f"\n...외 {today_count-2}곳"
        
        render_stat_card(
            emoji="🚨",
            title="오늘 체험 종료",
            value=today_count,
            unit="개교",
            description=today_desc
        )

    with col2:
        # 7일 내 종료 리스트 정리
        urgent_list = [f"• {s}" for s in urgent_schools[:2]]
        urgent_desc = "\n".join(urgent_list) if urgent_list else "임박한 학교가 없습니다."
        if urgent_count > 2: urgent_desc += f"\n...외 {urgent_count-2}곳"

        render_stat_card(
            emoji="⚠️",
            title="7일 내 종료 예정",
            value=urgent_count,
            unit="개교",
            description=urgent_desc
        )

    with col3:
        # 계약 완료 학교 현황 
        contract_count = len(contracted_schools)
        contract_list = [f"• {s}" for s in contracted_schools[:2]]
        contract_desc = "\n".join(contract_list) if contract_list else "계약 완료된 학교가 없습니다."
        if contract_count > 2: contract_desc += f"\n...외 {contract_count-2}곳"

        render_stat_card(
            emoji="🎊",
            title="계약 완료",
            value=contract_count,
            unit="개교",
            description=contract_desc
        )

    st.write("")
    st.divider()

    # 4. 검색 및 필터 UI
    with st.expander("🔍 검색 및 필터 설정", expanded=True):
        col1, col2, col3 = st.columns([1.5, 1, 1])
        
        with col1:
            # 학교명, 교사명, 체험교사계정 통합 검색
            search_query = st.text_input("🔍 통합 검색 (학교/교사/계정)", placeholder="검색어를 입력하세요")
            
        with col2:
            # 지역 필터
            all_regions = sorted(df['지역명'].unique()) if '지역명' in df.columns else []
            selected_regions = st.multiselect("📍 지역 선택", options=all_regions, default=all_regions)
            
        with col3:
            # 상태 필터 (자동 계산된 값 기준)
            status_options = ["전체", "🎉 계약완료", "✅ 체험중", "⚠️ 임박", "🚨 오늘종료", "❌ 종료"]
            status_filter = st.selectbox("🚦 실시간 상태", status_options)

    # --- [필터링 로직 적용] ---
    filtered_df = df.copy()

    # 지역 필터
    if selected_regions:
        filtered_df = filtered_df[filtered_df['지역명'].isin(selected_regions)]

    # 검색어 필터
    if search_query:
        filtered_df = filtered_df[
            filtered_df['학교명'].str.contains(search_query, na=False) | 
            filtered_df['교사명'].str.contains(search_query, na=False) |
            filtered_df['체험교사계정'].str.contains(search_query, na=False)
        ]

    # 상태 필터
    if status_filter != "전체":
        # '🎉 계약완료' 또는 '⚠️ 임박' 처럼 이모지가 포함된 경우를 위해 
        # 실제 텍스트 부분만 추출하거나 contains로 검색
        if "계약완료" in status_filter:
            target_status = "계약완료"
        elif "임박" in status_filter:
            target_status = "임박"
        else:            
            target_status = status_filter.split()[-1]
            
        filtered_df = filtered_df[filtered_df['체험진행여부'].str.contains(target_status, na=False)]

    # [1] 표시할 컬럼 및 스타일 정의 (상단 배치)
    display_cols = [
        "순번","지역명", "상세지역명", "학교명", "교사명", 
        "체험진행여부", "시작일", "종료일", "체험교사계정", "계약여부"
    ]

    def style_row(row):
        status = row.get('체험진행여부', '')
        if "🎉 계약완료" in status:
            return ['background-color: #e3f2fd; color: #0d47a1; font-weight: bold'] * len(row)
        elif "🚨 오늘종료" in status:
            return ['background-color: #ffdad9; color: #911'] * len(row)
        elif "⚠️ 임박" in status:
            return ['background-color: #fff9c4; color: #850'] * len(row)
        elif "❌ 종료" in status:
            return ['color: #999'] * len(row)
        return [''] * len(row)        
    # ---------------------------------------------------------
    # 🏝️ 데이터 출력부
    # ---------------------------------------------------------
    
    # 1. 세션 상태를 확인하여 선택 정보 미리 파악 (레이아웃 결정용)
    has_selection = False
    if "school_main_list_df" in st.session_state:
        sel_info = st.session_state["school_main_list_df"]
        if sel_info.get("selection", {}).get("rows"):
            has_selection = True

    # 2. 레이아웃 분할 (선택 시 0.6:0.4)
    if has_selection:
        col_list, col_detail = st.columns([0.6, 0.4])
    else:
        col_list = st.container()
        col_detail = None

    # [왼쪽 영역: 리스트]
    with col_list:
        st.write(f"📊 검색 결과: **{len(filtered_df)}** 건 (기준일: {today})")
        
        selection = st.dataframe(
            filtered_df[display_cols].style.apply(style_row, axis=1),
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            key="school_main_list_df" ,
            height=850
        )

        # 다운로드 버튼
        csv = filtered_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 현재 리스트 다운로드(CSV)", data=csv, file_name=f"trial_status_{today}.csv")

# [오른쪽 영역: 상세 정보 패널]
    if col_detail and selection.selection.rows:
        try:
            # 1. 선택된 행의 상대적 인덱스를 가져옵니다.
            selected_row_index = selection.selection.rows[0]
            
            # 2. filtered_df에서 해당 위치의 데이터를 안전하게 추출합니다.
            # .iloc은 '순서'를 기준으로 데이터를 가져오므로 에러가 없습니다.
            school_data = filtered_df.iloc[selected_row_index]
        
            with col_detail:
                st.write("") # 상단 여백
                
                with st.container(border=True):
                    # 1. 헤더 (학교명 및 상태)
                    st.markdown(f"### 📑 {school_data['학교명']}")
                    st.caption(f"📍 {school_data.get('지역명', '-')} {school_data.get('상세지역명', '')}")
                    
                    status_val = school_data.get('체험진행여부', '-')
                    st.success(f"**실시간 상태:** {status_val}")
                    
                    # 2. 시스템 및 계약 정보
                    st.markdown("##### 🔑 시스템 및 계약 정보")
                    sc1, sc2 = st.columns(2)
                    with sc1:
                        st.write(f"**순번(A):** {school_data.get('순번', '-')}")
                        st.write(f"**학교코드(S):** `{school_data.get('학교코드', '-')}`")
                        st.write(f"**계약여부(Z):** {school_data.get('계약여부', '-')}")
                    with sc2:
                        st.write(f"**유입경로(H):** {school_data.get('유입경로', '-')}")
                        st.write(f"**진행여부(R):** {school_data.get('진행여부', '-')}")
                        st.write(f"**진행상태(O):** {school_data.get('진행상태', '-')}")

                    st.markdown("**교사 계정(T)**")
                    st.code(f"{school_data.get('체험교사계정', '-')}", language=None)
                    st.write(f"📅 **체험 기간:** {school_data.get('시작일', '-')} ~ {school_data.get('종료일', '-')}") 

                    # 3. 담당자 연락 정보
                    st.markdown("##### 👤 담당자 연락처")
                    st.write(f"**성함(E):** {school_data.get('교사명', '-')}")
                    st.write(f"**연락처(F):** {school_data.get('연락처', '-')}")
                    st.write(f"**이메일(G):** {school_data.get('교사메일', '-')}")

                    # 4. 상담 내역
                    st.markdown("##### 📜 상담 히스토리")
                    
                    c_1 = school_data.get('1차상담')
                    c_2 = school_data.get('2차상담')
                    c_3 = school_data.get('3차상담')

                    if c_1:
                        st.info(f"**[1차 상담]**\n\n{c_1}")
                    if c_2:
                        st.info(f"**[2차 상담]**\n\n{c_2}")
                    if c_3:
                        st.warning(f"**[3차 상담]**\n\n{c_3}")
                    
                    if not any([c_1, c_2, c_3]):
                        st.caption("기록된 상담 내역이 없습니다.")
        except IndexError:
            # 혹시나 발생할 수 있는 인덱스 오류 방어
            st.error("데이터를 불러오는 중 오류가 발생했습니다. 다시 선택해주세요.")
    st.write("")
    st.divider()            
