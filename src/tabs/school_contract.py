import streamlit as st
import pandas as pd
from datetime import datetime, date
from src.data_loader import load_contract_school_data
from src.style_utils import render_stat_card

def render():
    c1, c2  = st.columns(2)
    with c1:
        st.markdown("### 📢 정규 계약 학교 관리")
    with c2:
        st.link_button("📂 구글 시트 원본 열기", "https://docs.google.com/spreadsheets/d/1nmAhwBLloq6pFGFIWYahKh4vPQaw08xugCWHURJ076c/edit?gid=1104967938#gid=1104967938")

# 1. 데이터 로드
    df_raw = load_contract_school_data()
    
    if df_raw.empty:
        st.info("계약 학교 데이터를 불러오는 중입니다...")
        return

    # 2. 데이터 가공 및 상태 계산
    df = df_raw.copy()
    # 최신 데이터가 위로 오도록 정렬 (순번 기준이거나 역순)
    df = df.iloc[::-1].reset_index(drop=True)
    today = date.today()

    def calculate_contract_status(row):
        try:
            # 종료일 데이터 확인 (U 또는 V열 데이터가 정확히 들어왔는지)
            end_date_val = row.get('종료일')
            
            if not end_date_val or pd.isna(end_date_val) or str(end_date_val).strip() == "":
                return "⚪ 정보없음"
            
            # 문자열 형태의 날짜를 datetime 객체로 변환
            end_dt = pd.to_datetime(end_date_val).date()
            diff = (end_dt - today).days
            
            if diff < 0: 
                return "⌛ 계약종료"
            elif diff <= 30: 
                return f"🚨 만료임박(D-{diff})"
            else: 
                return "✅ 정상운영"
        except Exception:
            # 날짜 형식이 잘못되었거나 변환 실패 시
            return "⚠️ 확인필요"

    # 상태 계산 적용
    df['운영상태'] = df.apply(calculate_contract_status, axis=1)

    # 상단 카드용 수치 미리 계산
    # '계약종료'와 '정보없음'을 제외한 현재 운영 중인 학교들
    active_mask = ~df['운영상태'].isin(["⌛ 계약종료", "⚪ 정보없음", "⚠️ 확인필요"])
    total_active = len(df[active_mask])
    
    # 만료 임박 학교 (D-30 이내)
    expiring_soon_count = len(df[df['운영상태'].str.contains("🚨", na=False)])

    # ---------------------------------------------------------
    # 🏝️ 상단 요약 카드 
    # ---------------------------------------------------------
    # 종료된 학교를 제외한 현재 '운영 중'인 학교 수
    total_contracts = len(df[df['운영상태'] != "⌛ 계약종료"]) 
    
    # 한 달 내 만료 예정 학교 수
    expiring_count = len(df[df['운영상태'].str.contains("🚨", na=False)])

    # 3. 퍼플 카드 호출 (변수명 일치 확인)
    col1, col2 = st.columns(2)

    with col1:
        render_stat_card(
            emoji="🏫",
            title="총 계약 운영 학교",
            value=total_contracts,  # 변수명 확인!
            unit="개교",
            description="현재 독서화랑 서비스를 이용 중인\n전체 학교 리스트입니다."
        )

    with col2:
        render_stat_card(
            emoji="🚨",
            title="한 달 내 종료 예정",
            value=expiring_count,   # 변수명 확인!
            unit="개교",
            description="30일 이내에 계약이 만료되어\n재계약 검토가 필요한 학교입니다."
        )

    st.divider()
    # 4. 검색 및 필터 UI
    with st.expander("🔍 상세 검색 및 필터", expanded=True):
        f1, f2, f3 = st.columns([1.5, 1, 1])
        with f1:
            search_query = st.text_input("통합 검색 (학교명/교사명/코드/고유번호)", placeholder="검색어를 입력하세요")
        with f2:
            region_list = ["전체"] + sorted(df['지역명'].unique().tolist())
            selected_region = st.selectbox("📍 지역 선택", region_list)
        with f3:
            status_list = ["전체", "✅ 정상운영", "🚨 만료임박", "⌛ 계약종료"]
            selected_status = st.selectbox("🚦 운영 상태", status_list)

    # 필터링 적용
    filtered_df = df.copy()
    if search_query:
        filtered_df = filtered_df[
            filtered_df['학교명'].str.contains(search_query, na=False) |
            filtered_df['관리교사명'].str.contains(search_query, na=False) |
            filtered_df['학교코드'].str.contains(search_query, na=False) |
            filtered_df['학교고유번호'].str.contains(search_query, na=False)
        ]
    if selected_region != "전체":
        filtered_df = filtered_df[filtered_df['지역명'] == selected_region]
    if selected_status != "전체":
        clean_status = selected_status.split()[-1]
        filtered_df = filtered_df[filtered_df['운영상태'].str.contains(clean_status)]

    # 5. 데이터 테이블 출력 (요청하신 필수 정보 포함)
    st.write(f"📊 검색 결과: **{len(filtered_df)}** 건")

    # 표에 반드시 나와야 하는 정보들 배치
    display_cols = [
        "순번", "지역명", "학교명", "운영상태", 
        "학교고유번호", "학교코드", 
        "관리교사명", "관리교사연락처", "관리교사이메일",
        "시작일", "종료일", "계약회차"
    ]

    def style_contract_row(row):
        status = row['운영상태']
        if "만료임박" in status:
            return ['background-color: #fff9c4; color: #850'] * len(row)
        if "계약종료" in status:
            return ['color: #999; text-decoration: line-through'] * len(row)
        return [''] * len(row)

    st.dataframe(
        filtered_df[display_cols].style.apply(style_contract_row, axis=1),
        use_container_width=True,
        hide_index=True
    )

    # 6. 다운로드 버튼
    csv = filtered_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 리스트 다운로드(CSV)",
        data=csv,
        file_name=f"contract_list_{today}.csv",
        mime="text/csv"
    )

if __name__ == "__main__":
    render()