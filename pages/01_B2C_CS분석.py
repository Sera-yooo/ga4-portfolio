import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import plotly.express as px
import datetime

# ==========================================
# [설정] 페이지 설정
# ==========================================
st.set_page_config(page_title="일반 CS 통합 대시보드", page_icon="📞", layout="wide")
SHEET_URL = "https://docs.google.com/spreadsheets/d/1MQVn2jcKiHagQqUyyHR3ew9BLhD520Cv3UTwVMo5_6g/edit?usp=sharing"

@st.cache_data(ttl=60)
def load_all_data():
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        sh = client.open_by_url(SHEET_URL)
        
        def fetch(sheet_name, prefix):
            try:
                ws = sh.worksheet(sheet_name)
                data = ws.get_all_values()
                if len(data) < 5: return pd.DataFrame()
                df = pd.DataFrame(data[5:], columns=[c.strip() for c in data[4]])
                df = df[df['일시'].str.strip() != ''].dropna(subset=['일시'])
                for c in ['일시', '처리일']:
                    if c in df.columns:
                        df[c] = pd.to_datetime(df[c].str.replace('.', '-'), errors='coerce')
                if '처리일' in df.columns:
                    df['체류시간'] = (df['처리일'] - df['일시']).dt.total_seconds() / (86400)
                
                day_map = {0:'월', 1:'화', 2:'수', 3:'목', 4:'금', 5:'토', 6:'일'}
                df['요일'] = df['일시'].dt.dayofweek.map(day_map)
                
                df['데이터소스'] = prefix
                df['고유ID'] = prefix[0] + "_" + df.index.astype(str)
                return df
            except: return pd.DataFrame()

        df_merged = pd.concat([fetch("CS 접수기록(관리부)", "관리부"), fetch("CS 접수기록(선생님)", "선생님")], ignore_index=True)
        return df_merged
    except Exception as e:
        st.error(f"데이터 로드 오류: {e}")
        return pd.DataFrame()

df_raw = load_all_data()

# ==========================================
# [UI] 사이드바 및 필터
# ==========================================
with st.sidebar:
    st.title("🗂️ 조회 모드")
    target_mode = st.radio("데이터 범위", ["전체(통합)", "관리부", "선생님"])
    st.divider()
    start_date = st.date_input("시작일", datetime.date(2025, 12, 3))
    end_date = st.date_input("종료일", datetime.date.today())

start_dt, end_dt = pd.to_datetime(start_date), pd.to_datetime(end_date)
mask = (df_raw['일시'] >= start_dt) & (df_raw['일시'] <= end_dt)
if target_mode != "전체(통합)": mask &= (df_raw['데이터소스'] == target_mode)
df = df_raw.loc[mask].copy()

if df.empty:
    st.warning("데이터가 없습니다.")
    st.stop()

# 메인 타이틀
st.title(f"📞 일반 CS 통합 분석 [{target_mode}]")

# 탭 생성
tab1, tab2,tab3 = st.tabs(["📊 종합 분석 리포트", "🔎 개별 상세 조회","🔎 유형별 상세 조회"])

# ==========================================
# [탭 1] 종합 분석 리포트
# ==========================================
with tab1:
    # KPI 지표
    k1, k2, k3 = st.columns(3)
    k1.metric("총 접수", f"{len(df)}건")
    k2.metric("평균 처리 시간", f"{df['체류시간'].mean():.1f}일")
    k3.metric("최다 발생 이슈", df['카테고리'].value_counts().idxmax() if '카테고리' in df.columns else "-")

    st.divider()

    # 1. 히트맵 분석
    st.subheader("1. 🗺️ 접수-처리 집중도 분석 (Heatmap)")
    if '카테고리' in df.columns and '처리카테고리' in df.columns:
        ct = pd.crosstab(df['카테고리'], df['처리카테고리'])
        fig_heat = px.imshow(ct, text_auto=True, aspect="auto", color_continuous_scale="Reds")
        st.plotly_chart(fig_heat, use_container_width=True, key="chart_1")

    st.divider()

    # 2. 분포 분석
    st.subheader("2. 항목별 상세 분포")
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("##### 🏢 부서별 이슈 관여도")
        if '협업 부서' in df.columns:
            dept_cnt = df[df['협업 부서'].str.strip() != '']['협업 부서'].value_counts().reset_index(name='건수')
            fig_dept = px.bar(dept_cnt, x='건수', y='협업 부서', orientation='h', color_discrete_sequence=['#FF8C00'])
            st.plotly_chart(fig_dept, use_container_width=True, key="chart_2")

        st.markdown("##### 🍕 카테고리별 비중")
        if '카테고리' in df.columns:
            fig_pie = px.pie(df, names='카테고리', hole=0.3)
            st.plotly_chart(fig_pie, use_container_width=True, key="chart_3") 

    with col_b:
        st.markdown("##### 📅 요일별 접수량")
        if '요일' in df.columns:
            day_order = ['월', '화', '수', '목', '금', '토', '일']
            day_cnt = df['요일'].value_counts().reindex(day_order).reset_index(name='건수')
            day_cnt.columns = ['요일', '건수'] 
            fig_day = px.bar(day_cnt, x='요일', y='건수', color_discrete_sequence=['#A9A9A9'])
            st.plotly_chart(fig_day, use_container_width=True, key="chart_4")
            
        st.markdown("##### 🎓 학년별 이슈 분포")
        if '학년' in df.columns:
            grade_order = ['초1', '초2', '초3', '초4', '초5']
            fig_grade = px.bar(df, x='학년', color='카테고리', barmode='stack', 
                               category_orders={'학년': grade_order})
            st.plotly_chart(fig_grade, use_container_width=True, key="chart_5")
    # 3. 리스크 진단
    st.subheader("3. 🚨 서비스 안정성 진단")
    def classify_risk(val):
        val = str(val).strip()
        if val in ['시스템오류', '회원연동문제']: return '⛔ 심각 오류 (시스템/연동)'
        elif val == '컨텐츠오류': return '📉 컨텐츠오류'
        else: return '⚠️ 일반문의/기타'

    target_col = '처리카테고리' if '처리카테고리' in df.columns else '카테고리'
    df['리스크'] = df[target_col].apply(classify_risk)
    risk_cnt = df['리스크'].value_counts().reset_index(name='건수')
    fig_risk = px.pie(risk_cnt, values='건수', names='리스크', hole=0.5, 
                     color='리스크',
                     color_discrete_map={'⛔ 심각 오류 (시스템/연동)': '#FF4B4B', '📉 컨텐츠오류': '#FF8C00', '⚠️ 일반문의/기타': '#E0E0E0'})
    st.plotly_chart(fig_risk, use_container_width=True, key="chart_6")

# ==========================================
# [탭 2] 개별 상세 조회 (기존 탭 유지)
# ==========================================
with tab2:
    st.subheader("🔍 개별 건 상세 정보 열람")

    # 1. 필수 컬럼명 매칭 
    name_col = '이름' if '이름' in df.columns else ('학생명' if '학생명' in df.columns else '이름')
    branch_col = '지점' if '지점' in df.columns else ('소속지점' if '소속지점' in df.columns else '지점')
    collab_col = '협업 부서' if '협업 부서' in df.columns else ('협업부서' if '협업부서' in df.columns else '협업 부서')
    q_col = '문의 내용' if '문의 내용' in df.columns else '문의내용'
    a_col = '처리 내용' if '처리 내용' in df.columns else '처리내용'

    # 2. 조회 방식 선택
    search_method = st.radio("조회 방식 선택", ["카테고리 필터로 찾기", "학생 이름으로 검색"], horizontal=True)

    selected_row = None

    if search_method == "학생 이름으로 검색":
        search_name = st.text_input("👤 조회할 학생 이름을 입력하세요", placeholder="이름 입력 후 엔터")
        if search_name:
            name_history = df[df[name_col].str.strip() == search_name.strip()].copy()
            if not name_history.empty:
                st.success(f"✅ '{search_name}' 학생의 데이터 총 **{len(name_history)}**건을 찾았습니다.")
                name_history['display_label'] = (
                    name_history['일시'].dt.strftime('%Y-%m-%d') + " | " + 
                    name_history[branch_col].astype(str) + " | " +
                    name_history['카테고리']
                )
                selected_item = st.selectbox("📑 열람할 상담 건을 선택하세요", name_history['display_label'].tolist())
                selected_row = name_history[name_history['display_label'] == selected_item].iloc[0]
            else:
                st.error(f"❌ '{search_name}' 학생의 데이터가 조회 기간 내에 없습니다.")
    else:
        # 필터 UI
        f1, f2 = st.columns(2)
        with f1: 
            sel_in = st.selectbox("📥 접수 유형 필터", ["전체"] + sorted(df['카테고리'].astype(str).unique().tolist()))
        with f2: 
            sel_out = st.selectbox("📤 처리 결과 필터", ["전체"] + sorted(df['처리카테고리'].astype(str).unique().tolist()) if '처리카테고리' in df.columns else ["전체"])

        # 필터링 로직
        df_filtered = df.copy()
        if sel_in != "전체":
            df_filtered = df_filtered[df_filtered['카테고리'] == sel_in]
        if sel_out != "전체" and '처리카테고리' in df_filtered.columns:
            df_filtered = df_filtered[df_filtered['처리카테고리'] == sel_out]

        st.info(f"✅ 현재 조건으로 검색된 데이터: 총 **{len(df_filtered)}**건")

        if not df_filtered.empty:
            st.dataframe(df_filtered[['고유ID', '일시', branch_col, name_col, '카테고리', '처리 상태']].sort_values('일시', ascending=False), 
                         use_container_width=True, hide_index=True, height=200)
            
            st.markdown("---")
            selected_id = st.selectbox("📑 상세 정보를 열람할 '고유ID'를 선택하세요", ["선택하세요"] + df_filtered['고유ID'].tolist())
            if selected_id != "선택하세요":
                selected_row = df_filtered[df_filtered['고유ID'] == selected_id].iloc[0]

    # 3. 상세 카드 출력 영역 
    if selected_row is not None:
        row = selected_row
        status_bg = "#E1F5FE" if row.get('처리 상태') == "처리완료" else "#FFF9C4"
        
        q_text = str(row.get(q_col, '내용 없음')).replace("#", "＃").replace("[", "［").replace("]", "］")
        a_text = str(row.get(a_col, '기록 없음')).replace("#", "＃").replace("[", "［").replace("]", "］")
        
        dept_info = f"{row.get('데이터소스', '-')} ({row.get(branch_col, '-')})"
        collab_val = str(row.get(collab_col, '')).strip()
        collab_dept = collab_val if collab_val not in ['', 'nan', 'None'] else '없음'

        card_html = f"""
        <div style="background-color: white; border: 1px solid #E0E0E0; border-radius: 12px; padding: 25px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); margin-top: 15px; font-family: sans-serif; text-align: left;">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 20px; border-bottom: 2px solid #F5F5F5; padding-bottom: 15px;">
                <div>
                    <span style="background-color: #1976D2; color: white; padding: 3px 12px; border-radius: 4px; font-weight: bold; font-size: 13px;">{row[name_col]} 학생</span>
                    <h3 style="margin: 10px 0 5px 0; color: #333; font-size: 18px; font-weight: bold; border:none;">{row.get('카테고리', '미분류')}</h3>
                    <p style="margin: 0; color: #888; font-size: 13px;">📅 접수: {row['일시'].strftime('%Y-%m-%d %H:%M')} | 🏢 소속: <b>{dept_info}</b> | 🎓 학년: {row.get('학년','-')}</p>
                </div>
                <div style="background-color: {status_bg}; padding: 8px 25px; border-radius: 50px; font-weight: bold; color: #444; border: 1px solid #DDD; font-size: 14px;">{row.get('처리 상태', '상태없음')}</div>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div style="background-color: #FDF7F2; padding: 18px; border-radius: 8px; border-top: 4px solid #FF8C00;">
                    <strong style="color: #D35400; font-size: 14px;">🗣️ 접수/문의 내용</strong>
                    <div style="margin-top: 12px; line-height: 1.6; font-size: 14px !important; color: #444; min-height: 120px; white-space: pre-wrap; font-weight: 400;">{q_text}</div>
                </div>
                <div style="background-color: #F2F9F2; padding: 18px; border-radius: 8px; border-top: 4px solid #2ECC71;">
                    <strong style="color: #27AE60; font-size: 14px;">🛠️ 실제 처리/답변 내용</strong>
                    <div style="margin-top: 12px; line-height: 1.6; font-size: 14px !important; color: #444; min-height: 120px; white-space: pre-wrap; font-weight: 400;">{a_text}</div>
                </div>
            </div>
            <div style="margin-top: 20px; padding-top: 15px; border-top: 1px dashed #DDD; display: flex; justify-content: space-between; color: #666; font-size: 13px;">
                <div style="display: flex; gap: 20px;">
                    <div><b>최종 처리 유형:</b> <span style="color: #1976D2;">{row.get('처리카테고리', '미분류')}</span></div>
                    <div><b>🤝 협업 부서:</b> <span style="color: #E65100; font-weight: bold;">{collab_dept}</span></div>
                    <div><b>🏷️ 분류 유형:</b> <span style="color: #8E44AD; font-weight: bold;">{row.get('유형', '-')}</span></div>
                </div>
                <div><b>ID:</b> {row['고유ID']} | <b>처리 소요:</b> {round(row.get('체류시간', 0), 1)}일</div>
            </div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)

with tab3:
    st.subheader("🔍 유형별 건 상세 정보 열람")
    
    if '유형' in df.columns:
        # ==========================================
        # 1. 표와 그래프 (기간 필터 적용: df 사용)
        # ==========================================
        df['대분류'] = df['유형'].astype(str).str.strip().apply(
            lambda x: f"유형 {x[0]}" if len(x) > 0 and x[0].isdigit() else "미분류"
        )
        
        type_cat_cnt = df.groupby(['대분류', '유형']).size().reset_index(name='건수')
        total_cnt = len(df)
        
        # ZeroDivisionError 방지
        if total_cnt > 0:
            type_cat_cnt['비중(%)'] = (type_cat_cnt['건수'] / total_cnt * 100).round(1).astype(str) + "%"
        else:
            type_cat_cnt['비중(%)'] = "0%"
        
        type_cat_cnt = type_cat_cnt.sort_values(by=['대분류', '건수'], ascending=[True, False])
        type_cat_cnt.rename(columns={'대분류': '분류', '유형': '상세 유형'}, inplace=True)
        
        col_table, col_chart = st.columns([1, 1.2])
        
        with col_table:
            st.markdown("##### 📋 유형 및 상세 유형별 발생 비중 (조회 기간 내)")
            st.dataframe(type_cat_cnt.set_index(['분류', '상세 유형']), use_container_width=True)
            
        with col_chart:
            st.markdown("##### 📊 대분류별 상세 유형 누적 막대 그래프 (조회 기간 내)")
            
            fig_stacked = px.bar(
                type_cat_cnt, 
                x='분류', 
                y='건수', 
                color='상세 유형', 
                text='건수',
                barmode='stack',
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            
            fig_stacked.update_traces(textposition='inside', textfont=dict(color='white'))
            
            total_by_class = type_cat_cnt.groupby('분류')['건수'].sum().reset_index()
            if not total_by_class.empty:
                fig_stacked.add_scatter(
                    x=total_by_class['분류'], 
                    y=total_by_class['건수'], 
                    text='<b>' + total_by_class['건수'].astype(str) + '건</b>',
                    mode='text', 
                    textposition='top center', 
                    textfont=dict(size=14, color='#333333'), 
                    showlegend=False,
                    hoverinfo='skip'
                )
            
            max_y = total_by_class['건수'].max() * 1.15 if not total_by_class.empty else 10
            
            fig_stacked.update_layout(
                xaxis_title="대분류 (유형)", 
                yaxis_title="접수 건수",
                yaxis=dict(range=[0, max_y]),
                legend_title_text="상세 유형",
                margin=dict(l=20, r=20, t=30, b=20)
            )
            st.plotly_chart(fig_stacked, use_container_width=True, key="tab3_stacked_chart")
            
        st.divider()

        # ==========================================
        # 2. 유형별 상세 검색
        # ==========================================
        st.subheader("🔍 유형별 유형 상세 기록 검색")
        
        # 날짜 필터의 영향을 받지 않도록 원본 데이터(df_raw)를 사용
        df_search_base = df_raw.copy()
        
        # 부서(조회 모드) 필터는 그대로 유지
        if target_mode != "전체(통합)":
            df_search_base = df_search_base[df_search_base['데이터소스'] == target_mode]

        # 검색용 데이터에도 대분류 생성
        if '유형' in df_search_base.columns:
            df_search_base['대분류'] = df_search_base['유형'].astype(str).str.strip().apply(
                lambda x: f"유형 {x[0]}" if len(x) > 0 and x[0].isdigit() else "미분류"
            )

        name_col = '이름' if '이름' in df_search_base.columns else ('학생명' if '학생명' in df_search_base.columns else '이름')
        branch_col = '지점' if '지점' in df_search_base.columns else ('소속지점' if '소속지점' in df_search_base.columns else '지점')
        collab_col = '협업 부서' if '협업 부서' in df_search_base.columns else ('협업부서' if '협업부서' in df_search_base.columns else '협업 부서')
        q_col = '문의 내용' if '문의 내용' in df_search_base.columns else '문의내용'
        a_col = '처리 내용' if '처리 내용' in df_search_base.columns else '처리내용'

        col_f1, col_f2 = st.columns(2)
        with col_f1:
            sel_main_type = st.selectbox("📌 대분류 선택", ["전체"] + sorted(df_search_base['대분류'].unique().tolist()))
        
        available_sub_types = ["전체"]
        if sel_main_type != "전체":
            available_sub_types += sorted(df_search_base[df_search_base['대분류'] == sel_main_type]['유형'].unique().tolist())
        else:
            available_sub_types += sorted(df_search_base['유형'].unique().tolist())
            
        with col_f2:
            sel_sub_type = st.selectbox("🔖 상세 유형 선택", available_sub_types)

        # 사용자가 선택한 필터 적용
        df_type_filtered = df_search_base.copy()
        if sel_main_type != "전체":
            df_type_filtered = df_type_filtered[df_type_filtered['대분류'] == sel_main_type]
        if sel_sub_type != "전체":
            df_type_filtered = df_type_filtered[df_type_filtered['유형'] == sel_sub_type]

        st.info(f"✅ 현재 선택된 유형의 데이터 (전체 기간): 총 **{len(df_type_filtered)}**건")

        if not df_type_filtered.empty:
            st.dataframe(
                df_type_filtered[['고유ID', '일시', branch_col, name_col, '유형', '카테고리', '처리 상태']].sort_values('일시', ascending=False), 
                use_container_width=True, 
                hide_index=True, 
                height=200
            )
            
            st.markdown("---")
            selected_type_id = st.selectbox("📑 상세 기록을 열람할 '고유ID'를 선택하세요", ["선택하세요"] + df_type_filtered['고유ID'].tolist())
            
            if selected_type_id != "선택하세요":
                row = df_type_filtered[df_type_filtered['고유ID'] == selected_type_id].iloc[0]
                status_bg = "#E1F5FE" if row.get('처리 상태') == "처리완료" else "#FFF9C4"
                
                q_text = str(row.get(q_col, '내용 없음')).replace("#", "＃").replace("[", "［").replace("]", "］")
                a_text = str(row.get(a_col, '기록 없음')).replace("#", "＃").replace("[", "［").replace("]", "］")
                
                dept_info = f"{row.get('데이터소스', '-')} ({row.get(branch_col, '-')})"
                collab_val = str(row.get(collab_col, '')).strip()
                collab_dept = collab_val if collab_val not in ['', 'nan', 'None'] else '없음'

                card_html = f"""
                <div style="background-color: white; border: 1px solid #E0E0E0; border-radius: 12px; padding: 25px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); margin-top: 15px; font-family: sans-serif; text-align: left;">
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 20px; border-bottom: 2px solid #F5F5F5; padding-bottom: 15px;">
                        <div>
                            <span style="background-color: #8E44AD; color: white; padding: 3px 12px; border-radius: 4px; font-weight: bold; font-size: 13px;">{row.get('대분류', '-')}</span>
                            <span style="background-color: #1976D2; color: white; padding: 3px 12px; border-radius: 4px; font-weight: bold; font-size: 13px; margin-left: 5px;">{row[name_col]} 학생</span>
                            <h3 style="margin: 10px 0 5px 0; color: #333; font-size: 18px; font-weight: bold; border:none;">{row.get('유형', '미분류')} <span style="font-size: 14px; color: #666; font-weight: normal;">({row.get('카테고리', '-')})</span></h3>
                            <p style="margin: 0; color: #888; font-size: 13px;">📅 접수: {row['일시'].strftime('%Y-%m-%d %H:%M')} | 🏢 소속: <b>{dept_info}</b> | 🎓 학년: {row.get('학년','-')}</p>
                        </div>
                        <div style="background-color: {status_bg}; padding: 8px 25px; border-radius: 50px; font-weight: bold; color: #444; border: 1px solid #DDD; font-size: 14px;">{row.get('처리 상태', '상태없음')}</div>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                        <div style="background-color: #FDF7F2; padding: 18px; border-radius: 8px; border-top: 4px solid #FF8C00;">
                            <strong style="color: #D35400; font-size: 14px;">🗣️ 접수/문의 내용</strong>
                            <div style="margin-top: 12px; line-height: 1.6; font-size: 14px !important; color: #444; min-height: 120px; white-space: pre-wrap; font-weight: 400;">{q_text}</div>
                        </div>
                        <div style="background-color: #F2F9F2; padding: 18px; border-radius: 8px; border-top: 4px solid #2ECC71;">
                            <strong style="color: #27AE60; font-size: 14px;">🛠️ 실제 처리/답변 내용</strong>
                            <div style="margin-top: 12px; line-height: 1.6; font-size: 14px !important; color: #444; min-height: 120px; white-space: pre-wrap; font-weight: 400;">{a_text}</div>
                        </div>
                    </div>
                    <div style="margin-top: 20px; padding-top: 15px; border-top: 1px dashed #DDD; display: flex; justify-content: space-between; color: #666; font-size: 13px;">
                        <div style="display: flex; gap: 20px;">
                            <div><b>최종 처리 결과:</b> <span style="color: #1976D2;">{row.get('처리카테고리', '미분류')}</span></div>
                            <div><b>🤝 협업 부서:</b> <span style="color: #E65100; font-weight: bold;">{collab_dept}</span></div>
                        </div>
                        <div><b>ID:</b> {row['고유ID']} | <b>처리 소요:</b> {round(row.get('체류시간', 0), 1)}일</div>
                    </div>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)