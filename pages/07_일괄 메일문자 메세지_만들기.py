import streamlit as st
import pandas as pd
import io
import os
from datetime import datetime

# --- 0. 페이지 설정 ---
st.set_page_config(page_title="독서화랑 일괄 생성기", page_icon="📑", layout="wide")

# --- 1. 상단: 양식 파일 다운로드 섹션 ---
st.title("📑 독서화랑 일괄 메일 & 문자 생성기")

# 파일 경로 설정 (페이지 폴더 혹은 루트 폴더 확인 필요)
template_file_path = "pages/일괄메일전송_양식파일.xlsx" 

with st.container(border=True):
    st.subheader("📥 작업 시작 전 양식 다운로드")
    col_dl, col_txt = st.columns([1, 2])
    
    with col_dl:
        try:
            with open(template_file_path, "rb") as f:
                st.download_button(
                    label="📂 일괄메일전송_양식파일 다운로드",
                    data=f,
                    file_name="일괄메일전송_양식파일.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    type="primary"
                )
        except FileNotFoundError:
            st.warning("⚠️ '일괄메일전송_양식파일.xlsx' 파일을 찾을 수 없습니다. 경로를 확인해주세요.")
            
    with col_txt:
        st.info("💡 위 양식을 다운로드하여 내용을 작성한 뒤, 아래 업로드 칸에 넣어주세요.")

st.divider()

# --- 2. 메일/문자 본문 생성 함수 ---
def generate_contents(row):
    # 엑셀 데이터 파싱
    sch = str(row.get('학교명', '')).strip()
    tea = str(row.get('담당교사명', '')).strip()
    
    # 계정 정보 매핑 (중복 컬럼 처리)
    a_id, a_pw = str(row.get('ID', '')).strip(), str(row.get('PW', '')).strip()
    s1_id, s1_pw = str(row.get('ID.1', '')).strip(), str(row.get('PW.1', '')).strip()
    s2_id, s2_pw = str(row.get('ID.2', '')).strip(), str(row.get('PW.2', '')).strip()
    
    # 날짜 처리
    s_date = row.get('체험시작일', '2026-03-10')
    e_date = row.get('체험종료일', '2026-03-31')
    s_str = s_date.strftime('%Y-%m-%d') if isinstance(s_date, datetime) else str(s_date)[:10]
    e_str = e_date.strftime('%Y-%m-%d') if isinstance(e_date, datetime) else str(e_date)[:10]

    mail_sub = "독서화랑 클래스 체험 안내 드립니다."

    # A. 메일 본문
    mail_body = f"""안녕하세요, {sch} {tea} 선생님!
우리 아이들의 즐거운 독서 습관 형성을 돕는 독서화랑 클래스입니다.

신청해주신 체험 서비스가 정상적으로 접수되었습니다. 
원활한 체험을 위해 아래 정보를 확인해 주세요.

[서비스 접속 정보]
1. 체험 기간: {s_str} ~ {e_str}
2. 접속 URL: https://school.dmy.co.kr/teacher/
3. 선생님 관리자 ID: {a_id} / PW: {a_pw}
4. 학생 ①(2학년)  ID : {s1_id}  / PW: {s1_pw}
   학생 ②(4학년)  ID : {s2_id}  / PW: {s2_pw}

[첨부파일]
1. 관리 선생님, 일반 선생님, 학생 이용 가이드
2. 독서화랑 클래스 서비스 소개서  

[참고 :이용 시 주의 사항]
- 콘텐츠의 무단 복제 및 배포는 엄격히 금지됩니다.
- 체험 종료 후 간단한 피드백(설문)에 협조 부탁드립니다.

독서화랑 클래스가 선생님의 수업 준비에 실질적인 도움이 될 수 있도록 최선을 다하겠습니다.

추가로 궁금하신 사항이나 자세한 안내가 필요하시면 말씀해 주시면
관련 내용을 정리하여 메일로 보내드리겠습니다.

감사합니다."""

    # B. 문자 본문
    sms_body = f"""안녕하세요, {sch} {tea}선생님!
독서화랑 클래스입니다.

신청해주신 체험 서비스가 정상적으로 접수되었습니다.
아래 접속 정보를 확인해 주세요.

[서비스 접속 정보]
1. 체험 기간: {s_str} ~ {e_str}
2. 접속 URL: https://school.dmy.co.kr/teacher/
3. 선생님 관리자 ID: {a_id} / PW: {a_pw}
4. 학생 ①(2학년)  ID :  {s1_id}  / PW: {s1_pw}
   학생 ②(4학년)  ID :  {s2_id}  / PW: {s2_pw}

이용 가이드 및 서비스 소개 자료가 있습니다.
이메일 주소를 보내주시면 첨부파일을 전달드리겠습니다.

보내실 이메일 : dsmycs001@gmail.com
독서화랑 클래스 마케팅팀
T. 02-593-9964

감사합니다."""

    return mail_sub, mail_body, sms_body

# --- 3. 엑셀 업로드 및 처리 ---
uploaded_file = st.file_uploader("작성된 엑셀 파일(.xlsx)을 업로드하세요", type=["xlsx"])

if uploaded_file:
    try:
        # 2행(index 1)을 헤더로 읽기
        df = pd.read_excel(uploaded_file, header=1)
        st.success("✅ 파일을 성공적으로 불러왔습니다.")

        if st.button("🚀 모든 데이터 일괄 생성하기", type="primary"):
            mail_titles, mail_contents, sms_contents = [], [], []

            for _, row in df.iterrows():
                if pd.isna(row.get('학교명')): continue
                
                sub, m_body, s_body = generate_contents(row)
                mail_titles.append(sub)
                mail_contents.append(m_body)
                sms_contents.append(s_body)

            # 데이터 합치기
            df['생성된 메일제목'] = mail_titles
            df['생성된 메일본문'] = mail_contents
            df['생성된 문자본문'] = sms_contents

            # 10개 컬럼만 추출
            target_cols = ['No', '지역', '상세지역', '학교명', '담당교사명', '학교코드', '전화번호', '생성된 메일제목', '생성된 메일본문', '생성된 문자본문']
            final_df = df[[col for col in target_cols if col in df.columns]]

            st.divider()
            st.subheader(f"📊 생성 결과 확인 (총 {len(final_df)}건)")
            st.dataframe(final_df, use_container_width=True)

            # 다운로드 버튼
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                final_df.to_excel(writer, index=False, sheet_name='발송리스트')
            
            st.download_button(
                label="📥 결과 엑셀 파일 다운로드 (10개 컬럼)",
                data=output.getvalue(),
                file_name=f"독서화랑_통합발송리스트_{datetime.now().strftime('%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            st.snow()

    except Exception as e:
        st.error(f"오류가 발생했습니다: {e}")