import streamlit as st
import pandas as pd
from datetime import datetime, date
from src.data_loader import load_contract_school_data
from src.style_utils import render_stat_card

def render():
    c1, c2 = st.columns(2)
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
    df = df.iloc[::-1].reset_index(drop=True)
    today = date.today()

    def calculate_contract_status(row):
        try:
            end_date_val = row.get('종료일')
            if not end_date_val or pd.isna(end_date_val) or str(end_date_val).strip() == "":
                return "⚪ 정보없음"
            end_dt = pd.to_datetime(end_date_val).date()
            diff = (end_dt - today).days
            if diff < 0: return "⌛ 계약종료"
            elif diff <= 30: return f"🚨 만료임박(D-{diff})"
            else: return "✅ 정상운영"
        except Exception:
            return "⚠️ 확인필요"

    df['운영상태'] = df.apply(calculate_contract_status, axis=1)

    # 상단 요약 수치
    total_contracts = len(df[df['운영상태'] != "⌛ 계약종료"]) 
    expiring_count = len(df[df['운영상태'].str.contains("🚨", na=False)])

    col1, col2 = st.columns(2)
    with col1:
        render_stat_card(emoji="🏫", title="총 계약 운영 학교", value=total_contracts, unit="개교", description="현재 서비스를 이용 중인 전체 학교입니다.")
    with col2:
        render_stat_card(emoji="🚨", title="한 달 내 종료 예정", value=expiring_count, unit="개교", description="30일 이내 계약 만료 예정 학교입니다.")

    st.divider()

    # 3. 검색 및 필터 UI
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

    def style_contract_row(row):
        """
        운영상태에 따른 행 스타일 정의
        """
        # '운영상태' 컬럼의 값을 가져옵니다.
        status = row.get('운영상태', '')
        
        # 1. 만료 임박: 연한 노란색 배경 (주의 필요)
        if "🚨 만료임박" in status:
            return ['background-color: #fff9c4; color: #850; font-weight: bold'] * len(row)
        
        # 2. 계약 종료: 회색 글자 + 취소선 (종료된 데이터)
        elif "⌛ 계약종료" in status:
            return ['color: #999; text-decoration: line-through'] * len(row)
        
        # 3. 정상 운영: 별도 스타일 없음 (또는 필요시 연한 녹색 등 설정 가능)
        elif "✅ 정상운영" in status:
            # return ['background-color: #e8f5e9'] * len(row) # 필요시 주석 해제
            return [''] * len(row)
            
        # 4. 정보 없음 또는 확인 필요
        elif "⚪" in status or "⚠️" in status:
            return ['color: #d32f2f'] * len(row)
            
        return [''] * len(row)

    # ---------------------------------------------------------
    # 🏝️ 데이터 출력부 (유동적 레이아웃)
    # ---------------------------------------------------------
    
    # 1. 세션 상태로 선택 여부 확인
    has_selection = False
    if "contract_main_list" in st.session_state:
        sel_info = st.session_state["contract_main_list"]
        if sel_info.get("selection", {}).get("rows"):
            has_selection = True

    # 2. 레이아웃 결정 (선택 시 0.5:0.5 또는 0.6:0.4)
    # 정보가 많으므로 0.5:0.5 비중도 좋습니다.
    if has_selection:
        col_list, col_detail = st.columns([0.5, 0.5])
    else:
        col_list = st.container()
        col_detail = None

    # [왼쪽 영역: 리스트] - 핵심 정보 6~7개만 노출
    with col_list:
        st.write(f"📊 검색 결과: **{len(filtered_df)}** 건")
        
        # 표에는 꼭 필요한 것만!
        list_display_cols = ["순번", "지역명", "학교명", "운영상태", "관리교사명", "시작일", "종료일"]

        selection = st.dataframe(
            filtered_df[list_display_cols].style.apply(style_contract_row, axis=1),
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            key="contract_main_list",
            height=700
        )

        csv = filtered_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 전체 데이터 다운로드(CSV)", data=csv, file_name=f"contract_full_list_{today}.csv")

    # [오른쪽 영역: 상세 정보 패널] - 로드된 모든 데이터를 섹션별로 배치
    if col_detail and selection.selection.rows:
        try:
            selected_row_index = selection.selection.rows[0]
            school_data = filtered_df.iloc[selected_row_index]
            
            with col_detail:
                st.write("") # 상단 여백
                
                with st.container(border=True):
                    # --- 헤더 섹션 ---
                    st.markdown(f"### 🏫 {school_data['학교명']}")
                    st.caption(f"📍 {school_data.get('지역명')} {school_data.get('상세지역')} | {school_data.get('계약회차')}회차 계약")
                    
                    status_val = school_data.get('운영상태', '-')
                    if "정상" in status_val: st.success(f"**운영 상태:** {status_val}")
                    elif "만료" in status_val: st.warning(f"**운영 상태:** {status_val}")
                    else: st.error(f"**운영 상태:** {status_val}")

                    # --- 1. 계약 및 시스템 정보 ---
                    st.markdown("##### 🔑 계약 및 시스템 정보")
                    c1, c2 = st.columns(2)
                    with c1:
                        st.write(f"**학교코드:** `{school_data.get('학교코드', '-')}`")
                        st.write(f"**고유번호:** {school_data.get('학교고유번호', '-')}")
                        st.write(f"**사업자번호:** {school_data.get('학교사업자번호', '-')}")
                    with c2:
                        st.write(f"**계약일:** {school_data.get('계약일', '-')}")
                        st.write(f"**시작일:** {school_data.get('시작일', '-')}")
                        st.write(f"**종료일:** {school_data.get('종료일', '-')}")

                    # --- 2. 교사 연락처 정보 (계약 vs 관리) ---
                    st.divider()
                    st.markdown("##### 👤 담당자 정보")
                    tc1, tc2 = st.columns(2)
                    with tc1:
                        st.markdown("**[계약 담당]**")
                        st.write(f"**성함:** {school_data.get('계약교사명', '-')}")
                        st.write(f"**연락처:** {school_data.get('계약교사연락처', '-')}")
                        st.caption(f"{school_data.get('계약교사이메일', '')}")
                    with tc2:
                        st.markdown("**[운영 관리]**")
                        st.write(f"**성함:** {school_data.get('관리교사명', '-')}")
                        st.write(f"**연락처:** {school_data.get('관리교사연락처', '-')}")
                        st.caption(f"{school_data.get('관리교사이메일', '')}")

                    # --- 3. 행정 및 비용 정보 ---
                    st.divider()
                    st.markdown("##### 📑 행정 및 비용 정보")
                    ac1, ac2 = st.columns(2)
                    with ac1:
                        st.write(f"**계약 학생 수:** {school_data.get('계약학생수', '-')}명")
                        st.write(f"**계약 단위:** {school_data.get('계약단위', '-')}")
                    with ac2:
                        st.write(f"**총 금액:** {school_data.get('총금액(vat포함)', '-')}원")
                        st.write(f"**이전 체험:** {school_data.get('이전 체험 현황', '-')}")

                    # --- 4. 기타 정보 ---
                    if school_data.get('체험일'):
                        st.info(f"📅 **체험 진행일:** {school_data.get('체험일')}")

        except Exception as e:
            st.error("상세 정보를 표시하는 중 오류가 발생했습니다.")

if __name__ == "__main__":
    render()