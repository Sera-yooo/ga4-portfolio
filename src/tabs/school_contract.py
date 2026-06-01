import streamlit as st
import pandas as pd
from datetime import datetime, date
from src.data_loader import load_contract_school_data
from src.style_utils import render_stat_card


# 임박 기준(일). 며칠 전부터 챙길지 — 여기 숫자만 바꾸면 됨.
IMMINENT_DAYS = 14


def _days_left(end_val, today):
    """종료일까지 남은 일수. 값이 없거나 이상하면 None."""
    if end_val is None or pd.isna(end_val) or str(end_val).strip() == "":
        return None
    try:
        return (pd.to_datetime(end_val).date() - today).days
    except Exception:
        return None


def _fmt_date(v):
    """날짜값 -> 'YYYY-MM-DD' (실패하면 원본 앞 10자)."""
    if v is None or str(v).strip() == "":
        return "-"
    try:
        return pd.to_datetime(v).strftime("%Y-%m-%d")
    except Exception:
        return str(v)[:10]


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
            elif diff <= IMMINENT_DAYS: return f"🚨 만료임박(D-{diff})"
            else: return "✅ 정상운영"
        except Exception:
            return "⚠️ 확인필요"

    df['운영상태'] = df.apply(calculate_contract_status, axis=1)

    # =========================================================
    # 🔔 곧 만료되는 학교 (D-14 이내) — 이 페이지의 핵심
    #   · 임박한 학교만 위에 모아서 표시 (이미 끝난 건 아래 표에만 기록)
    #   · 전화로 챙기실 수 있게 관리교사 이름·연락처도 함께 노출
    # =========================================================
    df['_dleft'] = df['종료일'].apply(lambda v: _days_left(v, today))
    imminent = (
        df[df['_dleft'].notna() & (df['_dleft'] >= 0) & (df['_dleft'] <= IMMINENT_DAYS)]
        .sort_values('_dleft')
    )

    st.markdown(f"#### 🔔 곧 만료되는 학교 (D-{IMMINENT_DAYS} 이내)")
    if imminent.empty:
        st.success(f"✅ {IMMINENT_DAYS}일 내 만료 예정 학교가 없습니다.")
    else:
        with st.container(border=True):
            for _, r in imminent.iterrows():
                d = int(r['_dleft'])
                tag = "오늘 만료" if d == 0 else f"D-{d}"
                line = f"🚨 **{r['학교명']}**  ·  {tag}  ·  종료 {_fmt_date(r['종료일'])}"
                mgr = str(r.get('관리교사명', '') or '').strip()
                tel = str(r.get('관리교사연락처', '') or '').strip()
                if mgr:
                    line += f"  ·  담당 {mgr}"
                if tel:
                    line += f"  ·  ☎ {tel}"
                st.markdown(line)
        st.caption("※ 서비스 점검차 연락이 필요한 학교입니다. 이미 만료된 학교는 아래 목록에서 확인하세요.")

    st.divider()

    # =========================================================
    # 📋 견적 현황 — 견적발송 / 계약완료 / 반려
    #   · 판정: '견적계약여부'(L열) 값을 그대로 사용
    #   · 회신 대기(='견적발송' 상태)만 펼쳐서 강조 (계약/반려는 끝난 상태)
    # =========================================================
    def _quote_status(row):
        v = str(row.get('견적계약여부', '') or '').strip()
        return v if v else "-"

    df['견적상태'] = df.apply(_quote_status, axis=1)

    q_sent = df[df['견적상태'] == "견적발송"]
    q_done = len(df[df['견적상태'] == "계약완료"])
    q_rej = len(df[df['견적상태'] == "반려"])

    st.markdown("#### 📋 견적 현황")
    st.markdown(f"견적발송(회신대기) **{len(q_sent)}** · 계약완료 **{q_done}** · 반려 **{q_rej}**")

    if not q_sent.empty:
        with st.expander(f"▸ 회신 대기 중인 학교 {len(q_sent)}곳 보기", expanded=False):
            for _, r in q_sent.iterrows():
                line = f"📨 **{r['학교명']}**"
                sent_disp = _fmt_date(r.get('견적발송날짜'))
                dleft = _days_left(r.get('견적발송날짜'), today)
                if sent_disp != "-":
                    line += f"  ·  발송 {sent_disp}"
                    if dleft is not None:
                        line += f" ({abs(dleft)}일 경과)"
                mgr = str(r.get('계약교사명', '') or '').strip()
                tel = str(r.get('계약교사연락처', '') or '').strip()
                if mgr:
                    line += f"  ·  담당 {mgr}"
                if tel:
                    line += f"  ·  ☎ {tel}"
                st.markdown(line)
        st.caption("※ 견적 보냈으나 아직 계약/반려로 정리되지 않은 학교입니다.")

    st.divider()

    # 상단 요약 수치
    total_contracts = len(df[df['운영상태'] != "⌛ 계약종료"]) 
    expiring_count = len(df[df['운영상태'].str.contains("🚨", na=False)])

    col1, col2 = st.columns(2)
    with col1:
        render_stat_card(emoji="🏫", title="총 계약 운영 학교", value=total_contracts, unit="개교", description="현재 서비스를 이용 중인 전체 학교입니다.")
    with col2:
        render_stat_card(emoji="🚨", title="2주 내 종료 예정", value=expiring_count, unit="개교", description=f"{IMMINENT_DAYS}일 이내 계약 만료 예정 학교입니다.")

    st.divider()

    # 3. 검색 및 필터 UI
    with st.expander("🔍 상세 검색 및 필터", expanded=True):
        f1, f2, f3, f4 = st.columns([1.5, 1, 1, 1])
        with f1:
            search_query = st.text_input("통합 검색 (학교명/교사명/코드/고유번호)", placeholder="검색어를 입력하세요")
        with f2:
            region_list = ["전체"] + sorted(df['지역명'].unique().tolist())
            selected_region = st.selectbox("📍 지역 선택", region_list)
        with f3:
            status_list = ["전체", "✅ 정상운영", "🚨 만료임박", "⌛ 계약종료"]
            selected_status = st.selectbox("🚦 운영 상태", status_list)
        with f4:
            quote_list = ["전체", "견적발송", "계약완료", "반려"]
            selected_quote = st.selectbox("📋 견적 상태", quote_list)

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
    if selected_quote != "전체":
        filtered_df = filtered_df[filtered_df['견적상태'] == selected_quote]

    def style_contract_row(row):
        """배경색 = 만료 상태(행 전체), 글씨색 = 견적 상태(견적상태 칸만)."""
        status = str(row.get('운영상태', ''))

        # --- 배경/행 스타일: 만료 기준 ---
        if "⌛ 계약종료" in status:
            base, ended = 'color: #999; text-decoration: line-through', True
        elif "🚨 만료임박" in status:
            base, ended = 'background-color: #fff9c4; font-weight: bold', False
        elif "⚪" in status or "⚠️" in status:
            base, ended = 'color: #d32f2f', False
        else:
            base, ended = '', False

        styles = [base] * len(row)

        # --- 견적상태 칸만 글씨색 (종료된 행은 회색 유지) ---
        if not ended and '견적상태' in row.index:
            q = str(row.get('견적상태', '')).strip()
            qcolor = {"견적발송": "#e67e22", "계약완료": "#2e7d32", "반려": "#d32f2f"}.get(q, "")
            if qcolor:
                i = row.index.get_loc('견적상태')
                sep = '; ' if styles[i] else ''
                styles[i] = f'{styles[i]}{sep}color: {qcolor}; font-weight: 600'

        return styles

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
        
        # 표시할 컬럼(요청 순서). 색칠은 '운영상태'를 보고 하므로 데이터엔 남겨두고,
        # column_order 로 보이는 컬럼만 제한한다.
        list_display_cols = ["학교명", "학교코드", "시작일", "종료일", "견적상태", "계약교사명", "계약교사연락처"]
        list_df = filtered_df.copy()
        list_df['_dleft'] = list_df['종료일'].apply(lambda v: _days_left(v, today))
        # 남은 일수 오름차순(임박 먼저), 날짜 없는 곳은 맨 뒤로
        list_df = list_df.sort_values('_dleft', na_position='last').reset_index(drop=True)

        selection = st.dataframe(
            list_df.style.apply(style_contract_row, axis=1),
            column_order=list_display_cols,
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
            school_data = list_df.iloc[selected_row_index]
            
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