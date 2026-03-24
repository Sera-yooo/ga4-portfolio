import streamlit as st
import pandas as pd
from datetime import date, timedelta, datetime
import io
import os
from src.data_loader import load_school_trial_data

# --- [엑셀 일괄 생성용 텍스트 생성 함수] ---
def generate_excel_contents(row):
    # 엑셀 데이터 파싱
    sch = str(row.get('학교명', '')).strip()
    tea = str(row.get('담당교사명', '')).strip()
    
    # 계정 정보 매핑
    a_id, a_pw = str(row.get('ID', '')).strip(), str(row.get('PW', '')).strip()
    s1_id, s1_pw = str(row.get('ID.1', '')).strip(), str(row.get('PW.1', '')).strip()
    s2_id, s2_pw = str(row.get('ID.2', '')).strip(), str(row.get('PW.2', '')).strip()
    
    # 날짜 처리
    s_date = row.get('체험시작일', '2026-03-10')
    e_date = row.get('체험종료일', '2026-03-31')
    s_str = s_date.strftime('%Y-%m-%d') if isinstance(s_date, datetime) else str(s_date)[:10]
    e_str = e_date.strftime('%Y-%m-%d') if isinstance(e_date, datetime) else str(e_date)[:10]

    mail_sub = "독서화랑 클래스 체험 계정 안내 드립니다."

    # A. 메일 본문 (원본 유지)
    mail_body = f"""안녕하세요, {sch} {tea} 선생님!
우리 아이들의 즐거운 독서 습관 형성을 돕는 독서화랑 클래스입니다.

신청해주신 체험 서비스가 정상적으로 접수되었습니다. 
원활한 체험을 위해 아래 정보를 확인해 주세요.

[서비스 접속 정보]
1. 체험 기간: {s_str} ~ {e_str}
2. 접속 URL: https://school.dmy.co.kr/
3. 선생님 관리자 ID: {a_id} / PW: {a_pw}
4. 학생 ①(2학년)  ID : {s1_id}  / PW: {s1_pw}
   학생 ②(4학년)  ID : {s2_id}  / PW: {s2_pw}

[첨부파일]
1. 이용 가이드 
2. 서비스 소개서

[참고 :이용 시 주의 사항]
- 콘텐츠의 무단 복제 및 배포는 엄격히 금지됩니다.
- 체험 종료 후 간단한 피드백에 협조 부탁드립니다.

독서화랑 클래스가 선생님의 수업 준비에 실질적인 도움이 될 수 있도록 최선을 다하겠습니다.

추가로 궁금하신 사항이나 자세한 안내가 필요하시면 말씀해 주시면
관련 내용을 정리하여 메일로 보내드리겠습니다.

감사합니다."""

    # B. 문자 본문 (원본 유지)
    sms_body = f"""안녕하세요, {sch} {tea}선생님!
독서화랑 클래스입니다.

신청해주신 체험 서비스가 정상적으로 접수되었습니다.
아래 접속 정보를 확인해 주세요.

[서비스 접속 정보]
1. 체험 기간: {s_str} ~ {e_str}
2. 접속 URL: https://school.dmy.co.kr/
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

def render():
    st.subheader("📩 독서화랑 CS 메시지 자동 생성기")
    st.info("개별 맞춤 메시지를 생성하거나, 시트 데이터를 연동하여 대량으로 안내문을 뽑아낼 수 있습니다.")

    tab_single, tab_excel = st.tabs(["✉️ 단일 맞춤 메시지 생성", "📊 엑셀 사용 대량 메시지 생성"])

    # =========================================================
    # [탭 1] 단일 맞춤 메시지 생성 
    # =========================================================
    with tab_single:
        if 'res_type' not in st.session_state: st.session_state.res_type = "" 
        if 'gen_sub' not in st.session_state: st.session_state.gen_sub = ""
        if 'gen_body' not in st.session_state: st.session_state.gen_body = ""

        with st.container(border=True):
            st.markdown("##### 👤 기본 수신 정보 (공통)")
            c1, c2, c3 = st.columns(3)
            with c1:
                school = st.text_input("학교명/기관명", placeholder="예: 서울초", key="sg_sch")
            with c2:
                teacher = st.text_input("교사/담당자 성함", placeholder="예: 김선생", key="sg_tea")
            with c3:
                email_addr = st.text_input("수신인 메일 주소", placeholder="example@email.com", key="sg_em")

        template_options = ["1. 체험 계정 안내", "2. 중간 점검 설문", "3. 견적서 발행 및 송부", "4. 계약 서류 송부", "5. 정규 서비스 개시 안내"]
        selected = st.selectbox("📌 업무 단계 선택", template_options, key="sg_step")

        st.divider()

        if selected == "1. 체험 계정 안내":
            st.markdown(f"#### 📂 {selected}")
            
            ca, cb = st.columns(2)
            with ca:
                start_date = st.date_input("체험 시작일", value=date.today(), key="sg_start")
                admin_id = st.text_input("선생님 관리자 ID", key="sg_adm_id")
                std1_id = st.text_input("학생①(2학년) ID", key="sg_std1")
            with cb:
                end_date = st.date_input("체험 종료일", value=date.today() + timedelta(days=31), key="sg_end")
                admin_pw = st.text_input("관리자 비밀번호", value="0000", key="sg_adm_pw")
                std2_id = st.text_input("학생②(4학년) ID", key="sg_std2")

            doc_list = st.multiselect(
                "송부 서류 선택 (메일/문자 생성 시 반영)", 
                [
                    "이용 가이드 (관리교사,일반교사,학생용)", 
                    "서비스 소개서", 
                    "학생 계정 명단", 
                    "이용 확인서",
                    "상세 매뉴얼(관리교사용)", 
                    "상세 매뉴얼(일반교사용)",
                    "학운위 체크리스트 (PDF)",
                    "학운위 체크리스트 (PPT)"
                ], 
                # 핵심 수정: 옵션 리스트에 있는 문자열과 토씨 하나 안 틀리고 똑같이 맞춰야 합니다.
                default=["이용 가이드 (관리교사,일반교사,학생용)", "서비스 소개서"], 
                key="sg_docs"
            )

            def get_manual_section(selected_list):
                links = []
                # 선택된 리스트에 정확히 해당 문구가 있는지 확인
                if "상세 매뉴얼(관리교사용)" in selected_list:
                    links.append("- 관리교사용: https://drive.google.com/drive/folders/1EOoPtolllNWbUgst_ki8hv-purrh3to0?usp=drive_link")
                if "상세 매뉴얼(일반교사용)" in selected_list:
                    links.append("- 일반교사용: https://drive.google.com/drive/folders/15oAEQMXyBwh95_xEbdTQuvKr3aRBP_is?usp=drive_link")       
                if "학운위 체크리스트 (PDF)" in selected_list:
                    links.append("- 학운위(PDF): https://drive.google.com/file/d/1Prg8hOxVQ396BDREX1OAvtJBi0flTExF/view?usp=drive_link")         
                if "학운위 체크리스트 (PPT)" in selected_list:
                    links.append("- 학운위(PPT): https://docs.google.com/presentation/d/1YPrYwDKA3IJYIuWs2fRSc4v0C4pV3u8I/edit?usp=drive_link&ouid=102025982189355015550&rtpof=true&sd=true")         
                
                if links:
                    # 가독성을 위해 상단에 한 줄 띄움 처리
                    return "\n[상세 매뉴얼 다운로드]\n" + "\n".join(links) + "\n"
                return ""

            col_btn1, col_btn2 = st.columns(2)
            
            # A. 메일 메시지 생성
            with col_btn1:
                if st.button("📧 메일 메시지 생성하기", type="primary", use_container_width=True):
                    st.session_state.res_type = "메일"
                    st.session_state.gen_sub = "독서화랑 클래스 체험 안내 드립니다."
                    
                    other_docs = [d for d in doc_list if "상세 매뉴얼" not in d]
                    attachment_text = "\n".join([f"{i+1}. {doc}" for i, doc in enumerate(other_docs)])
                    manual_section = get_manual_section(doc_list)
                    
                    st.session_state.gen_body = f"""안녕하세요, {school} {teacher} 선생님.
우리 아이들의 즐거운 독서 습관 형성을 돕는 독서화랑 클래스입니다.

신청해주신 체험 서비스가 정상적으로 접수되었습니다. 
원활한 체험을 위해 아래 정보를 확인해 주세요.

[서비스 접속 정보]
체험 기간 : {start_date} ~ {end_date}
접속 URL : https://school.dmy.co.kr/
선생님 관리자 ID: {admin_id} / PW: {admin_pw}
학생①(2학년) ID : {std1_id} / PW : 0000
학생②(4학년) ID : {std2_id} / PW : 0000

{manual_section}
[첨부파일]
{attachment_text}

[참고 :이용 시 주의 사항]
- 콘텐츠의 무단 복제 및 배포는 엄격히 금지됩니다.
- 체험 종료 후 간단한 피드백에 협조 부탁드립니다.

독서화랑 클래스가 선생님의 수업 준비에 실질적인 도움이 될 수 있도록 최선을 다하겠습니다.

추가로 궁금하신 사항이나 자세한 안내가 필요하시면 말씀해 주시면
관련 내용을 정리하여 메일로 보내드리겠습니다.

감사합니다."""

            # B. 문자 메시지 생성
            with col_btn2:
                if st.button("📱 문자 메시지 생성하기", type="secondary", use_container_width=True):
                    st.session_state.res_type = "문자"
                    st.session_state.gen_sub = "독서화랑 클래스 체험 계정 안내 드립니다."
                    manual_section = get_manual_section(doc_list)
                    
                    st.session_state.gen_body = f"""안녕하세요, {school} {teacher} 선생님.
우리 아이들의 즐거운 독서 습관 형성을 돕는 독서화랑 클래스입니다.

신청해주신 체험 서비스가 정상적으로 접수되었습니다. 
원활한 체험을 위해 아래 정보를 확인해 주세요.

[서비스 접속 정보]
체험 기간 : {start_date} ~ {end_date}
접속 URL : https://school.dmy.co.kr/
선생님 관리자 ID: {admin_id} / PW: {admin_pw}
학생①(2학년) ID : {std1_id} / PW : 0000
학생②(4학년) ID : {std2_id} / PW : 0000

{manual_section}
이용 가이드 및 서비스 소개 자료가 있습니다.
이메일 주소를 보내주시면 첨부파일을 전달드리겠습니다.

보내실 이메일 : dsmycs001@gmail.com

독서화랑 클래스 마케팅팀
T. 02-593-9964

감사합니다."""

        # ✨ 결과 출력부 수정: st.code를 사용하여 복사 버튼 자동 생성 및 업데이트 오류 해결
        if st.session_state.gen_sub:
            st.divider()
            st.subheader(f"✅ 생성된 {st.session_state.res_type} 메시지")
            
            st.markdown("**📌 제목**")
            st.code(st.session_state.gen_sub, language="plaintext")
            
            st.markdown("**📌 본문**")
            st.code(st.session_state.gen_body, language="plaintext")
            
            st.success(f"👆 위 박스 우측 상단의 **복사 아이콘**을 클릭하여 사용하세요!")

    # =========================================================
    # [탭 3] 엑셀 파일 업로드 기반 대량 생성 
    # =========================================================
    with tab_excel:
        st.markdown("#### 📥 양식 작성 후 엑셀 업로드 일괄 생성")
        template_file_path = "pages/일괄메일전송_양식파일.xlsx" 

        with st.container(border=True):
            st.markdown("##### 1️⃣ 작업 시작 전 양식 다운로드")
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
                            type="primary",
                            key="excel_dl_btn"
                        )
                except FileNotFoundError:
                    st.warning("⚠️ '일괄메일전송_양식파일.xlsx' 파일을 찾을 수 없습니다. 경로를 확인해주세요.")
                    
            with col_txt:
                st.info("💡 위 양식을 다운로드하여 내용을 작성한 뒤, 아래 업로드 칸에 넣어주세요.")

        st.divider()
        
        st.markdown("##### 2️⃣ 작성된 엑셀 파일 업로드")
        uploaded_file = st.file_uploader("작성 완료된 엑셀 파일(.xlsx)을 업로드하세요", type=["xlsx"], key="excel_uploader")

        if uploaded_file:
            try:
                # 2행(index 1)을 헤더로 읽기
                df_ex = pd.read_excel(uploaded_file, header=1, dtype=str)
                st.success("✅ 파일을 성공적으로 불러왔습니다.")

                if st.button("🚀 엑셀 데이터 일괄 생성하기", type="primary", use_container_width=True, key="excel_gen_btn"):
                    mail_titles, mail_contents, sms_contents = [], [], []

                    for _, row in df_ex.iterrows():
                        if pd.isna(row.get('학교명')): continue
                        
                        sub, m_body, s_body = generate_excel_contents(row)
                        mail_titles.append(sub)
                        mail_contents.append(m_body)
                        sms_contents.append(s_body)

                    # 데이터 합치기
                    df_ex['생성된 메일제목'] = mail_titles
                    df_ex['생성된 메일본문'] = mail_contents
                    df_ex['생성된 문자본문'] = sms_contents

                    # 10개 컬럼만 추출
                    target_cols = ['No', '지역', '상세지역', '학교명', '담당교사명', '학교코드', '전화번호', '생성된 메일제목', '생성된 메일본문', '생성된 문자본문']
                    final_df = df_ex[[col for col in target_cols if col in df_ex.columns]]

                    st.divider()
                    st.subheader(f"📊 생성 결과 확인 (총 {len(final_df)}건)")
                    st.dataframe(final_df, use_container_width=True)

                    # 다운로드 버튼
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        final_df.to_excel(writer, index=False, sheet_name='발송리스트')
                    
                    st.download_button(
                        label="📥 결과 엑셀 파일 다운로드 (메일/문자 본문 포함)",
                        data=output.getvalue(),
                        file_name=f"독서화랑_통합발송리스트_{datetime.now().strftime('%m%d')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                        type="primary",
                        key="excel_res_dl_btn"
                    )
                    st.snow()

            except Exception as e:
                st.error(f"파일 처리 중 오류가 발생했습니다: {e}")