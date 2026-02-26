import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

# ==========================================
# [설정] 페이지 설정
# ==========================================
st.set_page_config(page_title="회원 가입 분석", page_icon="📈", layout="wide")

st.title("📈 독서화랑 회원 가입 분석")

# -------------------------------------------------------------------
# [설정] 구글 시트 주소
# -------------------------------------------------------------------
NEW_SHEET_URL = "https://docs.google.com/spreadsheets/d/1gQ9kS_gVrcvDFA7cZEy6Ch5pSxRSbSwUaPX-ZwVUVV0/edit?usp=sharing"
# -------------------------------------------------------------------

# ==========================================
# [설정] 고정값 (재원생 수 & 기존 가입자 수)
# ==========================================
# 1. 지점별 총 재원생 수 (분모)
TOTAL_STUDENTS = {
    '대치점': 1835,
    '잠실점': 1351,
    '서초점': 1042,
    '분당점': 594,
    '온라인': 795
}

# 2. [추가] 12/3 이전 기존 가입자 수 (시작값)
# (~9/14 가입자 데이터 반영)
BASE_SUBSCRIBERS = {
    '대치점': 438,
    '잠실점': 230,
    '서초점': 258,
    '분당점': 124,
    '온라인': 99
}

# ==========================================
# [설정] 그래프 디자인 테마 (Ryah's Rhythm Game UI)
# ==========================================
# 1. 배경 설정 (빈티지 색감이 돋보이게 깔끔한 흰색 배경 사용)
# ※ 주의: 여기엔 'plotly_white', 'seaborn' 같은 약속된 이름만 들어가야 해요!
THEME_TEMPLATE = "plotly_white" 

# 2. Ryah's Rhythm Game UI 컬러 팔레트 (사랑스럽고 빈티지한 색감)
MY_COLORS = ['#F2C744', '#88A61C','#6BBEF2', '#BF2604', '#D9A59A', '#260101']

# ==========================================
# [함수] 데이터 로드
# ==========================================
@st.cache_data(ttl=60)
def load_data():
    try:
        # 1. 인증 정보 설정 (파일 없이 secrets만 사용)
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        
        # 이전의 from_json_keyfile_name 부분은 완전히 지우고 아래 내용만 남깁니다.
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        
        client = gspread.authorize(creds)
        
        # 2. 시트 연결 및 데이터 로드
        sh = client.open_by_url(NEW_SHEET_URL)
        worksheet = sh.worksheet('가입자_RAW_DATA(신규)')        
        
        data = worksheet.get_all_values()

        
        if len(data) < 2:
            return pd.DataFrame()
            
        header = data[0]
        rows = data[1:]
        
        # 중복 컬럼명 해결
        seen_count = {}
        new_header = []
        for col_name in header:
            if col_name in seen_count:
                seen_count[col_name] += 1
                new_header.append(f"{col_name}_{seen_count[col_name]}")
            else:
                seen_count[col_name] = 0
                new_header.append(col_name)
        
        df = pd.DataFrame(rows, columns=new_header)
        
        # 전처리
        if '가입일' in df.columns:
            df['가입일'] = pd.to_datetime(df['가입일'], errors='coerce')
        
        if '소속' in df.columns:
            df['소속'] = df['소속'].astype(str).str.strip()
            df['소속'] = df['소속'].replace({
                '대치': '대치점', '잠실': '잠실점', '서초': '서초점', '분당': '분당점'
            })
            df = df[~df['소속'].isin(['x', 'X'])]
            
        if '학년' in df.columns:
            df['학년'] = df['학년'].astype(str).str.strip()

        return df

    except Exception as e:
        st.error(f"데이터 로드 중 오류 발생: {e}")
        return None

# 데이터 불러오기
with st.spinner("데이터를 분석하고 있습니다..."):
    df = load_data()

if df is None or df.empty:
    st.warning("데이터가 없거나 불러오지 못했습니다.")
    st.stop()

# ==========================================
# [UI] 1. 핵심 지표 (KPI)
# ==========================================
st.subheader("📌 핵심 요약 (전체 데이터 기준)")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

total_members = len(df)
kpi1.metric("총 가입 회원", f"{total_members:,}명")

if '가입일' in df.columns:
    this_month = datetime.datetime.now().strftime('%Y-%m')
    valid_date_df = df.dropna(subset=['가입일'])
    new_member_count = len(valid_date_df[valid_date_df['가입일'].dt.strftime('%Y-%m') == this_month])
    kpi2.metric("이번 달 신규", f"{new_member_count}명", "New!")
else:
    kpi2.metric("이번 달 신규", "-")

if '학년' in df.columns:
    top_grade = df['학년'].value_counts().idxmax()
    kpi3.metric("최다 가입 학년", top_grade)
else:
    kpi3.metric("최다 가입 학년", "-")

if '소속' in df.columns:
    top_org = df['소속'].value_counts().idxmax()
    kpi4.metric("최다 가입 소속", top_org)
else:
    kpi4.metric("최다 가입 소속", "-")

st.divider()

# ==========================================
# [UI] 2. 탭 구성
# ==========================================
# tab1, tab2, tab3, tab4 = st.tabs(["📊 가입 현황", "🎯 초등(1~5) 집계", "📈 재원생 대비 현황", "📄 원본 데이터"])
tab1, tab2, tab3 = st.tabs(["📊 가입 현황", "🎯 초등(1~5) 집계", "📈 재원생 대비 현황"])

# --- 탭 1: 전체 그래프 ---
with tab1:
    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("📅 최근 30일 가입자 추이")
        if '가입일' in df.columns:
            ten_days_ago = pd.Timestamp.now() - pd.Timedelta(days=30)
            recent_df = df[df['가입일'] >= ten_days_ago]
            if not recent_df.empty:
                daily_counts = recent_df.groupby(recent_df['가입일'].dt.date).size().reset_index(name='가입자수')
                daily_counts.columns = ['날짜', '가입자수']
                fig_trend = px.line(daily_counts, x='날짜', y='가입자수', markers=True, text='가입자수', template=THEME_TEMPLATE)
                fig_trend.update_traces(line_color='#FF4B4B', textposition="bottom center")

                fig_trend.update_layout(
                    xaxis=dict(
                        rangeslider=dict(
                            visible=True,
                            thickness=0.05, # 슬라이더 두께를 아주 얇게 (기본은 0.15)
                            bgcolor="#F0F2F6" # 슬라이더 배경색을 연한 회색으로 변경
                        )
                    )
                )
                # 슬라이더 안의 데이터 숫자가 보기 싫다면 아래 설정 추가
                fig_trend.update_xaxes(rangeslider_visible=True)

                st.plotly_chart(fig_trend, use_container_width=True)
    
    with col_right:
        st.subheader("🏢 소속별 가입자 분포")
        if '소속' in df.columns:
            org_counts = df['소속'].value_counts().reset_index()
            org_counts.columns = ['소속', '인원수']
            fig_org = px.bar(org_counts, x='소속', y='인원수', color='소속', text='인원수', template=THEME_TEMPLATE, color_discrete_sequence=MY_COLORS)
            st.plotly_chart(fig_org, use_container_width=True)

# --- 탭 2: 초등 1~5학년 집계 리포트 ---
with tab2:
    st.subheader("🎯 초등 1~5학년 집계 리포트")
    st.caption("※ 2025-12-03(정식 오픈) 이후 데이터만 집계합니다.")

    if '가입일' in df.columns and '소속' in df.columns and '학년' in df.columns:
        
        target_grades = ['초1', '초2', '초3', '초4', '초5']
        start_date = pd.Timestamp('2025-12-03')
        
        filtered_df = df[
            (df['학년'].isin(target_grades)) & 
            (df['가입일'] >= start_date)
        ].copy()
        
        if filtered_df.empty:
            st.warning(f"⚠️ 2025-12-03 이후 가입한 '초1~초5' 회원이 없습니다.")
        else:
            # 1. 지점별 비중 표
            st.markdown("##### 1️⃣ 지점별 가입자 수 비중")
            branch_counts = filtered_df['소속'].value_counts()
            total_filtered = len(filtered_df)
            
            summary_data = {}
            for branch in branch_counts.index:
                count = branch_counts[branch]
                ratio = count / total_filtered
                summary_data[branch] = [f"{ratio:.0%}", f"{count:,}"] 
            
            summary_df = pd.DataFrame(summary_data, index=['비중', '가입자 수'])
            summary_df['합계'] = ['100%', f"{total_filtered:,}"]
            st.dataframe(summary_df, use_container_width=True)
            
            st.divider()

            # 2. 지점별 꺾은선
            st.markdown("##### 2️⃣ 지점별 신규 가입 추이")
            daily_branch_trend = filtered_df.groupby([filtered_df['가입일'].dt.date, '소속']).size().reset_index(name='가입자수')
            daily_branch_trend.columns = ['날짜', '소속', '가입자수']
            fig_line_branch = px.line(daily_branch_trend, x='날짜', y='가입자수', color='소속', markers=True,
                                      title="매일 신규 가입자 수 (지점별 비교)", template=THEME_TEMPLATE, color_discrete_sequence=MY_COLORS)
            fig_line_branch.update_traces(marker_size=8, line_width=2)
            
            st.plotly_chart(fig_line_branch, use_container_width=True)
            
            st.divider()

            # 3. 일별 상세 집계표
            st.markdown("##### 3️⃣ 일별 상세 집계표")
            filtered_df['날짜'] = filtered_df['가입일'].dt.strftime('%Y-%m-%d')
            pivot_df = filtered_df.pivot_table(index='날짜', columns='소속', values='이름', aggfunc='count', fill_value=0)
            pivot_df = pivot_df.sort_index(ascending=True)
            
            weekdays_map = {0:'월', 1:'화', 2:'수', 3:'목', 4:'금', 5:'토', 6:'일'}
            temp_dates = pd.to_datetime(pivot_df.index)
            pivot_df['요일'] = temp_dates.weekday.map(weekdays_map)
            
            numeric_cols = pivot_df.select_dtypes(include='number').columns
            pivot_df['일일 합계'] = pivot_df[numeric_cols].sum(axis=1)
            pivot_df['누적 합계'] = pivot_df['일일 합계'].cumsum()
            
            target_order = ['대치점', '잠실점', '서초점', '분당점', '온라인']
            for branch in target_order:
                if branch not in pivot_df.columns:
                    pivot_df[branch] = 0
            
            final_columns = ['요일'] + target_order + ['일일 합계', '누적 합계']
            pivot_df = pivot_df[final_columns]
            st.dataframe(pivot_df, use_container_width=True, height=500)
    else:
        st.error("필요한 컬럼이 부족합니다.")

# --- [수정 완료] 탭 3: 재원생 대비 가입 현황 ---
with tab3:
    st.subheader("📈 재원생 대비 누적 가입 현황 (참여율)")
    
    # [설정] 분석 대상 학년 고정
    target_grades = ['초1', '초2', '초3', '초4', '초5']
   
    if '가입일' in df.columns and '소속' in df.columns:
        start_date = pd.Timestamp('2025-12-03')
        
        # 1. 데이터 필터링: 초1~초5 학년이면서 12/3 이후 가입자만 추출
        sub_df = df[(df['학년'].isin(target_grades)) & (df['가입일'] >= start_date)].copy()
        
        # ----------------------------------------------------------------
        # [검산기] 초1~초5 기준 누적 확인
        # ----------------------------------------------------------------
        total_enrolled_sum = sum(TOTAL_STUDENTS.values()) 
        base_sum = sum(BASE_SUBSCRIBERS.values()) 
        new_signup_count = len(sub_df) 
        final_total_signup = base_sum + new_signup_count
        
        with st.expander("🧮 초1~초5 누적 가입자 확인", expanded=True):
            st.info("※ 본 수치는 초1~초5 학년 데이터만 필터링하여 계산되었습니다.")
            c1, c2, c3 = st.columns(3)
            c1.metric("1. 기존 가입자 (초1~5)", f"{base_sum:,}명")
            c2.metric("2. 신규 가입자 (초1~5)", f"{new_signup_count:,}명")
            c3.metric("3. 최종 누적 가입자", f"{final_total_signup:,}명")
        # ----------------------------------------------------------------

        sub_df['날짜'] = sub_df['가입일'].dt.strftime('%Y-%m-%d')
        
        # 일별 신규 누적 데이터 생성
        daily_cum = sub_df.groupby(['날짜', '소속']).size().unstack(fill_value=0)
        daily_cum = daily_cum.cumsum()
        
        target_branches = ['대치점', '잠실점', '서초점', '분당점', '온라인']
        for b in target_branches:
            if b not in daily_cum.columns:
                daily_cum[b] = 0
                
        # 기존 가입자(초1~5 기준) 합산
        for branch in target_branches:
            base_count = BASE_SUBSCRIBERS.get(branch, 0)
            daily_cum[branch] = daily_cum[branch] + base_count
            
        daily_cum = daily_cum[target_branches]

        # 2. 비율(%) 계산 (분모: 초1~초5 재원생 수)
        display_table = pd.DataFrame(index=daily_cum.index)
        ratio_data_list = []

        for branch in target_branches:
            total_std = TOTAL_STUDENTS.get(branch, 0) # 초1~5 재원생 수여야 함
            display_table[f'{branch}_가입'] = daily_cum[branch]
            display_table[f'{branch}_재원'] = total_std
            
            # 비율 계산 (분자/분모 모두 초1~5 한정)
            ratio_series = (daily_cum[branch] / total_std * 100).round(1) if total_std > 0 else 0
            display_table[f'{branch}_비중'] = ratio_series.apply(lambda x: f"{x}%")
            
            for date_idx, ratio_val in ratio_series.items():
                ratio_data_list.append({
                    '날짜': date_idx,
                    '지점': branch,
                    '참여율(%)': ratio_val
                })

        # 합계 계산
        daily_cum['전체_가입'] = daily_cum.sum(axis=1)
        display_table['합계_가입'] = daily_cum['전체_가입']
        display_table['합계_재원'] = total_enrolled_sum
        total_ratio = (daily_cum['전체_가입'] / total_enrolled_sum * 100).round(1)
        display_table['합계_비중'] = total_ratio.apply(lambda x: f"{x}%")

        # 시각화 및 테이블 출력
        # 4. [상단] 참여율 추이 그래프
        st.markdown("##### 🏆 지점별 참여율 도달 추이 및 현재 순위 (초1~5)")
        ratio_df = pd.DataFrame(ratio_data_list)
        
        # 꺾은선 그래프 생성 (기존 라벨링 제거하여 선을 깨끗하게 유지)
        fig_ratio = px.line(ratio_df, x='날짜', y='참여율(%)', color='지점', 
                            markers=True,
                            template=THEME_TEMPLATE, 
                            color_discrete_sequence=MY_COLORS)

        # [핵심] 2번 방법: 각 선의 오른쪽 끝(마지막 데이터)에만 수치 고정 라벨 추가
        last_date = ratio_df['날짜'].max()
        
        for i, branch in enumerate(target_branches):
            # 각 지점별 마지막 날짜의 수치 추출
            branch_last = ratio_df[(ratio_df['지점'] == branch) & (ratio_df['날짜'] == last_date)]
            
            if not branch_last.empty:
                val = branch_last['참여율(%)'].iloc[0]
                
                # 그래프 우측 끝에 텍스트 주석 추가
                fig_ratio.add_annotation(
                    x=last_date,
                    y=val,
                    text=f"<b>{val}%</b>", # 굵게 표시
                    showarrow=False,
                    xanchor="left", # 텍스트를 점 오른쪽에 배치
                    xshift=12,      # 점과의 간격
                    font=dict(
                        color=MY_COLORS[i % len(MY_COLORS)], # 선 색상과 일치
                        size=14
                    ),
                    bgcolor="rgba(255,255,255,0.8)" # 배경을 살짝 넣어 선과 겹쳐도 잘 보이게 함
                )

        # 차트 레이아웃 최적화
        fig_ratio.update_traces(line_width=3, marker_size=7)
        fig_ratio.update_layout(
            yaxis_ticksuffix="%",
            margin=dict(r=80), # 우측 숫자가 잘리지 않도록 여백 확보
            hovermode="x unified", # 마우스 오버 시 모든 지점 수치 비교 툴팁 제공
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1) # 범례를 상단으로 이동
        )
        
        st.plotly_chart(fig_ratio, use_container_width=True)        

        st.divider()
       
        st.markdown("##### 2️⃣ 일별 누적 상세표 (초1~5 한정)")

        # 표를 보기 좋게 날짜 내림차순(최신순)으로 정렬하여 표시
        display_table_sorted = display_table.sort_index(ascending=False)
        st.dataframe(display_table_sorted, use_container_width=True, height=500)

        # 엑셀(CSV) 다운로드 기능
        # 한국어 깨짐 방지를 위해 utf-8-sig 인코딩 사용
        csv = display_table_sorted.to_csv().encode('utf-8-sig')

        st.download_button(
            label="💾 상세표 엑셀 다운로드 (비교용)",
            data=csv,
            file_name=f"초등_참여율_상세현황_{pd.Timestamp.now().strftime('%m%d_%H%M')}.csv",
            mime="text/csv",
            help="다운로드한 파일을 엑셀에서 열어 수치를 비교해보세요."
        )


# --- 탭 4: 원본 데이터 ---
# with tab4:
#     st.subheader("📄 전체 데이터 리스트")
#     st.dataframe(df, use_container_width=True)