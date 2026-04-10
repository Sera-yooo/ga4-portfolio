import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

# ==========================================
# CSS 설정
# ==========================================
import src.style_utils as style
st.set_page_config(page_title="독서화랑 대시보드", layout="wide")
style.apply_common_style()

# ==========================================
# 1. 페이지 및 기본 설정
# ==========================================
st.set_page_config(layout="wide", page_title="독서화랑 학생 상세 대시보드")

st.markdown("""
    <style>
    .main-title { font-size: 32px; font-weight: 800; color: #1E3A8A; margin-bottom: 5px; }
    .sub-title { font-size: 20px; font-weight: 700; color: #2C3E50; margin-top: 30px; border-bottom: 2px solid #E5E7EB; padding-bottom: 10px; margin-bottom: 20px;}
    .profile-card { background-color: #F8FAFC; border-radius: 15px; padding: 20px; text-align: center; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); }
    .profile-avatar { font-size: 60px; line-height: 1; margin-bottom: 10px; }
    .profile-name { font-size: 24px; font-weight: bold; color: #1E293B; margin: 0; }
    .profile-info { font-size: 14px; color: #64748B; margin-top: 5px; }
    .info-row { display: flex; justify-content: space-between; font-size: 14px; margin-top: 10px; border-bottom: 1px dashed #E2E8F0; padding-bottom: 5px;}
    .info-label { color: #64748B; font-weight: 600; }
    .info-value { color: #0F172A; font-weight: 500; }
    .activity-card { 
        background-color: #FFF9F0; 
        border-radius: 12px; 
        padding: 15px 10px; 
        text-align: center; 
        border: 1px solid #FDF2E9; 
        margin-top: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .activity-icon { font-size: 28px; margin-bottom: 5px; }
    .activity-title { font-size: 14px; font-weight: 600; color: #52525B; margin-bottom: 5px; }
    .activity-value { font-size: 22px; font-weight: 800; color: #18181B; }            
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📚 독서화랑 학생 상세 관리</div>', unsafe_allow_html=True)

# ==========================================
# 2. 학생 딕셔너리 DB (Mock Data) - 재원 여부 추가
# ==========================================
student_db = {
    "이하루 (초2)": {
        "학부모아이디": "haru_mom", "아이디": "haru_lee", "이름": "이하루", "닉네임": "하루하루", "전화번호": "010-1234-5678", 
        "소속": "서초점", "학교": "서래초", "학년": "초2", "성별": "여자", "아바타": "👧🏻",
        "마지막이용날짜": "2026-01-12", "현재도서레벨": "Lv.9", 
        "총완독도서수": 15, "현재레벨_완독도서": 8, "레벨업_목표도서": 21, 
        "정독단계": "2단계", "정독_최초레벨": "Lv.7", "정독_회원등급": "새싹독서",
        "has_jeongdok": True, "has_tamheom": False,
        "논술재원여부": True # 💡 재원생
    },
    "김지수 (초4)": {
        "학부모아이디": "kmsecret", "아이디": "jisu_k", "이름": "김지수", "닉네임": "지수스타", "전화번호": "010-8030-2476", 
        "소속": "대치점", "학교": "대치초", "학년": "초4", "성별": "여자", "아바타": "👩🏻‍🎓",
        "마지막이용날짜": "2026-02-28", "현재도서레벨": "Lv.16", 
        "총완독도서수": 45, "현재레벨_완독도서": 5, "레벨업_목표도서": 25,
        "다독_최초레벨": "Lv.16", "보유금화": 120, "지성의별": 350,
        "has_jeongdok": False, "has_tamheom": True,
        "논술재원여부": False # 💡 비재원생
    },
    "박진급 (초4)": {
        "학부모아이디": "jin_park", "아이디": "jin_park", "이름": "박진급", "닉네임": "진급왕", "전화번호": "010-5555-7777", 
        "소속": "분당점", "학교": "분당초", "학년": "초4", "성별": "남자", "아바타": "👦🏻",
        "마지막이용날짜": "2026-03-13", "현재도서레벨": "Lv.20", 
        "총완독도서수": 70, "현재레벨_완독도서": 5, "레벨업_목표도서": 25,
        "정독단계": "7단계", "정독_최초레벨": "Lv.10", "정독_회원등급": "나무독서",
        "다독_최초레벨": "Lv.19", "보유금화": 40, "지성의별": 450,
        "has_jeongdok": True, "has_tamheom": True,
        "논술재원여부": True # 💡 재원생
    }
}

# ==========================================
# 3. 최상단: 학생 검색 컨트롤 패널 - 박진급 기본 선택
# ==========================================
with st.container(border=True):
    col_icon, col_sel = st.columns([0.5, 9.5])
    with col_icon:
        st.markdown("<h2 style='margin:0; padding-top:20px; text-align:center;'>🔍</h2>", unsafe_allow_html=True)
    with col_sel:
        # 💡 박진급(초4)를 기본값으로 선택하기 위해 index 설정
        student_keys = list(student_db.keys())
        default_idx = student_keys.index("박진급 (초4)")
        
        selected_key = st.selectbox("조회할 학생을 검색하세요", student_keys, index=default_idx)
        data = student_db[selected_key] 

# 신호등 뱃지 계산
last_date = datetime.strptime(data["마지막이용날짜"], "%Y-%m-%d")
days_passed = (datetime(2026,3,13) - last_date).days
if days_passed <= 7:
    status_badge = "🟢 안정 (최근 접속)"
elif days_passed <= 14:
    status_badge = "🟡 주의 (접속 뜸함)"
else:
    status_badge = "🔴 위험 (이탈 의심)"

# ==========================================
# 4. 화면 레이아웃 구성
# ==========================================
st.markdown('<div class="sub-title">1. 통합 고객 정보 및 진척도</div>', unsafe_allow_html=True)

# 🚨 [새로운 방식] 가로형 전체 너비 CS 알림 배너
st.markdown("""
    <div style="cursor: pointer; padding: 12px 20px; margin-bottom: 20px; border-radius: 8px; background-color: #FFF1F2; border: 1px solid #FDA4AF; display: flex; justify-content: space-between; align-items: center;">
        <div style="display: flex; align-items: center; gap: 15px;">
            <span style="font-size: 16px;">🚨 <b>최근 상담 요약</b></span>
            <span style="background-color: #E11D48; color: white; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold;">완독/활동 오류</span>
            <span style="font-size: 15px; color: #1E293B; font-weight: 600;">10권 읽었으나 8권만 완독 처리됨...</span>
        </div>
        <div style="display: flex; align-items: center; gap: 15px;">
            <span style="font-size: 13px; color: #94A3B8;">2026-03-14 | 담당자A</span>
            <span style="font-size: 14px; color: #E11D48; font-weight: 800;">⚠️ 접수/대기</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# 원래의 예쁜 3단 기둥 복구
col_profile, col_metrics, col_chart = st.columns([1.2, 1, 1.5])

# 1️⃣ 왼쪽: 프로필
with col_profile:
    st.markdown(f"""
        <div class="profile-card">
            <div class="profile-avatar">{data['아바타']}</div>
            <p class="profile-name">{data['이름']}</p>
            <p class="profile-info">{data['학교']} | {data['학년']} | {data['소속']}</p>
            <div style="margin-top:20px;">
                <div class="info-row"><span class="info-label">아이디</span><span class="info-value">{data['아이디']}</span></div>
                <div class="info-row"><span class="info-label">닉네임</span><span class="info-value">{data['닉네임']}</span></div>
                <div class="info-row"><span class="info-label">보호자 연락처</span><span class="info-value">{data['전화번호']}</span></div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("") 
    q1, q2, q3 = st.columns(3)
    q1.button("📄 리포트", use_container_width=True)
    q2.button("🪙 금화전송", use_container_width=True)
    q3.button("⚙️ 수정", use_container_width=True)

# 2️⃣ 중앙: 핵심 지표 (다시 딱 3개만!)
with col_metrics:
    with st.container(border=True):
        st.metric("현재 도서레벨", data['현재도서레벨'])
    with st.container(border=True):
        enrolled_text = "😉 재원중" if data.get('논술재원여부') else "😺 비재원"
        st.metric("논술 화랑 재원생", enrolled_text)
    with st.container(border=True):
        st.metric("마지막 이용 날짜", data['마지막이용날짜'], delta=status_badge, delta_color="off")

# 3️⃣ 우측: 파이 차트 (원래 높이로 복구)
with col_chart:
    with st.container(border=True):
        st.markdown("<p style='font-size:16px; font-weight:bold; margin-bottom:0;'>🚀 다음 단계 진척도</p>", unsafe_allow_html=True)
        remain_books = data['레벨업_목표도서'] - data['현재레벨_완독도서']
        progress_pct = min(int((data['현재레벨_완독도서'] / data['레벨업_목표도서']) * 100), 100)
        
        fig = px.pie(
            names=['유효 완독', '남은 권수'], 
            values=[data['현재레벨_완독도서'], remain_books], 
            hole=0.65,
            color_discrete_sequence=['#3B82F6', '#F1F5F9'] 
        )
        fig.update_traces(textinfo='none', hoverinfo='label+percent', marker=dict(line=dict(color='#FFFFFF', width=2)))
        fig.update_layout(
            margin=dict(t=10, b=10, l=10, r=10), showlegend=False, height=210,
            annotations=[dict(text=f'{progress_pct}%', x=0.5, y=0.5, font_size=30, font_color='#1E293B', showarrow=False)]
        )
        st.plotly_chart(fig, use_container_width=True)
        st.info(f"💡 현재 레벨({data['현재도서레벨']})에서 **{data['현재레벨_완독도서']}권** 읽었습니다. (목표: {data['레벨업_목표도서']}권)", icon="ℹ️")

st.write("")

card_col1, card_col2, card_col3 = st.columns(3)

with card_col1:
    st.markdown(f"""
    <div class="activity-card">
        <div class="activity-icon">📖</div>
        <div class="activity-title">완독도서</div>
        <div class="activity-value">x {data.get('총완독도서수', 0)}</div>
    </div>
    """, unsafe_allow_html=True)

with card_col2:
    st.markdown("""
    <div class="activity-card">
        <div class="activity-icon">🌱</div>
        <div class="activity-title">독서노트</div>
        <div class="activity-value">x 5</div> 
    </div>
    """, unsafe_allow_html=True)

with card_col3:
    st.markdown("""
    <div class="activity-card">
        <div class="activity-icon">💳</div>
        <div class="activity-title">어휘통장</div>
        <div class="activity-value">x 20</div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# Section 2 & 3: 요약 테이블
# ==========================================
col_diag, col_summary = st.columns([1.5, 1])

with col_diag:
    st.markdown('<div class="sub-title">2. 독서력 지수 진단 결과</div>', unsafe_allow_html=True)
    df_diagnosis = pd.DataFrame({
        "번호": ["4856", "2104"], "학생명": [data['이름'], data['이름']], 
        "결과점수": ["86.00", "72.50"], "테스트시레벨": ["0 Lv", "0 Lv"],
        "추천레벨": [data['현재도서레벨'], "Lv.12"], "제출일": ["2026-03-12", "2025-09-05"],
        "결과보기": ["🔍 보기", "🔍 보기"]
    })
    st.dataframe(df_diagnosis, use_container_width=True, hide_index=True)

with col_summary:
    st.markdown('<div class="sub-title">3. 맞춤형 활동 요약</div>', unsafe_allow_html=True)
    with st.container(border=True):
        if data['학년'] in ["초1", "초2", "초3"]:
            st.markdown("🌱 **화랑도서관 (정독)**")
            sc1, sc2 = st.columns(2)
            sc1.metric("정독 단계", data.get('정독단계', '-'))
            sc2.metric("정독 회원등급", data.get('정독_회원등급', '-'))
        else:
            st.markdown("🚀 **탐험도서관 (다독)**")
            sc1, sc2 = st.columns(2)
            sc1.metric("지성의 별", f"{data.get('지성의별', 0)} 개")
            sc2.metric("현재 금화", f"{data.get('보유금화', 0)} 개")

# ==========================================
# Section 4: 📅 독서활동
# ==========================================
# ==========================================
# Section 4: 📅 기간별 데이터 조회 (10개 데이터 테스트)
# ==========================================
st.markdown('<div class="sub-title">4. 기간별 퀴즈 응시 상세 로그</div>', unsafe_allow_html=True)

with st.container(border=True):
    col_date1, col_date2, col_blank = st.columns([1, 1, 3])
    with col_date1:
        start_date = st.date_input("🗓️ 시작일", datetime(2026, 3, 1))
    with col_date2:
        end_date = st.date_input("🗓️ 종료일", datetime(2026, 3, 13))

    st.write("")

    tab1, tab2, tab3 = st.tabs(["🌱 화랑도서관", "🚀 탐험도서관", "💬 CS/상담 이력"])

    # -----------------------------
    # 화랑도서관 탭
    # -----------------------------
    with tab1:
        if data["has_jeongdok"]:
            st.markdown("##### 📊 정독 퀴즈 결과")
            # 데이터 10개로 증식
            df_jeongdok = pd.DataFrame({
                "도서레벨": ["Lv.9", "Lv.9", "Lv.8", "Lv.9", "Lv.10", "Lv.10", "Lv.11", "Lv.9", "Lv.8", "Lv.12"], 
                "차수": ["1차", "2차", "1차", "1차", "1차", "2차", "1차", "1차", "2차", "1차"],
                "결과점수": ["80.00", "100.00", "90.00", "85.00", "95.00", "100.00", "75.00", "90.00", "80.00", "100.00"], 
                "패스여부": ["Y", "Y", "Y", "Y", "Y", "Y", "N", "Y", "Y", "Y"],
                "제출일": ["2026-03-12", "2026-03-10", "2026-03-09", "2026-03-08", "2026-03-07", "2026-03-06", "2026-03-05", "2026-03-04", "2026-03-03", "2026-03-02"], 
                "결과보기": ["🔍 결과보기"] * 10
            })
            # 💡 height=250 적용
            st.dataframe(df_jeongdok, use_container_width=True, hide_index=True, height=250)

            st.divider()

            st.markdown("##### 📝 독서 상세 활동 내역 (독후대화 / 정독어휘 / 감정발견)")
            df_activities = pd.DataFrame({
                "도서명": [
                    "에덴 호텔에서는 두 발로 걸어 주세요", "고양이 해결사 냥냥이", "누가 왕이라고?", "마법의 설탕 두 조각", "샬롯의 거미줄", 
                    "푸른 사자 와니니", "긴긴밤", "수상한 아파트", "만복이네 떡집", "아몬드"
                ],
                "독후대화": ["🔍 1/3 작성", "🔍 미작성", "🔍 3/3 작성", "🔍 2/3 작성", "🔍 미작성", "🔍 3/3 작성", "🔍 1/3 작성", "🔍 미작성", "🔍 2/3 작성", "🔍 3/3 작성"],
                "정독어휘": ["🔍 미작성", "🔍 2/3 작성", "🔍 3/3 작성", "🔍 미작성", "🔍 1/3 작성", "🔍 3/3 작성", "🔍 2/3 작성", "🔍 미작성", "🔍 1/3 작성", "🔍 3/3 작성"],
                "감정발견": ["🔍 2개 작성", "🔍 미작성", "🔍 1개 작성", "🔍 3개 작성", "🔍 미작성", "🔍 2개 작성", "🔍 1개 작성", "🔍 미작성", "🔍 2개 작성", "🔍 3개 작성"],
                "최종제출일": ["2026-03-12", "2026-03-10", "2026-03-09", "2026-03-08", "2026-03-07", "2026-03-06", "2026-03-05", "2026-03-04", "2026-03-03", "2026-03-02"]
            })
            # 💡 height=250 적용
            st.dataframe(df_activities, use_container_width=True, hide_index=True, height=250)
            st.caption("💡 '🔍' 아이콘이 있는 항목을 클릭하면 학생이 직접 입력한 텍스트 원문을 확인할 수 있습니다.")

        else:
            st.info("해당 학생은 설정한 기간 내에 활동한 [정독] 내역이 없습니다.")
            
    # -----------------------------
    # 탐험도서관 탭
    # -----------------------------
    with tab2:
        if data["has_tamheom"]:
            st.markdown("##### 📊 독서 퀴즈 및 완독 현황")
            
            # 1. 필터 컨트롤 (전체 / 완독 / 미완독)
            filter_choice = st.radio(
                "조회 필터", 
                ["📋 전체보기", "✅ 완독 완료", "⏳ 미완독 (진행중/미달)"], 
                horizontal=True,
                label_visibility="collapsed"
            )

            # 2. 데이터 구성 (요청하신 컬럼 + 지성의별 개수)
            df_tamheom = pd.DataFrame({
                "책제목": [
                    "캄캄한 밤에 나홀로", "꼬마 난민 도야", "시간을 굽는 빵집", "이상한 과자 가게 전천당", "십자도 이야기", 
                    "해리포터와 마법사의 돌", "나니아 연대기", "어린 왕자", "나의 라임오렌지나무", "모모"
                ],
                "도서레벨": ["Lv.20", "Lv.20", "Lv.21", "Lv.20", "Lv.22", "Lv.25", "Lv.24", "Lv.20", "Lv.21", "Lv.23"], 
                "지성의별": [5, 3, 6, 5, 0, 5, 5, 2, 5, 4], # 💡 별 개수 데이터 (5개 이상 완독)
                "제출일": ["2026-03-13", "2026-03-11", "2026-03-10", "2026-03-09", "-", "2026-03-07", "2026-03-06", "2026-03-05", "2026-03-04", "2026-03-03"], 
                "결과보기": ["🔍 결과보기"] * 10
            })

            # 💡 3. 비즈니스 로직: 지성의 별 5개 이상이면 '완독', 미만이면 '미완독'으로 상태 텍스트 동적 생성
            df_tamheom["완독상태"] = df_tamheom["지성의별"].apply(
                lambda x: f"✅ 완독 (⭐ {x}개)" if x >= 5 else f"⏳ 미완독 (⭐ {x}개)"
            )

            # 💡 4. 화면에 보여줄 컬럼만 딱 맞게 필터링
            display_cols = ["책제목", "도서레벨", "완독상태", "제출일", "결과보기"]

            # 5. 선택된 라디오 버튼에 따라 데이터 필터링 (텍스트가 아닌 실제 '지성의별' 숫자값으로 정확하게 필터링)
            if filter_choice == "✅ 완독 완료":
                filtered_df = df_tamheom[df_tamheom["지성의별"] >= 5][display_cols]
            elif filter_choice == "⏳ 미완독 (진행중/미달)":
                filtered_df = df_tamheom[df_tamheom["지성의별"] < 5][display_cols]
            else:
                filtered_df = df_tamheom[display_cols]

            # 6. 결과 표 출력
            st.dataframe(filtered_df, use_container_width=True, hide_index=True, height=250)

            st.divider()

            # (하단 독서 상세 활동 내역은 그대로 유지)
            st.markdown("##### 📝 독서 상세 활동 내역 (독서노트 / 도서평점)")
            df_tamheom_activities = pd.DataFrame({
                "도서명": [
                    "캄캄한 밤에 나홀로", "꼬마 난민 도야", "시간을 굽는 빵집", "이상한 과자 가게 전천당", "십자도 이야기", 
                    "해리포터와 마법사의 돌", "나니아 연대기", "어린 왕자", "나의 라임오렌지나무", "모모"
                ],
                "독서노트": ["🔍 1/2 작성", "🔍 미작성", "🔍 2/2 작성", "🔍 1/2 작성", "🔍 미작성", "🔍 2/2 작성", "🔍 1/2 작성", "🔍 미작성", "🔍 2/2 작성", "🔍 1/2 작성"],
                "도서평점": ["🔍 😐 3점", "🔍 미작성", "🔍 😃 5점", "🔍 😃 4점", "🔍 미작성", "🔍 😃 5점", "🔍 😐 3점", "🔍 미작성", "🔍 😃 5점", "🔍 😃 4점"],
                "최종제출일": ["2026-03-13", "-", "2026-03-10", "2026-03-09", "-", "2026-03-07", "2026-03-06", "-", "2026-03-04", "2026-03-03"]
            })
            st.dataframe(df_tamheom_activities, use_container_width=True, hide_index=True, height=250)
            st.caption("💡 '🔍' 아이콘이 있는 항목을 클릭하면 학생이 직접 입력한 노트 원문과 평점 이유를 확인할 수 있습니다.")

        else:
            st.info("해당 학생은 설정한 기간 내에 응시한 [탐험 퀴즈] 내역이 없습니다.")

#tab3 (CS/상담 이력) 추가
    with tab3:
        st.markdown("##### 🎧 고객 센터(CS) 및 실무 상담 이력")
        
        # 1. 입력 및 수정 폼
        with st.expander("📝 문의 접수 및 답변 등록/수정", expanded=False):
            # 입력부 상단 설정
            c1, c2, c3 = st.columns([1, 1, 1])
            category = c1.selectbox("처리 카테고리", ["레벨/진단", "완독/활동 오류", "시스템 오류", "이벤트/뱃지", "기타"], key="cs_cat")
            status = c2.selectbox("처리 상태", ["접수/대기", "확인 중", "처리 완료", "답변 완료"], key="cs_stat")
            manager = c3.text_input("담당자", value="관리자A", key="cs_manager")
            
            # 메인 내용 입력 (제목 없이 질문과 답변으로 구성)
            q_content = st.text_area("질문(문의) 내용", height=100, placeholder="학생/학부모의 문의 원문을 입력하세요.")
            a_content = st.text_area("답변(처리) 내용", height=100, placeholder="조치 결과 또는 답변 내용을 입력하세요.")
            
            save_btn = st.button("💾 데이터 저장")

        st.divider()

        # 2. 통합 이력 리스트 (제목 없이 핵심 내용 위주)
        # 질문자님이 주신 예시를 답변형 구조로 재구성한 데이터
        df_cs_final = pd.DataFrame({
            "접수일": ["2026-03-14", "2026-03-12", "2026-03-10"],
            "질문 내용": [
                "10권 읽었으나 8권만 완독 처리됨. 확인 요청.",
                "작년 진단 결과가 현재 레벨과 안 맞음. 초기화 희망.",
                "자매 동시 수강생인데 뱃지는 한 명만 들어오나요?"
            ],
            "답변 내용": [
                "로그 확인 결과 네트워크 끊김으로 2권 누락. 수동 완독 처리 완료.",
                "진단 이력 초기화 완료. 이번 주말까지 재응시 안내함.",
                "자매 개별 아이디로 각각 설문 참여 시 모두 지급 가능함 안내."
            ],
            "처리 카테고리": ["완독/활동 오류", "레벨/진단", "이벤트/뱃지"],
            "처리 상태": ["처리 완료", "처리 완료", "답변 완료"],
            "담당자": ["관리자A", "상담원B", "관리자A"],
            "관리": ["⚙️ 수정", "⚙️ 수정", "⚙️ 수정"]
        })
        
        # 가독성을 위해 데이터프레임 출력 (height=300으로 넉넉하게 설정)
        st.dataframe(df_cs_final, use_container_width=True, hide_index=True, height=300)