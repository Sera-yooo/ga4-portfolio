import streamlit as st
import pandas as pd
from datetime import datetime, date
from src.data_loader import load_school_trial_data, load_trial_consulting_logs,update_school_status , add_consulting_log
from src.style_utils import render_stat_card

def render():    
    # 1. 데이터 로드
    @st.cache_data(ttl=600)
    def get_cached_data():
        raw = load_school_trial_data()
        logs = load_trial_consulting_logs()
        return raw, logs
    
    df_raw, logs_df = get_cached_data()
    
    # 데이터를 가공하기위해 복제한다
    df = df_raw.copy() 
    today = date.today()
    
    if df_raw.empty:
        st.warning("학교 데이터를 불러오지 못했습니다.")
        return

    # 행 스타일 정의 (통화예정 등 강조)
    def style_row(row):
        status = row.get('상담상태', '')
        if status == "통화예정":
            return ['background-color: #fff9db'] * len(row) # 연한 노랑
        if status == "확인필요":
            return ['background-color: #fff0f0'] * len(row) # 연한 빨강
        return [''] * len(row)

    # 보여줄 컬럼 순서 (B~G열 우선 배치)
    priority_cols = ["지역명", "상세지역명", "학교명", "학교연락처", "교사명", "연락처", "상담상태"]
    other_cols = [c for c in df.columns if c not in priority_cols]
    display_cols = priority_cols + other_cols # 리스트 출력용 컬럼 정의

    # --- [추가] 사이드바 필터 (상담 상태 기준) ---
    st.sidebar.markdown("### 🔍 필터 설정")
    status_options = ["26' 1학기 상담종료", "통화예정", "미상담", "계약완료", "확인필요"]
    selected_status = st.sidebar.multiselect(
        "조회할 상담 상태 선택",
        options=status_options,
        default=status_options
    )
    
    # 체험 진행 여부 계산 함수 (기존 유지)
    def calculate_status(row):
        if row.get('계약여부') == '여': return "🎉 계약완료"
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
    contracted_schools = df[df['계약여부'] == '여']['학교명'].tolist() 

    col1, col2, col3 = st.columns(3)
    
    today_count = len(today_schools)
    urgent_count = len(urgent_schools)

    # 4. 검색 및 필터 UI
    with st.expander("🔍 검색 및 필터 설정", expanded=True):
        # 4컬럼으로 확장하여 상담 상태 필터 공간 확보
        col1, col2, col3, col4 = st.columns([1.2, 1, 1, 1])
        
        with col1:
            # 통합 검색 
            search_query = st.text_input("🔍 통합 검색", placeholder="학교/교사/계정 입력")
            
        with col2:
            # 지역 필터 
            all_regions = sorted(df['지역명'].unique()) if '지역명' in df.columns else []
            selected_regions = st.multiselect("📍 지역 선택", options=all_regions, default=all_regions)
            
        with col3:
            # [신규] 상담 상태 필터 (O열 기준 - 업무용)
            # 사용자가 요청한 5가지 상태값 적용
            consult_options = ["전체", "26' 1학기 상담종료", "통화예정", "미상담", "계약완료", "확인필요"]
            selected_consult_status = st.selectbox("📞 상담 상태 (업무)", consult_options)

        with col4:
            # 체험 상태 필터
            live_status_options = ["전체", "🎉 계약완료", "✅ 체험중", "⚠️ 임박", "🚨 오늘종료", "❌ 종료"]
            selected_live_status = st.selectbox("🚦 체험 상태 (일정)", live_status_options)

    # --- [필터링 로직 적용] ---
    filtered_df = df.copy()

    # 1. 지역 필터
    if selected_regions:
        filtered_df = filtered_df[filtered_df['지역명'].isin(selected_regions)]

    # 2. 통합 검색 필터
    if search_query:
        filtered_df = filtered_df[
            filtered_df['학교명'].str.contains(search_query, na=False) | 
            filtered_df['교사명'].str.contains(search_query, na=False) |
            filtered_df['체험교사계정'].str.contains(search_query, na=False)
        ]

    # 3. 상담 상태 필터
    if selected_consult_status != "전체":
        filtered_df = filtered_df[filtered_df['상담상태'] == selected_consult_status]

    # 4. 체험 실시간 상태 필터 
    if selected_live_status != "전체":
        if "임박" in selected_live_status:
            filtered_df = filtered_df[filtered_df['체험진행여부'].str.contains("임박")]
        else:
            filtered_df = filtered_df[filtered_df['체험진행여부'] == selected_live_status]
    
    # ---------------------------------------------------------
    # 🏝️ 데이터 출력부
    # ---------------------------------------------------------
    
    col_list, col_detail = st.columns([0.5, 0.5])

    # ---------------------------------------------------------
    # 📋 학교 리스트 영역
    # ---------------------------------------------------------
    with col_list:
        # 상단 정보 요약
        st.caption(
            f"📅 기준일: {today} · 검색 결과 {len(filtered_df)}건"
        )

        st.divider()

        # 데이터프레임 출력
        # style.apply(style_row)를 통해 '통화예정' 등에 색상을 넣는 로직이 포함된 상태입니다.
        selection = st.dataframe(
            filtered_df[display_cols].style.apply(
                style_row,
                axis=1
            ),
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            key="school_main_list_df",
            height=720
        )

        st.write("")

        # CSV 다운로드 버튼 (데이터 순서와 컬럼이 정비된 filtered_df 기준)
        csv = filtered_df[display_cols].to_csv(
            index=False
        ).encode('utf-8-sig')

        st.download_button(
            "📥 현재 리스트 다운로드 (CSV)",
            data=csv,
            file_name=f"school_list_{today}.csv",
            use_container_width=True
        )

    # [오른쪽 영역: 상세 정보 패널]    
    if col_detail and selection.selection.rows:
        try:
            # 1. 선택된 행의 상대적 인덱스를 가져옵니다.
            selected_row_index = selection.selection.rows[0]
            
            # 2. filtered_df에서 해당 위치의 데이터를 추출합니다.
            school_data = filtered_df.iloc[selected_row_index]
            
            # ---------------------------------------------------------
            # 🚀 [수정 포인트] 선택된 학교의 상담 로그 필터링 로직 추가
            # ---------------------------------------------------------
            target_id = str(school_data["순번"]).strip()
            school_logs = logs_df[logs_df["체험인덱스"].astype(str).str.strip() == target_id].copy()
            # ---------------------------------------------------------

            with col_detail:
                st.markdown(f"### 🏫 {school_data['학교명']}") # 학교명 상단 출력

                # --- [섹션 1] 상담 타임라인
                st.markdown("#### 📜 상담 타임라인")
                if not school_logs.empty:
                    # 날짜순 정렬 (최신순)
                    school_logs["날짜"] = pd.to_datetime(school_logs["날짜"], errors="coerce")
                    school_logs = school_logs.sort_values("날짜", ascending=True)

                    for _, log in school_logs.iterrows():
                        c_type = log.get("상담유형", "기타")
                        c_date = log["날짜"].strftime("%Y-%m-%d") if pd.notnull(log["날짜"]) else "날짜미상"
                        c_content = log.get("상담내용", "-")
                        c_manager = log.get("담당자", "미지정")

                        # 아이콘 설정
                        icon = {
                            "상담": "📞", "계약": "🎉", "메모": "📝", 
                            "부재중": "📵", "상담종료": "📌"
                        }.get(c_type, "📌")
                        
                        with st.container(border=True):
                            # 1. 상단 레이아웃 (날짜 강조 배지 & 담당자)
                            col_header1, col_header2 = st.columns([0.7, 0.3])
                            
                            with col_header1:
                                st.markdown(f"""
                                    <div style="display: flex; align-items: center; gap: 10px;">
                                        <span style="
                                            background-color: #e1f5fe; 
                                            color: #01579b; 
                                            padding: 2px 8px; 
                                            border-radius: 4px; 
                                            font-weight: bold; 
                                            font-size: 0.9rem;
                                        ">{c_date}</span>
                                        <span style="font-weight: bold; font-size: 1rem;">{icon} {c_type}</span>
                                    </div>
                                """, unsafe_allow_html=True)
                                
                            with col_header2:
                                st.markdown(f"<p style='text-align:right; color:#666; font-size:0.85rem; margin:0;'>👤 {c_manager}</p>", unsafe_allow_html=True)
                            
                            # 2. 상담 내용 박스
                            st.markdown(f"""
                                <div style="
                                    background-color: #ffffff; 
                                    padding: 12px; 
                                    border: 1px solid #eee;
                                    border-radius: 6px; 
                                    margin-top: 10px;
                                    font-size: 0.95rem;
                                    color: #222;
                                    line-height: 1.6;
                                ">
                                    {c_content}
                                </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info("등록된 상담 로그가 없습니다.")

                #  --- [섹션 2] 상담 기록 및 상태 변경 ---
                with st.form("unified_consulting_form", clear_on_submit=True):
                    st.markdown("##### ✍️ 상담 기록 및 상태 변경")
                    
                    # [레이아웃 조정] 상단: 날짜와 상태를 한 줄에 배치
                    top_c1, top_c2 = st.columns(2)
                    with top_c1:
                        input_date = st.date_input("📅 상담 날짜", value=date.today())
                    with top_c2:
                        status_list = ["26' 1학기 상담종료", "통화예정", "미상담", "계약완료", "확인필요"]
                        current_status = school_data.get("상담상태", "미상담")
                        try:
                            current_idx = status_list.index(current_status)
                        except:
                            current_idx = 2
                        new_status = st.selectbox("⚡ 진행 단계 변경", options=status_list, index=current_idx)

                    # [레이아웃 조정] 중간: 유형과 담당자를 한 줄에 배치
                    mid_c1, mid_c2 = st.columns(2)
                    with mid_c1:
                        c_type = st.selectbox("📞 상담 유형",  ["부재중", "상담종료", "상담", "계약완료", "메모"])
                    with mid_c2:
                        c_manager = st.text_input("👤 담당자명", value=school_data.get("교사명", "담당자"))

                    # 하단: 상담 내용
                    c_content = st.text_area("🗒️ 상담 상세 내용", placeholder="내용을 입력하세요.", height=120)

                    # 통합 저장 버튼
                    submit_btn = st.form_submit_button("🚀 기록 저장 및 상태 업데이트", use_container_width=True)

                    if submit_btn:
                        if not c_content.strip():
                            st.warning("내용을 입력해 주세요.")
                        else:
                            # 1단계: 상담 로그 추가 (체험학교상담로그 시트)
                            log_success = add_consulting_log(
                                school_data["순번"], 
                                school_data["학교명"], 
                                input_date, 
                                c_type, 
                                c_content, 
                                c_manager
                            )
                            
                            # 2단계: 상담 상태 업데이트 (상담/체험학교 시트 O열)
                            status_success = update_school_status(school_data["순번"], new_status)
                            
                            if log_success and status_success:
                                st.success(f"✅ 기록 저장 및 상태 변경({new_status}) 완료!")
                                st.cache_data.clear() 
                                st.rerun()
                            elif log_success:
                                st.info("⚠️ 상담 로그는 저장되었으나 상태 업데이트에 실패했습니다.")

        except Exception as e:
            st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.write("")
    st.divider()            

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
