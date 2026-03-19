import streamlit as st
from datetime import date, timedelta

# --- 0. 기본 설정 ---
st.set_page_config(page_title="독서화랑 CS 업무 비서", page_icon="📚", layout="wide")

if 'result_type' not in st.session_state:
    st.session_state.result_type = "" 
if 'generated_subject' not in st.session_state:
    st.session_state.generated_subject = ""
if 'generated_body' not in st.session_state:
    st.session_state.generated_body = ""

# --- 1. 상단: 공통 수신 정보 ---
st.title("📚 독서화랑 단일 메시지 생성기")

with st.container(border=True):
    st.subheader("👤 기본 수신 정보 (공통)")
    c1, c2, c3 = st.columns(3)
    with c1:
        school = st.text_input("학교명/기관명", placeholder="예: 서울초")
    with c2:
        teacher = st.text_input("교사/담당자 성함", placeholder="예: 김선생")
    with c3:
        email_addr = st.text_input("수신인 메일 주소", placeholder="example@email.com")

st.divider()

# --- 2. 사이드바: 업무 단계 선택 ---
template_options = ["1. 체험 계정 안내", "2. 중간 점검 설문", "3. 견적서 발행 및 송부", "4. 계약 서류 송부", "5. 정규 서비스 개시 안내"]
selected = st.sidebar.radio("📌 업무 단계 선택", template_options)

# --- 3. 단계별 로직 ---

if selected == "1. 체험 계정 안내":
    st.subheader(f"📂 {selected}")
    
    ca, cb = st.columns(2)
    with ca:
        start_date = st.date_input("체험 시작일", value=date.today())
        admin_id = st.text_input("선생님 관리자 ID")
        std1_id = st.text_input("학생①(2학년) ID")
    with cb:
        end_date = st.date_input("체험 종료일", value=date.today() + timedelta(days=31))
        admin_pw = st.text_input("관리자 비밀번호", value="0000")
        std2_id = st.text_input("학생②(4학년) ID")

    # [선택지 업데이트] 매뉴얼 두 가지를 개별 선택 가능하게 추가
    doc_list = st.multiselect(
        "송부 서류 선택 (메일/문자 생성 시 반영)", 
        [
            "이용 가이드", 
            "서비스 소개서", 
            "학생 계정 명단", 
            "이용 확인서",
            "상세 매뉴얼(관리교사용)", 
            "상세 매뉴얼(일반교사용)"
        ], 
        default=["이용 가이드", "서비스 소개서"]
    )

    # 매뉴얼 링크 생성 로직
    def get_manual_section(selected_list):
        links = []
        if "상세 매뉴얼(관리교사용)" in selected_list:
            links.append("- 관리교사용: https://drive.google.com/drive/folders/1EOoPtolllNWbUgst_ki8hv-purrh3to0?usp=drive_link")
        if "상세 매뉴얼(일반교사용)" in selected_list:
            links.append("- 일반교사용: https://drive.google.com/drive/folders/15oAEQMXyBwh95_xEbdTQuvKr3aRBP_is?usp=drive_link")
        
        if links:
            return "[상세 매뉴얼 다운로드]\n" + "\n".join(links) + "\n"
        return ""

    col_btn1, col_btn2 = st.columns(2)
    
    # A. 메일 메시지 생성
    with col_btn1:
        if st.button("📧 메일 메시지 생성하기", type="primary", use_container_width=True):
            st.session_state.result_type = "메일"
            st.session_state.generated_subject = "독서화랑 클래스 체험 안내 드립니다."
            
            # 일반 첨부파일 목록 (매뉴얼 제외하고 번호 매기기)
            other_docs = [d for d in doc_list if "상세 매뉴얼" not in d]
            attachment_text = "\n".join([f"{i+1}. {doc}" for i, doc in enumerate(other_docs)])
            manual_section = get_manual_section(doc_list)
            
            st.session_state.generated_body = f"""안녕하세요, {school} {teacher} 선생님.
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
            st.session_state.result_type = "문자"
            st.session_state.generated_subject = "독서화랑 클래스 체험 계정 안내 드립니다."
            manual_section = get_manual_section(doc_list)
            
            st.session_state.generated_body = f"""안녕하세요, {school} {teacher} 선생님.
독서화랑 클래스입니다.

신청해주신 체험 서비스가 정상적으로 접수되었습니다.
아래 접속 정보를 확인해 주세요.

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

# --- 4. 최종 결과 출력 ---
if st.session_state.generated_subject:
    st.divider()
    st.subheader(f"✅ 생성된 {st.session_state.result_type} 메시지")
    st.text_input("제목 (복사용)", value=st.session_state.generated_subject)
    st.text_area("본문 (복사용)", value=st.session_state.generated_body, height=500)
    st.success(f"{st.session_state.result_type} 메시지가 성공적으로 생성되었습니다!")