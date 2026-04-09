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
        try:
            end_dt = pd.to_datetime(row['종료일']).date()
            diff = (end_dt - today).days
            if diff < 0: return "❌ 종료"
            elif diff == 0: return "🚨 오늘종료"
            elif diff <= 7: return f"⚠️ 임박(D-{diff})"
            else: return "✅ 체험중"
        except: return "정보없음"

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
    
    today_count = len(today_schools)
    urgent_count = len(urgent_schools)

    # ---------------------------------------------------------
    # 🏝️ 상단 요약 카드 (퍼플 테마 적용)
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
        # 전체 활성 학교 현황
        total_active_count = len(df[~df['체험진행여부'].str.contains("❌ 종료")])
        
        render_stat_card(
            emoji="✅",
            title="전체 활성 학교",
            value=total_active_count,
            unit="개교",
            description="현재 독서화랑을 체험 중인\n모든 학교의 총합입니다."
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
            status_options = ["전체", "✅ 체험중", "⚠️ 임박", "🚨 오늘종료", "❌ 종료"]
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
        # '임박' 선택 시 '임박(D-3)' 등을 모두 포함하도록 검색
        clean_status = status_filter.split()[-1] 
        filtered_df = filtered_df[filtered_df['체험진행여부'].str.contains(clean_status, na=False)]

    # 5. 결과 출력
    st.write(f"📊 검색 결과: **{len(filtered_df)}** 건 (기준일: {today})")

    # 테이블 컬럼 순서 조정
    display_cols = [
        "지역명", "상세지역명", "학교명", "교사명", 
        "체험진행여부", "시작일", "종료일", "체험교사계정", "계약여부"
    ]

    # 행 스타일 적용 (오늘종료/임박 강조)
    def style_row(row):
        status = row['체험진행여부']
        if "오늘종료" in status:
            return ['background-color: #ffdad9; color: #911'] * len(row)
        if "임박" in status:
            return ['background-color: #fff9c4; color: #850'] * len(row)
        if "종료" in status:
            return ['color: #999'] * len(row)
        return [''] * len(row)

    st.dataframe(
        filtered_df[display_cols].style.apply(style_row, axis=1),
        use_container_width=True,
        hide_index=True
    )

    # 현재 필터링된 데이터 다운로드
    csv = filtered_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 현재 리스트 다운로드(CSV)", data=csv, file_name=f"trial_status_{today}.csv")
