import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import plotly.express as px
import plotly.graph_objects as go
import datetime
from prophet import Prophet

# 워드 클라우드용 라이브러리
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import platform

#한글깨짐 보완
import os
import urllib.request

# ==========================================
# [설정] 페이지 설정
# ==========================================
st.set_page_config(page_title="일반 CS 대시보드", page_icon="📞", layout="wide")

# -------------------------------------------------------------------
# [중요] 구글 시트 주소
# -------------------------------------------------------------------
SHEET_URL = "https://docs.google.com/spreadsheets/d/1MQVn2jcKiHagQqUyyHR3ew9BLhD520Cv3UTwVMo5_6g/edit?usp=sharing"
# -------------------------------------------------------------------

# ==========================================
# [함수] 데이터 로드 (시트 이름을 인자로 받음)
# ==========================================
@st.cache_data(ttl=60)
def load_data(target_sheet_name):
    try:
        # 1. 인증 및 연결
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        
        # --- 변경소스 ---
        # 파일 이름 대신 st.secrets에 저장한 딕셔너리를 직접 사용합니다.
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        # -----------------------
        
        client = gspread.authorize(creds)
        
        sh = client.open_by_url(SHEET_URL)
        
        # 선택된 시트 이름으로 접속
        try:
            worksheet = sh.worksheet(target_sheet_name)
        except gspread.exceptions.WorksheetNotFound:
            return None # 시트가 없으면 None 반환

        # 2. 데이터 가져오기
        raw_data = worksheet.get_all_values()
        
        if len(raw_data) < 5:
            return pd.DataFrame()

        # 5행 헤더, 6행 데이터
        header = raw_data[4]
        rows = raw_data[5:]
        
        df = pd.DataFrame(rows, columns=header)
        
        # 3. 데이터 청소
        df.columns = df.columns.str.strip()
        
        if '일시' in df.columns:
            df = df[df['일시'].str.strip() != '']
        else:
            return pd.DataFrame()

        # 4. 날짜 변환 (점. 제거 및 변환)
        def clean_date(col_name):
            if col_name in df.columns:
                df[col_name] = df[col_name].astype(str).str.replace('.', '-', regex=False)
                df[col_name] = pd.to_datetime(df[col_name], errors='coerce')

        clean_date('일시')
        clean_date('처리일')
        
        # 날짜 없는 행 제거
        df = df.dropna(subset=['일시'])

        # 5. 파생 변수 생성
        if '처리일' in df.columns:
            df['체류시간'] = (df['처리일'] - df['일시']).dt.total_seconds() / (60 * 60 * 24)
        
        if '일시' in df.columns:
            day_map = {0:'월', 1:'화', 2:'수', 3:'목', 4:'금', 5:'토', 6:'일'}
            df['요일'] = df['일시'].dt.dayofweek.map(day_map)
            
        return df

    except Exception as e:
        st.error(f"오류 발생: {e}")
        return pd.DataFrame()

# ==========================================
# [UI] 사이드바 (먼저 보여야 함)
# ==========================================
with st.sidebar:
    st.title("🗂️ 조회 대상 선택")
    
    # 1. 시트 선택 스위치 (라디오 버튼)
    target_mode = st.radio(
        "보고 싶은 데이터를 선택하세요",
        ["관리부", "선생님"],
        index=0 # 기본값: 관리부
    )
    
    # 선택에 따라 실제 시트 이름 매핑
    if target_mode == "관리부":
        sheet_name = "CS 접수기록(관리부)"
    else:
        sheet_name = "CS 접수기록(선생님)"
        
    st.divider()
    st.header("🔍 검색 필터")

# ==========================================
# [UI] 메인 로직
# ==========================================
st.title(f"📞 독서화랑 일반 CS ({target_mode})")

# 선택된 시트 이름으로 데이터 로드
with st.spinner(f"'{target_mode}' 데이터를 불러오는 중..."):
    df_raw = load_data(sheet_name)

# 시트가 없는 경우 처리
if df_raw is None:
    st.error(f"❌ '{sheet_name}' 시트를 찾을 수 없습니다! 구글 시트 탭 이름을 확인해주세요.")
    st.stop()

if df_raw.empty:
    st.warning("⚠️ 데이터가 비어있거나 날짜 형식이 맞지 않습니다.")
    st.stop()

# --- 사이드바 필터 (데이터 로드 후 설정) ---
with st.sidebar:
    # 날짜 범위 자동 인식
    min_date = df_raw['일시'].min().date()
    max_date = df_raw['일시'].max().date()
    
    start_date = st.date_input("시작일", min_date)
    end_date = st.date_input("종료일", max_date)
    
    # 학년 필터
    if '학년' in df_raw.columns:
        grades = sorted([g for g in df_raw['학년'].unique() if g and str(g).strip() != ''])
        selected_grades = st.multiselect("학년 선택", grades, default=grades)
    else:
        selected_grades = []

# --- 필터링 적용 ---
mask = (df_raw['일시'].dt.date >= start_date) & (df_raw['일시'].dt.date <= end_date)

if '학년' in df_raw.columns and selected_grades:
    mask = mask & (df_raw['학년'].isin(selected_grades))

df = df_raw.loc[mask]

# --- KPI 지표 ---
c1, c2, c3, c4 = st.columns(4)
c1.metric("총 접수", f"{len(df)}건")

unsolved = len(df[df['처리 상태'] != '처리완료']) if '처리 상태' in df.columns else 0
c2.metric("미처리", f"{unsolved}건", delta_color="inverse")

avg_time = df['체류시간'].mean() if '체류시간' in df.columns else 0
val_time = f"{avg_time:.1f}일" if pd.notnull(avg_time) else "-"
c3.metric("평균 처리 시간", val_time)

top_cat = df['카테고리'].value_counts().idxmax() if '카테고리' in df.columns and not df.empty else "-"
c4.metric("최다 발생 이슈", top_cat)

st.divider()

# --- 탭 구성 ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📊 종합 현황", "📈 상세 분석", "💡 건의사항 집중 분석", "🔮 미래 예측 (AI)", "📋 데이터 원본","🔍 키워드 맞춤 분석"])

# 탭 1: 종합 분석 (순서 변경: 상세표 -> 추이 -> 안전성 진단)
with tab1:
    # --------------------------------------------------------------------------------
    # [1] 상세 데이터 (접수 유형 vs 처리 유형) - 가장 먼저 팩트 체크!
    # --------------------------------------------------------------------------------
    st.subheader("📋 [상세 데이터] 접수 유형 vs 처리 유형")
    st.caption("현재 접수된 문의들의 유형별 교차 분석표입니다. (가로: 처리 결과 / 세로: 문의 주제)")
    
    if '카테고리' in df.columns and '처리카테고리' in df.columns:
        pivot = pd.crosstab(df['카테고리'], df['처리카테고리'], margins=True, margins_name="총 합계")
        # 히트맵 스타일 적용 (숫자가 클수록 진하게)
        st.dataframe(pivot.style.background_gradient(cmap="Reds", axis=None), use_container_width=True)
    else:
        st.info("카테고리 데이터가 부족하여 표를 생성할 수 없습니다.")

    st.divider()

    # --------------------------------------------------------------------------------
    # [2] 일반 현황 (부서별 관여도 & 일자별 추이)
    # --------------------------------------------------------------------------------
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("🏢 부서별 이슈 관여도")
        if '협업 부서' in df.columns:
            dept_df = df[df['협업 부서'].str.strip() != '']
            dept_cnt = dept_df['협업 부서'].value_counts().reset_index()
            dept_cnt.columns = ['부서', '건수']
            
            fig = px.bar(dept_cnt, x='건수', y='부서', orientation='h', text='건수',
                         color_discrete_sequence=['#FF8C00']) # 주황색
            fig.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
            
    with c2:
        st.subheader("📅 일자별 접수 추이")
        if not df.empty:
            daily = df.groupby(df['일시'].dt.date).size().reset_index(name='건수')
            fig_daily = px.bar(daily, x='일시', y='건수', color_discrete_sequence=['#A9A9A9']) # 회색
            st.plotly_chart(fig_daily, use_container_width=True)

    st.divider()

    # --------------------------------------------------------------------------------
    # [3] 서비스 안정성 진단 (Showstopper & Quality Risk) - 결론 및 경고
    # --------------------------------------------------------------------------------
    st.markdown("### 🚨 서비스 안정성 진단 ")
    
    # [리스크 분류 로직 개선]
    # 팀장님 의견 반영: 시스템/연동은 Showstopper, 컨텐츠는 Quality Issue로 분리
    def classify_risk(val):
        val = str(val).strip()
        
        # 1. Showstopper: 문이 안 열림 (가장 심각)
        if val in ['회원연동문제', '시스템오류']:
            return '⛔ Showstopper (진입/이용 불가)'
            
        # 2. Quality Issue: 보기에 안 좋음 (신뢰도 하락)
        elif val in ['컨텐츠오류']:
            return '📉 Quality Issue (신뢰도 하락)'
            
        # 3. General: 사용성 문제
        elif val in ['단순문의']:
            return '⚠️ 일반 문의 (사용성 불편)'
        else:
            return '기타'

    # 분석 기준열 설정
    target_col = '처리카테고리' if '처리카테고리' in df.columns else '카테고리'
    
    df['리스크_유형'] = df[target_col].apply(classify_risk)
    
    # 통계 계산
    risk_counts = df['리스크_유형'].value_counts()
    
    showstopper_count = risk_counts.get('⛔ Showstopper (진입/이용 불가)', 0)
    quality_count = risk_counts.get('📉 Quality Issue (신뢰도 하락)', 0)
    total_count = len(df)
    
    showstopper_ratio = (showstopper_count / total_count * 100) if total_count > 0 else 0

    # [핵심 메시지 박스]
    if showstopper_count > 0:
        st.error(f"""
        **심각한 장애(Showstopper) 발생 비율: {showstopper_ratio:.1f}% ({showstopper_count}건)**
        
        * **Showstopper:** 회원 연동 실패, 시스템 오류 등 서비스 진입 자체가 불가능한 치명적 결함
        * **Quality Issue:** 컨텐츠 오류 등 브랜드 신뢰도를 떨어뜨리는 품질 저하 ({quality_count}건)
        """)
    else:
        st.success("현재 Showstopper급 치명적 장애는 발견되지 않았습니다.")
    
    # [시각화]
    col_risk1, col_risk2 = st.columns([1, 1])
    
    with col_risk1:
        st.caption("📊 리스크 유형별 비중")
        risk_df = df['리스크_유형'].value_counts().reset_index()
        risk_df.columns = ['유형', '건수']
        
        fig_risk = px.pie(risk_df, values='건수', names='유형', hole=0.4,
                          color='유형',
                          color_discrete_map={
                              '⛔ Showstopper (진입/이용 불가)': '#FF4B4B',   # 빨강
                              '📉 Quality Issue (신뢰도 하락)': '#FF8C00', # 주황
                              '⚠️ 일반 문의 (사용성 불편)': '#FFCC00',     # 노랑
                              '기타': '#E0E0E0'
                          })
        st.plotly_chart(fig_risk, use_container_width=True)
        
    with col_risk2:
        st.caption("🔥 Showstopper & Quality 상세 내역")
        # 기타/일반문의 제외하고 진짜 문제들만 필터링
        critical_df = df[df['리스크_유형'].str.contains('Showstopper|Quality')]
        
        if not critical_df.empty:
            detail_counts = critical_df[target_col].value_counts().reset_index()
            detail_counts.columns = ['장애 내용', '건수']
            
            fig_detail = px.bar(detail_counts, x='건수', y='장애 내용', orientation='h',
                                text='건수', color='건수',
                                color_continuous_scale='Reds') 
            fig_detail.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_detail, use_container_width=True)
        else:
            st.info("표시할 장애 상세 내역이 없습니다.")

# 탭 2: 상세 분석 + 워드 클라우드
with tab2:
    r1_1, r1_2 = st.columns(2)
    with r1_1:
        st.subheader("카테고리별 비중")
        if '카테고리' in df.columns:
            cat_cnt = df['카테고리'].value_counts().reset_index()
            cat_cnt.columns = ['카테고리', '건수']
            fig_pie = px.pie(cat_cnt, values='건수', names='카테고리', hole=0.3)
            st.plotly_chart(fig_pie, use_container_width=True)
    with r1_2:
        st.subheader("요일별 접수량")
        if '요일' in df.columns:
            order = ['월', '화', '수', '목', '금', '토', '일']
            day_cnt = df['요일'].value_counts().reindex(order).reset_index()
            day_cnt.columns = ['요일', '건수']
            fig_day = px.bar(day_cnt, x='요일', y='건수', color='건수')
            st.plotly_chart(fig_day, use_container_width=True)
            
    st.subheader("학년별 이슈 분포")
    if '학년' in df.columns and '카테고리' in df.columns:
        grade_cat = df.groupby(['학년', '카테고리']).size().reset_index(name='건수')
        grade_cat = grade_cat.sort_values('학년')
        fig_stack = px.bar(grade_cat, x='학년', y='건수', color='카테고리', barmode='stack')
        st.plotly_chart(fig_stack, use_container_width=True)

    st.divider()
    st.subheader("☁️ 문의 내용 키워드 분석 (Word Cloud)")
    
    text_data = ""
    if '문의 내용' in df.columns:
        text_data = " ".join(df['문의 내용'].astype(str))
    elif '문의내용' in df.columns:
        text_data = " ".join(df['문의내용'].astype(str))
    elif '카테고리' in df.columns:
        text_data = " ".join(df['카테고리'].astype(str))
    
    if text_data.strip():
        # 1. [핵심] 제거할 단어 리스트 만들기 (불용어)
        # 여기에 보기 싫은 단어를 계속 추가하시면 됩니다!
        stop_words = {
            "합니다", "부탁드립니다", "문의주셨습니다", "확인부탁드립니다", 
            "안녕하세요", "감사합니다", "주셨습니다", "대해", "관련", 
            "확인", "부탁", "드립니다", "있는", "있습니다", "하는", 
            "문의", "내용", "건으로", "대한", "드립니다","독서화랑","충돌","이해","비판","어머니께서"
        }

        font_file = "NanumGothic.ttf"
        if not os.path.exists(font_file):
            url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf"
            urllib.request.urlretrieve(url, font_file)
            
        try:
            wc = WordCloud(
                font_path=font_file,
                width=1000, height=500,
                background_color='white',
                colormap='viridis',
                max_words=100,
                stopwords=stop_words  # <--- [핵심] 여기에 제거 리스트 적용!
            ).generate(text_data)
            
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.imshow(wc, interpolation='bilinear')
            ax.axis('off')
            st.pyplot(fig)
            
        except Exception as e:
            st.error(f"워드 클라우드 에러: {e}")
    else:
        st.info("분석할 텍스트 데이터가 부족합니다.")

# 탭 3: 건의사항 집중 분석 
with tab3:
    st.subheader("💡 고객 건의사항 리스트")
    
    # 1. 데이터 필터링 ([건의사항] 카테고리만)
    if '카테고리' in df.columns:
        # 카테고리 매칭 정확히 수행
        suggestion_df_all = df[df['카테고리'] == '[건의사항]'].copy()
        content_col = '문의 내용' if '문의 내용' in suggestion_df_all.columns else '문의내용'
        
        if not suggestion_df_all.empty:
            # 2. 버튼형 필터 구성 (처리 상태)
            status_options = ["전체"] + sorted(suggestion_df_all['처리 상태'].unique().tolist())
            
            # 버튼 형태로 필터 배치
            selected_status = st.radio(
                "🚦 처리 상태 필터",
                status_options,
                horizontal=True  # 버튼을 가로로 배치
            )
            
            # 필터링 적용
            if selected_status == "전체":
                display_df = suggestion_df_all
            else:
                display_df = suggestion_df_all[suggestion_df_all['처리 상태'] == selected_status]

            # 3. 검색 결과 건수 표시
            st.markdown(f"🔍 검색된 데이터: **{len(display_df)}**건")
            st.divider()

            # 4. 3열 그리드 레이아웃
            display_df = display_df.sort_values('일시', ascending=False)
            
            cols = st.columns(3)
            
            for idx, (_, row) in enumerate(display_df.iterrows()):
                with cols[idx % 3]:
                    date_str = row['일시'].strftime('%Y-%m-%d')
                    status = row.get('처리 상태', '미정')
                    proc_cat = row.get('처리카테고리', '미분류')
                    
                    # 상태별 색상 설정
                    status_bg = '#d4edda' if status == '처리완료' else '#fff3cd'
                    status_text = '#155724' if status == '처리완료' else '#856404'

                    # 카드 UI 구성
                    st.markdown(f"""
                    <div style="
                        border: 1px solid #e6e9ef; 
                        border-radius: 10px; 
                        padding: 15px; 
                        margin-bottom: 20px; 
                        background-color: #ffffff;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                        min-height: 250px;
                    ">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                            <span style="color: #888; font-size: 0.8em; font-weight: 500;">📅 {date_str}</span>
                            <span style="
                                background-color: {status_bg}; 
                                color: {status_text}; 
                                padding: 2px 10px; 
                                border-radius: 15px; 
                                font-size: 0.75em; 
                                font-weight: bold;
                            ">{status}</span>
                        </div>
                        <div style="
                            font-size: 0.95em; 
                            line-height: 1.6; 
                            color: #333; 
                            height: 110px;
                            overflow-y: auto;
                            white-space: pre-wrap;
                            margin-bottom: 12px;
                            padding-right: 5px;
                        ">
                            {row[content_col]}
                        </div>
                        <div style="border-top: 1px solid #f3f4f6; padding-top: 10px; display: flex; align-items: center;">
                            <span style="color: #007bff; font-size: 0.8em; font-weight: bold;">🏷️ {proc_cat}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("현재 조건에 맞는 '[건의사항]' 데이터가 없습니다.")
    else:
        st.error("'카테고리' 컬럼을 찾을 수 없습니다.")
# 탭 4: 미래 예측 (NEW!)
with tab4:
    st.subheader("🔮 향후 30일 CS 인입량 예측")
    st.markdown("과거 데이터를 학습하여 **향후 30일간의 CS 접수량**을 예측합니다.")
    
    # 데이터 준비 (Prophet은 ds, y 컬럼이 필요함)
    # 전체 기간 데이터를 사용해야 학습이 잘 되므로 df_raw를 사용
    if not df_raw.empty:
        # 일별 데이터로 묶기
        prophet_df = df_raw.groupby(df_raw['일시'].dt.date).size().reset_index(name='y')
        prophet_df.columns = ['ds', 'y'] # Prophet 규칙: 날짜=ds, 값=y
        
        # 데이터가 너무 적으면 경고
        if len(prophet_df) < 10:
            st.warning("⚠️ 예측을 하기에는 데이터가 너무 적습니다. (최소 10일 이상 필요)")
        else:
            with st.spinner("AI가 데이터를 학습하고 있습니다... (Prophet)"):
                # 1. 모델 생성 및 학습
                m = Prophet()
                m.fit(prophet_df)
                
                # 2. 미래 날짜 생성 (30일)
                future = m.make_future_dataframe(periods=30)
                
                # 3. 예측 수행
                forecast = m.predict(future)
                
                # 4. 시각화 (Plotly로 예쁘게 그리기)
                fig_forecast = go.Figure()
                
                # (1) 실제 데이터 점 찍기
                fig_forecast.add_trace(go.Scatter(
                    x=prophet_df['ds'], y=prophet_df['y'],
                    mode='markers', name='실제 데이터',
                    marker=dict(color='gray', size=8)
                ))
                
                # (2) 예측 선 그리기
                fig_forecast.add_trace(go.Scatter(
                    x=forecast['ds'], y=forecast['yhat'],
                    mode='lines', name='예측(Trend)',
                    line=dict(color='blue', width=2)
                ))
                
                # (3) 예측 범위 (불확실성) 그리기 (투명하게)
                fig_forecast.add_trace(go.Scatter(
                    x=forecast['ds'].tolist() + forecast['ds'][::-1].tolist(),
                    y=forecast['yhat_upper'].tolist() + forecast['yhat_lower'][::-1].tolist(),
                    fill='toself',
                    fillcolor='rgba(0,0,255,0.2)',
                    line=dict(color='rgba(255,255,255,0)'),
                    name='예측 범위',
                    showlegend=False
                ))
                
                st.plotly_chart(fig_forecast, use_container_width=True)
                
                st.info("💡 **파란 선**이 앞으로 예상되는 CS 건수입니다. (회색 점은 실제 과거 데이터)")
                
                # (선택) 예측 데이터 표로 보여주기
                st.write("▼ 날짜별 예측 수치")
                forecast_show = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(30)
                forecast_show['ds'] = forecast_show['ds'].dt.date
                forecast_show.columns = ['날짜', '예측 건수', '최소 예상', '최대 예상']
                st.dataframe(forecast_show)

# 탭 5: 원본 데이터
with tab5:
    df_display = df.copy()
    df_display['일시'] = df_display['일시'].dt.strftime('%Y. %m. %d')
    if '처리일' in df_display.columns:
        df_display['처리일'] = df_display['처리일'].apply(lambda x: x.strftime('%Y. %m. %d') if pd.notnull(x) else "")
        
    st.dataframe(df_display.sort_values('일시', ascending=False), use_container_width=True)

with tab6:
    st.subheader("🔍 키워드 맞춤 분석")
    st.markdown("띄어쓰기와 상관없이 핵심 단어를 검색합니다. (예: '지성의 별'과 '지성의별' 모두 검색)")

    # 1. 사용자가 직접 키워드를 추가할 수 있도록 입력창 제공
    # 기본값으로 '완독'과 '지성의별'을 설정
    user_keywords = st.text_input("분석하고 싶은 키워드들을 쉼표(,)로 구분해서 입력하세요", "완독, 지성의별")
    target_keywords = [kw.strip() for kw in user_keywords.split(",") if kw.strip()]

    content_col = '문의 내용' if '문의 내용' in df.columns else '문의내용'

    if content_col in df.columns:
        keyword_data = []
        for kw in target_keywords:
            # [핵심] 띄어쓰기 무시 로직 (Regex 사용)
            # 단어 사이의 모든 공백을 제거한 패턴을 생성하여 검색
            clean_kw = kw.replace(" ", "")
            regex_pattern = r"\s*".join(list(clean_kw)) # '지', '성', '의', '별' 사이에 공백 허용 패턴
            
            # 패턴 설명: '지'와 '성' 사이에 공백(\s*)이 있어도 되고 없어도 됨
            filtered_df = df[df[content_col].str.contains(regex_pattern, na=False, case=False, regex=True)]
            
            keyword_data.append({"키워드": kw, "건수": len(filtered_df), "데이터": filtered_df})

        # 2. 요약 지표 (상단 카드)
        kpi_cols = st.columns(len(keyword_data))
        for i, data in enumerate(keyword_data):
            kpi_cols[i].metric(f"'{data['키워드']}' 검색 결과", f"{data['건수']}건")

        st.divider()

        # 3. 상세 리스트 확인
        if target_keywords:
            selected_kw = st.selectbox("리스트를 확인할 키워드 선택", target_keywords)
            selected_data = next(item['데이터'] for item in keyword_data if item['키워드'] == selected_kw)

            if not selected_data.empty:
                st.write(f"▼ '{selected_kw}' 관련 문의 상세 내역 (총 {len(selected_data)}건)")
                
                # 가독성을 위해 날짜 및 주요 컬럼 정리
                display_kw_df = selected_data.copy()
                display_kw_df['일시'] = display_kw_df['일시'].dt.strftime('%Y-%m-%d')
                
                show_cols = ['일시', content_col, '카테고리', '처리 상태']
                avail = [c for c in show_cols if c in display_kw_df.columns]
                
                st.dataframe(display_kw_df[avail].sort_values('일시', ascending=False), use_container_width=True)
            else:
                st.info(f"'{selected_kw}'와(과) 관련된 문의가 없습니다.")
    else:
        st.error("데이터에서 문의 내용 컬럼을 찾을 수 없습니다.")