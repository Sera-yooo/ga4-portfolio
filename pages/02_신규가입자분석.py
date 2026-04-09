import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

# ==========================================
# CSS 설정
# ==========================================
from src.style_utils import apply_purple_theme
st.set_page_config(page_title="독서화랑 대시보드", layout="wide")
apply_purple_theme()

# ==========================================
# [설정] 페이지 설정
# ==========================================
st.set_page_config(page_title="회원 가입 분석 대시보드", page_icon="📈", layout="wide")

st.title("📈 독서화랑 가입 현황 대시보드")
st.caption("📅 데이터 기준: 2026년 3월 16일 (출처: 퍼팽 관리자 메뉴 > 관리부지점관리 > 2026 탭 인원 기준)")

# ==========================================
# [설정] 인쇄(PDF 저장) 시 그래프 잘림 방지 CSS
# ==========================================
st.markdown("""
    <style>
    @media print {
        /* 차트나 표 내부에서 페이지가 잘리지 않도록 방지 */
        .element-container, .stPlotlyChart, .stDataFrame {
            page-break-inside: avoid !important;
            break-inside: avoid !important;
        }
        /* 인쇄할 때 왼쪽 사이드바 숨기기 (공간 확보) */
        section[data-testid="stSidebar"] {
            display: none !important;
        }
        /* 상단 여백 조절 */
        .block-container {
            padding-top: 1rem !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# [데이터] 지점 순서 및 고정 색상 설정 (핵심 변경 포인트)
# -------------------------------------------------------------------
BRANCH_ORDER = ['대치점', '잠실점', '서초점', '분당점', '온라인']
MY_COLORS = ['#F2C744', '#88A61C', '#6BBEF2', '#BF2604', '#D9A59A']

# 지점명과 색상을 1:1로 매핑
BRANCH_COLOR_MAP = dict(zip(BRANCH_ORDER, MY_COLORS))

# -------------------------------------------------------------------
# [데이터] 논술화랑 재원생 상세 정보
# -------------------------------------------------------------------
# BRANCH_ORDER 순서에 맞춰서 딕셔너리 구성
STUDENT_DETAILS = {
    '대치점': {'초1': 167, '초2': 408, '초3': 513, '초4': 485, '초5': 367},
    '잠실점': {'초1': 112, '초2': 227, '초3': 347, '초4': 398, '초5': 283},
    '서초점': {'초1': 138, '초2': 284, '초3': 322, '초4': 214, '초5': 169},
    '분당점': {'초1': 82, '초2': 127, '초3': 129, '초4': 150, '초5': 131},
    '온라인': {'초1': 0, '초2': 203, '초3': 266, '초4': 268, '초5': 164}
}

TOTAL_STUDENTS = {branch: sum(grades.values()) for branch, grades in STUDENT_DETAILS.items()}
BASE_SUBSCRIBERS = {'대치점': 438, '잠실점': 230, '서초점': 258, '분당점': 124, '온라인': 99}

THEME_TEMPLATE = "plotly_white" 
NEW_SHEET_URL = "https://docs.google.com/spreadsheets/d/1gQ9kS_gVrcvDFA7cZEy6Ch5pSxRSbSwUaPX-ZwVUVV0/edit?usp=sharing"

# ==========================================
# [함수] 데이터 로드
# ==========================================
@st.cache_data(ttl=60)
def load_data():
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        sh = client.open_by_url(NEW_SHEET_URL)
        worksheet = sh.worksheet('가입자_RAW_DATA(신규)')        
        data = worksheet.get_all_values()
        
        if len(data) < 2: 
            return pd.DataFrame()
        
        header = data[0]
        seen = {}
        new_header = []
        for c in header:
            if c in seen:
                seen[c] += 1
                new_header.append(f"{c}_{seen[c]}")
            else:
                seen[c] = 0
                new_header.append(c)
                
        df = pd.DataFrame(data[1:], columns=new_header)
        
        if '가입일' in df.columns:
            df['가입일'] = pd.to_datetime(df['가입일'], errors='coerce')
        if '소속' in df.columns:
            df['소속'] = df['소속'].astype(str).str.strip().replace({
                '대치': '대치점', '잠실': '잠실점', '서초': '서초점', '분당': '분당점'
            })
            df = df[~df['소속'].isin(['x', 'X'])]
        if '학년' in df.columns:
            df['학년'] = df['학년'].astype(str).str.strip()
            
        return df
    except Exception as e:
        st.error(f"데이터 로드 오류: {e}\n\nStreamlit Secrets 설정이나 구글 시트 공유 권한을 확인해주세요.")
        return None

df = load_data()

if df is None:
    st.stop() 
elif df.empty:
    st.warning("구글 시트에 불러올 데이터가 없습니다.")
    st.stop()

# ==========================================
# [사이드바] 필터 설정
# ==========================================
st.sidebar.header("🔍 조회 조건")
date_range = st.sidebar.date_input("조회 기간", [datetime.date(2025, 12, 3), datetime.date(2026, 3, 16)])

all_grades = ['초1', '초2', '초3', '초4', '초5']
available_grades = [g for g in all_grades if g in df['학년'].unique()]
selected_grades = st.sidebar.multiselect("학년 선택", options=all_grades, default=available_grades)

if len(date_range) == 2:
    start_dt = pd.to_datetime(date_range[0])
    end_dt = pd.to_datetime(date_range[1])
    filtered_df = df[
        (df['가입일'] >= start_dt) & 
        (df['가입일'] <= end_dt) & 
        (df['학년'].isin(selected_grades))
    ].copy()
else:
    st.warning("조회 기간의 시작일과 종료일을 모두 선택해주세요.")
    st.stop()

# --- 지점별 데이터 집계 (BRANCH_ORDER 순서 강제 적용) ---
new_counts = filtered_df['소속'].value_counts()
branch_data = []
for b in BRANCH_ORDER:
    base = BASE_SUBSCRIBERS.get(b, 0)
    new = new_counts.get(b, 0)
    total_acc = base + new
    ratio = (total_acc / TOTAL_STUDENTS[b] * 100) if TOTAL_STUDENTS[b] > 0 else 0
    branch_data.append({'소속': b, '가입자': total_acc, '신규': new, '재원생': TOTAL_STUDENTS[b], '참여율': round(ratio, 1)})
branch_summary_df = pd.DataFrame(branch_data)

# ==========================================
# [TOP] 핵심 요약 지표 (KPI)
# ==========================================
st.subheader("📌 전체 가입 요약")

total_students_sum = sum(TOTAL_STUDENTS.values())
total_acc_sum = branch_summary_df['가입자'].sum()
total_new_sum = branch_summary_df['신규'].sum()
total_ratio_avg = (total_acc_sum / total_students_sum * 100) if total_students_sum > 0 else 0

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("전체 재원생", f"{total_students_sum:,}명")
kpi2.metric("총 가입자 (누적)", f"{total_acc_sum:,}명")
kpi3.metric("기간 내 신규 가입", f"{total_new_sum:,}명")
kpi4.metric("전체 참여율", f"{total_ratio_avg:.1f}%")

st.divider()

# ==========================================
# [본문] 시각화
# ==========================================

# 1. 소속별 가입자 분포 (누적 기준) & 지점별 참여율 표
col_a, col_b = st.columns(2)
with col_a:
    st.subheader("1. 지점별 누적 가입자 분포")
    fig1 = px.bar(branch_summary_df, x='소속', y='가입자', color='소속', text='가입자',
                  category_orders={'소속': BRANCH_ORDER}, 
                  color_discrete_map=BRANCH_COLOR_MAP, template=THEME_TEMPLATE)
    fig1.update_traces(textposition='outside')
    st.plotly_chart(fig1, use_container_width=True)

with col_b:
    st.subheader("지점별 재원생 대비 가입률 현황")
    display_df = branch_summary_df[['소속', '재원생', '가입자', '참여율']].copy()
    display_df.columns = ['지점명', '논술화랑 재원생 수', '독서화랑 가입자', '현재 참여율(%)']
    display_df['현재 참여율(%)'] = display_df['현재 참여율(%)'].apply(lambda x: f"{x}%")
    st.table(display_df)

st.divider()

# 2. 기간 내 소속별 신규 가입 분포 & 3. 일별 신규 가입자 추이
col_c, col_d = st.columns([1, 2])
with col_c:
    st.subheader("2. 기간 내 신규 가입 분포")
    # ✅ 수정된 부분: color='소속' 추가 및 update_traces(sort=False) 적용
    fig2 = px.pie(branch_summary_df, values='신규', names='소속', color='소속', hole=0.4,
                  category_orders={'소속': BRANCH_ORDER}, 
                  color_discrete_map=BRANCH_COLOR_MAP, template=THEME_TEMPLATE)
    fig2.update_traces(sort=False) 
    st.plotly_chart(fig2, use_container_width=True)

with col_d:
    st.subheader("3. 일별 신규 가입자 추이")
    
    # 1. 데이터 집계
    daily_trend = filtered_df.groupby([filtered_df['가입일'].dt.date, '소속']).size().reset_index(name='가입자수')
    
    # 2. 선 그래프 생성
    fig3 = px.line(daily_trend, x='가입일', y='가입자수', color='소속', markers=True,
                   category_orders={'소속': BRANCH_ORDER},
                   color_discrete_map=BRANCH_COLOR_MAP, template=THEME_TEMPLATE)

    # ✅ 3. X축 설정 (기본 자동 설정으로 복구)
    # 특정 간격(dtick)을 강제하지 않아 Plotly가 겹치지 않게 알아서 조절합니다.
    fig3.update_xaxes(
        type='date',
        hoverformat="%Y-%m-%d",
        showgrid=True,
        gridcolor="#F0F0F0"
    )

    # ✅ 4. 이벤트 라벨
    highlight_dates = [
        {"date": "2026-01-13", "text": "서초점 (1/13)", "color": "#51b8fe"},
        {"date": "2026-01-24", "text": "대치점 (1/24)", "color": "#fbc02d"},
        {"date": "2026-02-02", "text": "잠실점 (2/2)", "color": "#6d8d05"}
    ]

    # 라벨을 표시할 높이 (그래프 최대값 기준)
    y_max = daily_trend['가입자수'].max() if not daily_trend.empty else 100

    for item in highlight_dates:
        # 세로 점선
        fig3.add_vline(x=item["date"], line_width=1.5, line_dash="dash", line_color=item["color"])
        
        # 상단 텍스트 주석 (에러 났던 font_weight를 weight로 수정)
        fig3.add_annotation(
            x=item["date"],
            y=y_max,
            text=item["text"],
            showarrow=False,
            font=dict(size=12, color=item["color"], weight="bold"),
            bgcolor="rgba(255, 255, 255, 0.9)",
            bordercolor=item["color"],
            borderwidth=1,
            yshift=20
        )

    # ✅ 5. 레이아웃 마무리
    fig3.update_layout(
        margin=dict(t=100, b=50, l=10, r=10), # 상단 라벨이 잘리지 않게 여백 확보
        legend_title_text='지점별 소속',
        hovermode="x unified"
    )

    st.plotly_chart(fig3, use_container_width=True)

st.divider()

# 4. 참여율(%) 누적 도달 추이
st.subheader("4. 참여율(%) 누적 도달 추이")
sub_df = filtered_df.copy()
sub_df['날짜'] = sub_df['가입일'].dt.strftime('%Y-%m-%d')
daily_cum = sub_df.groupby(['날짜', '소속']).size().unstack(fill_value=0).cumsum()

ratio_list = []
for branch in BRANCH_ORDER:
    if branch not in daily_cum.columns: 
        daily_cum[branch] = 0
    series = (daily_cum[branch] + BASE_SUBSCRIBERS.get(branch, 0)) / TOTAL_STUDENTS[branch] * 100
    for d, v in series.items():
        ratio_list.append({'날짜': d, '지점': branch, '참여율': round(v, 1)})

fig4 = px.line(pd.DataFrame(ratio_list), x='날짜', y='참여율', color='지점', markers=True,
               category_orders={'지점': BRANCH_ORDER},
               color_discrete_map=BRANCH_COLOR_MAP, template=THEME_TEMPLATE)
fig4.update_layout(yaxis_ticksuffix="%")
st.plotly_chart(fig4, use_container_width=True)

st.divider()

# 5. 학년별 가입자 분포 (재원생 vs 기간 내 신규 가입자)
st.subheader("5. 학년별 재원생 대비 가입 현황 (기간 내)")

grade_student_total = []
for g in selected_grades:
    total_g = sum(STUDENT_DETAILS[branch].get(g, 0) for branch in BRANCH_ORDER)
    grade_student_total.append(total_g)

grade_new_counts = filtered_df['학년'].value_counts().reindex(selected_grades, fill_value=0).tolist()

fig5 = go.Figure()
fig5.add_trace(go.Bar(
    x=selected_grades, 
    y=grade_student_total,
    name='전체 재원생 (26.03.16 기준)',
    marker_color='#E5E5E5',
    text=grade_student_total,
    textposition='outside'
))
fig5.add_trace(go.Bar(
    x=selected_grades, 
    y=grade_new_counts,
    name='기간 내 신규 가입자',
    marker_color='#6BBEF2', 
    text=grade_new_counts,
    textposition='outside'
))

fig5.update_layout(
    barmode='group',
    template=THEME_TEMPLATE,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    yaxis_title="인원 수 (명)"
)
st.plotly_chart(fig5, use_container_width=True)