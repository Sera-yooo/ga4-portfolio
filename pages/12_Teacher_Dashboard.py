import streamlit as st
import pandas as pd
import plotly.express as px  # 👈 [추가] 차트용 모듈
from datetime import datetime, timedelta # 👈 [추가] 날짜 계산용 모듈

# ==========================================
# 1. 페이지 및 스타일 설정
# ==========================================
st.set_page_config(layout="wide", page_title="독서화랑 선생님 대시보드")

st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; }
    
    /* 💡 [수정] 모든 상단 카드의 높이를 200px로 고정하여 완벽하게 정렬! */
    .hero-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px; border-radius: 15px; color: white; text-align: center;
        box-shadow: 0 4px 6px rgba(118, 75, 162, 0.2); 
        min-height: 200px; /* 고정 높이 */
        display: flex; flex-direction: column; justify-content: center; align-items: center;
    }
    
    .metric-box {
        background: white; padding: 25px; border-radius: 15px; border: 1px solid #eaeaea;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02); 
        min-height: 200px; /* 고정 높이 */
        display: flex; flex-direction: column; justify-content: center;
    }
    
    .metric-label { font-size: 0.95rem; color: #64748B; font-weight: 600; margin-bottom: 15px; }
    .metric-val { font-size: 2.2rem; font-weight: 800; color: #1E293B; margin-bottom: 5px; }
    .class-row { display: flex; justify-content: space-between; font-size: 0.95rem; margin-bottom: 8px; color: #1E293B; }
    
    .sub-title { font-size: 1.3rem; font-weight: 800; color: #1E3A8A; margin-top: 35px; margin-bottom: 15px; border-left: 5px solid #764ba2; padding-left: 10px;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 통합 Mock Data (url을 내부 페이지 경로로 변경!)
# ==========================================
# 💡 url에 "11_Student_Dashboard?student=이름" 형태로 내부 상대 경로와 파라미터를 세팅했습니다.
full_student_db = [
    # 화 (16:00) 
    {"아바타": "👧🏻", "이름": "이하루", "반": "화 (16:00)", "현재 레벨": "Lv.9", "현재권수": 15, "상태": "✅ 독서화랑 이용", "마지막 접속일": "2026-03-24", "url": "11_Student_Dashboard?student=이하루"},
    {"아바타": "👦🏻", "이름": "김서휘", "반": "화 (16:00)", "현재 레벨": "Lv.7", "현재권수": 8,  "상태": "✅ 독서화랑 이용", "마지막 접속일": "2026-03-23", "url": "11_Student_Dashboard?student=김서휘"},
    {"아바타": "👧🏻", "이름": "강지아", "반": "화 (16:00)", "현재 레벨": "Lv.5", "현재권수": 3,  "상태": "🔴 가입 요망",     "마지막 접속일": "2026-03-10", "url": None},
    {"아바타": "👦🏻", "이름": "김시준", "반": "화 (16:00)", "현재 레벨": "Lv.8", "현재권수": 12, "상태": "🔴 가입 요망",     "마지막 접속일": "2026-03-22", "url": None},
    {"아바타": "👧🏻", "이름": "이시율", "반": "화 (16:00)", "현재 레벨": "Lv.10", "현재권수": 20, "상태": "✅ 독서화랑 이용", "마지막 접속일": "2026-03-24", "url": "11_Student_Dashboard?student=이시율"},
    
    # 화 (18:10)
    {"아바타": "👦🏻", "이름": "김지수", "반": "화 (18:10)", "현재 레벨": "Lv.16", "현재권수": 18, "상태": "✅ 독서화랑 이용", "마지막 접속일": "2026-03-24", "url": "11_Student_Dashboard?student=김지수"},
    {"아바타": "👦🏻", "이름": "김준우", "반": "화 (18:10)", "현재 레벨": "Lv.14", "현재권수": 22, "상태": "✅ 독서화랑 이용", "마지막 접속일": "2026-03-23", "url": "11_Student_Dashboard?student=김준우"},
    {"아바타": "👧🏻", "이름": "서채민", "반": "화 (18:10)", "현재 레벨": "Lv.15", "현재권수": 10, "상태": "✅ 독서화랑 이용", "마지막 접속일": "2026-03-24", "url": "11_Student_Dashboard?student=서채민"},
    {"아바타": "👧🏻", "이름": "이주하", "반": "화 (18:10)", "현재 레벨": "Lv.13", "현재권수": 5,  "상태": "🔴 가입 요망",     "마지막 접속일": "2026-03-15", "url": None},
    {"아바타": "👦🏻", "이름": "김민재", "반": "화 (18:10)", "현재 레벨": "Lv.17", "현재권수": 24, "상태": "✅ 독서화랑 이용", "마지막 접속일": "2026-03-24", "url": "11_Student_Dashboard?student=김민재"},

    # 금 (16:00)
    {"아바타": "👦🏻", "이름": "박진급", "반": "금 (16:00)", "현재 레벨": "Lv.20", "현재권수": 25, "상태": "✅ 독서화랑 이용", "마지막 접속일": "2026-03-24", "url": "11_Student_Dashboard?student=박진급"},
    {"아바타": "👦🏻", "이름": "조윤우", "반": "금 (16:00)", "현재 레벨": "Lv.19", "현재권수": 20, "상태": "✅ 독서화랑 이용", "마지막 접속일": "2026-03-23", "url": "11_Student_Dashboard?student=조윤우"},
    {"아바타": "👧🏻", "이름": "이도경", "반": "금 (16:00)", "현재 레벨": "Lv.18", "현재권수": 15, "상태": "✅ 독서화랑 이용", "마지막 접속일": "2026-03-24", "url": "11_Student_Dashboard?student=이도경"},
    {"아바타": "👦🏻", "이름": "김두원", "반": "금 (16:00)", "현재 레벨": "Lv.17", "현재권수": 8,  "상태": "🔴 가입 요망",     "마지막 접속일": "2026-03-12", "url": None},
    {"아바타": "👦🏻", "이름": "정희도", "반": "금 (16:00)", "현재 레벨": "Lv.21", "현재권수": 24, "상태": "✅ 독서화랑 이용", "마지막 접속일": "2026-03-24", "url": "11_Student_Dashboard?student=정희도"},

    # 금 (18:10)
    {"아바타": "👧🏻", "이름": "강리안", "반": "금 (18:10)", "현재 레벨": "Lv.11", "현재권수": 18, "상태": "✅ 독서화랑 이용", "마지막 접속일": "2026-03-24", "url": "11_Student_Dashboard?student=강리안"},
    {"아바타": "👦🏻", "이름": "장시윤", "반": "금 (18:10)", "현재 레벨": "Lv.10", "현재권수": 12, "상태": "✅ 독서화랑 이용", "마지막 접속일": "2026-03-23", "url": "11_Student_Dashboard?student=장시윤"},
    {"아바타": "👧🏻", "이름": "박연두", "반": "금 (18:10)", "현재 레벨": "Lv.9",  "현재권수": 5,  "상태": "✅ 독서화랑 이용", "마지막 접속일": "2026-03-24", "url": "11_Student_Dashboard?student=박연두"},
    {"아바타": "👦🏻", "이름": "이도윤", "반": "금 (18:10)", "현재 레벨": "Lv.12", "현재권수": 20, "상태": "🔴 가입 요망",     "마지막 접속일": "2026-03-20", "url": None},
    {"아바타": "👦🏻", "이름": "차시호", "반": "금 (18:10)", "현재 레벨": "Lv.11", "현재권수": 15, "상태": "✅ 독서화랑 이용", "마지막 접속일": "2026-03-24", "url": "11_Student_Dashboard?student=차시호"},
]

classes_info = {"화 (16:00)": 5, "화 (18:10)": 5, "금 (16:00)": 5, "금 (18:10)": 5}

st.title("👨‍🏫 Teacher Intelligence Dashboard")
st.divider()

# --- 상단 레이아웃 (카드 4개 나란히 배치) ---
# col_hero(프로필), col_m1(담당학생), col_m2(오늘활동), col_m3(미가입)
col_hero, col_m1, col_m2, col_m3 = st.columns(4)

with col_hero:
    st.markdown("""
        <div class="hero-card">
            <img src="https://api.dicebear.com/9.x/avataaars/svg?seed=TeacherKwak" width="70" style="border-radius: 50%; background: white; margin-bottom: 10px; border: 3px solid rgba(255,255,255,0.3);">
            <h3 style="margin: 0; font-weight:800; font-size:1.2rem;">박상아 선생님</h3>
            <p style="opacity: 0.9; font-size: 0.85rem; margin-top:5px;">샤갈반 전담</p>
        </div>
    """, unsafe_allow_html=True)

with col_m1:
    class_html = "".join([f'<div class="class-row"><span>📅 {k}</span> <b>{v}명</b></div>' for k, v in classes_info.items()])
    st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">👥 담당 학생 (총 20명)</div>
            <div style="margin-top: 5px; width: 100%;">{class_html}</div>
        </div>
    """, unsafe_allow_html=True)

with col_m2:
    st.markdown("""
        <div class="metric-box" style="border-left: 5px solid #22C55E;">
            <div class="metric-label">📖 오늘 활동 학생</div>
            <div class="metric-val">5명</div>
            <p style="color: #22C55E; font-size: 0.85rem; margin:0; font-weight:bold;">▲ 전일 대비 2명 증가</p>
        </div>
    """, unsafe_allow_html=True)

with col_m3:
    st.markdown("""
        <div class="metric-box" style="border-left: 5px solid #EF4444;">
            <div class="metric-label" style="color:#EF4444;">🚨 미가입 학생</div>
            <div class="metric-val" style="color:#EF4444;">4명</div>
            <p style="color: #64748B; font-size: 0.85rem; margin:0;">학부모 계정 연동 필요</p>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# 3.5 [추가] 클래스별 성과 분석 차트 & 업데이트 소식 (2분할 레이아웃)
# ==========================================
st.markdown('<div class="sub-title">1. 클래스별 성과 및 시스템 소식</div>', unsafe_allow_html=True)

# 💡 차트가 공간을 더 많이 차지하도록 2.5 : 1.5 비율로 나눕니다.
col_chart, col_notice = st.columns([2.5, 1.5])

with col_chart:
    with st.container(border=True):
        st.markdown('<div style="font-size: 0.95rem; color: #64748B; font-weight: 600; margin-bottom: 10px;">🚀 클래스별 레벨업 임박 학생 수 (15권 이상)</div>', unsafe_allow_html=True)
        
        # 💡 [핵심] 실제 데이터(full_student_db)에서 계산
        df_all = pd.DataFrame(full_student_db)
        # 15권 이상 읽은 학생만 필터링해서 반별로 카운트
        df_levelup = df_all[df_all["현재권수"] >= 15].groupby("반").size().reset_index(name="학생수")
        
        # 모든 반이 나오게 하기 위해 전체 반 리스트와 병합 (학생수 없는 반은 0)
        all_classes = pd.DataFrame({"반": list(classes_info.keys())})
        df_final = pd.merge(all_classes, df_levelup, on="반", how="left").fillna(0)

        fig = px.bar(df_final, x='반', y='학생수', color='학생수', text='학생수',
                     color_continuous_scale=['#E9D5FF', '#7E22CE'], # 연보라 -> 진보라
                     labels={'학생수': '인원(명)'})
    
        fig.update_layout(
            height=220, 
            margin=dict(l=0, r=0, t=30, b=0), 
            coloraxis_showscale=False,
            xaxis_title=None, 
            yaxis_title="학생 수(명)"
        )
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

with col_notice:
    with st.container(border=True):
        st.markdown('<div style="font-size: 0.95rem; color: #F59E0B; font-weight: 600; margin-bottom: 15px;">📢 독서화랑 업데이트 & 공지</div>', unsafe_allow_html=True)
        
        # 💡 공지사항 내용 (HTML로 깔끔하게 줄바꿈 및 디자인 적용)
        st.markdown("""
        <div style="font-size: 0.9rem; color: #1E293B; margin-bottom: 15px; line-height: 1.5;">
            <span style="color:#64748B; font-size:0.8rem;">2026.03.24</span>
            <b>[업데이트]</b> 초등 필독서 15권 신규 큐레이션 추가
        </div>
        <div style="font-size: 0.9rem; color: #1E293B; margin-bottom: 15px; line-height: 1.5;">
            <span style="color:#64748B; font-size:0.8rem;">2026.03.20</span>
            <b>[안내]</b> 서버 정기 점검 및 관리자 UI 개선
        </div>
        <div style="font-size: 0.9rem; color: #1E293B; line-height: 1.5;">
            <span style="color:#64748B; font-size:0.8rem;">2026.03.15</span>
            <b>[자료]</b> 3월 학부모 상담 가이드라인 PDF 배포
        </div>
        <div style="font-size: 0.9rem; color: #1E293B; line-height: 1.5;">
            <span style="color:#64748B; font-size:0.8rem;">2026.03.15</span>
            <b>[자료]</b> 3월 선생님 상담 가이드라인 PDF 배포
        </div>
        <div style="font-size: 0.9rem; color: #1E293B; margin-bottom: 15px; line-height: 1.5;">
            <span style="color:#64748B; font-size:0.8rem;">2026.03.24</span>
            <b>[업데이트]</b> 레벨12 10권 신규 도서 추가
        </div>                    
        """, unsafe_allow_html=True)

# ==========================================
# 4. [하단] 학생 독서 모니터링 및 분석 섹션 시작
# ==========================================
st.markdown('<div class="sub-title">2. 클래스별 학생 독서 모니터링</div>', unsafe_allow_html=True)

# 💡 [1단계] 반 선택을 먼저 해야 합니다.
selected_time = st.selectbox("조회할 반을 선택하세요", list(classes_info.keys()), index=0)

# 💡 [2단계] 선택된 반에 맞춰 데이터를 필터링합니다. (df_filtered 생성)
df_raw = pd.DataFrame(full_student_db)
df_filtered = df_raw[df_raw["반"] == selected_time].copy()
df_filtered["상세보기"] = "🔍 상세보기"

# 💡 [3단계] 이제 필터링된 df_filtered를 가지고 도넛 차트와 랭킹을 만듭니다.
col_donut, col_ranking = st.columns(2)

with col_donut:
    with st.container(border=True):
        st.markdown('📊 계정 가입 상태 분포')
        # ✅ Mock 데이터 [16, 4] 대신 실제 df_filtered에서 계산된 비율을 쓰면 더 정확합니다!
        status_dist = df_filtered["상태"].value_counts().reset_index()
        status_dist.columns = ["상태", "학생수"]
        
        fig_donut = px.pie(status_dist, values='학생수', names='상태', hole=0.6,
                           color_discrete_sequence=['#764BA2', '#D1D5DB'])
        fig_donut.update_layout(height=250, margin=dict(l=10, r=10, t=30, b=10), showlegend=False)
        st.plotly_chart(fig_donut, use_container_width=True)

# --- [우측] 명예의 전당  ---
with col_ranking:
    with st.container(border=True):
        st.markdown('<div style="font-size: 0.95rem; color: #64748B; font-weight: 600; margin-bottom: 10px;">🏆 우리 반 명예의 전당 (Top 3)</div>', unsafe_allow_html=True)
        
        if not df_filtered.empty:
            # 1. 데이터 복사 및 정렬용 숫자 추출
            df_rank = df_filtered.copy()
            df_rank["level_num"] = df_rank["현재 레벨"].str.extract('(\d+)').fillna(0).astype(int)
            
            # 2. 정렬 (권수 내림차순 -> 레벨 내림차순)
            df_rank = df_rank.sort_values(by=["현재권수", "level_num"], ascending=[False, False])
            top_3 = df_rank.head(3)
            
            # 3. 🏅 실제 화면에 출력하는 반복문
            for i, (idx, row) in enumerate(top_3.iterrows()):
                # 금, 은, 동 색상 세팅
                colors = ["#FFD700", "#C0C0C0", "#CD7F32"] 
                
                # 여기서부터가 진짜 화면을 그리는 HTML입니다!
                st.markdown(f"""
                <div style="display: flex; align-items: center; background: #F8FAFC; padding: 12px; border-radius: 10px; border: 1px solid #E2E8F0; margin-bottom: 8px;">
                    <div style="font-size: 1.5rem; color: {colors[i]}; font-weight: 800; width: 40px; text-align: center;">{i+1}</div>
                    <div style="font-size: 1rem; margin-left: 10px; font-weight: 600; color: #1E293B;">{row['이름']}</div>
                    <div style="margin-left: auto; text-align: right;">
                        <span style="font-size: 0.85rem; color: #764BA2; font-weight: 700;">{row['현재 레벨']}</span> | 
                        <span style="font-size: 0.85rem; color: #1E293B; font-weight: 800;">{row['현재권수']}권 완독</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.write("표시할 학생 데이터가 없습니다.")

# ==========================================
# 5. [하단] 학생 독서 모니터링 표 (현재 창 이동 기능 적용)
# ==========================================

df_raw = pd.DataFrame(full_student_db)
df_filtered = df_raw[df_raw["반"] == selected_time].copy()

# 💡 '상세보기' 컬럼을 가짜 데이터로 만들어 디자인만 유지합니다.
df_filtered["상세보기"] = "🔍 상세보기"

st.caption("💡 표 안의 학생 데이터를 클릭하면 현재 창에서 해당 학생의 상세 분석지로 즉시 이동합니다.")

with st.container(border=True):
    # event 변수로 테이블 클릭 이벤트를 감지합니다.
    event = st.dataframe(
        df_filtered[["아바타", "이름", "현재 레벨", "현재권수", "상태", "마지막 접속일", "상세보기"]],
        column_config={
            "아바타": st.column_config.TextColumn("", width="small"),
            "이름": st.column_config.TextColumn("이름", width="small"),
            "현재 레벨": st.column_config.TextColumn("현재 레벨", width="small"),
            "현재권수": st.column_config.ProgressColumn(
                "레벨업 진척도 (현재/목표)", format="%d / 21권", min_value=0, max_value=21,
            ),
            "상태": st.column_config.TextColumn("계정 연동 상태", width="medium"),
            "마지막 접속일": st.column_config.DateColumn("마지막 접속일", format="YYYY-MM-DD"),
            # 💡 LinkColumn 대신 TextColumn으로 텍스트만 보여줍니다.
            "상세보기": st.column_config.TextColumn("상세페이지 이동", width="medium") 
        },
        hide_index=True,
        use_container_width=True,
        on_select="rerun",           # 👈 행 클릭 시 앱을 재실행하며 이벤트 캡처
        selection_mode="single-row"  # 👈 한 번에 한 행만 선택 가능하도록 설정
    )

# 💡 [핵심] 테이블에서 클릭 이벤트가 발생했을 때 현재 창에서 이동하는 로직
if len(event.selection.rows) > 0:
    selected_idx = event.selection.rows[0]
    target_student = df_filtered.iloc[selected_idx]["이름"]
    
    # 1. 11번 페이지로 넘겨줄 학생 이름을 세션에 저장
    st.session_state['target_student'] = target_student
    
    # 2. 현재 창에서 11번 파일로 부드럽게 이동 (파일명은 실제 경로에 맞게 수정!)
    st.switch_page("pages/11_Student_Dashboard.py")

c1, c2, c3, c4 = st.columns([1.5, 1.5, 1, 1.5])
with c1:
    start_d = st.date_input("조회 시작일", datetime.now() - timedelta(days=30))
with c2:
    end_d = st.date_input("조회 종료일", datetime.now())
with c4:
    st.write("") # 버튼 위치를 아래로 살짝 내리기 위한 빈 공간
    # 현재 화면에 필터링된 데이터를 CSV로 변환
    csv = df_filtered.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 엑셀(CSV) 다운로드",
        data=csv,
        file_name=f"독서활동보고서_{selected_time}.csv",
        mime="text/csv",
        use_container_width=True
    )
st.write("") # 표와의 간격 띄우기