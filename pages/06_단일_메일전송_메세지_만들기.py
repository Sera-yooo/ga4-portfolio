import streamlit as st
import urllib.parse
from datetime import date, timedelta

# --- 0. 기본 설정 ---
st.set_page_config(page_title="독서화랑 CS 업무 비서", page_icon="📚", layout="wide")

# 세션 상태 초기화 (버튼 클릭 시 데이터를 저장하기 위함)
if 'generated_subject' not in st.session_state:
    st.session_state.generated_subject = ""
if 'generated_body' not in st.session_state:
    st.session_state.generated_body = ""

# --- 1. 상단: 공통 수신 정보 ---
st.title("📚 독서화랑 CS 프로세스 가이드 & 메일 생성기")

with st.container(border=True):
    st.subheader("👤 기본 수신 정보 (공통)")
    c1, c2, c3 = st.columns(3)
    with c1:
        school = st.text_input("학교명/기관명", placeholder="예: 서울초")
    with c2:
        teacher = st.text_input("교사/담당자 성함", placeholder="예: 김선생")
    with c3:
        email = st.text_input("수신인 메일 주소", placeholder="example@email.com")

st.divider()

# --- 2. 사이드바: 업무 단계 선택 ---
template_options = [
    "1. 체험 신청 확인 및 계정 생성",
    "2. 미응답 리마인드 (메일 발송 2일 후)",
    "3. 체험 준비 지원 (5~7일 후)",
    "4. 중간 점검 설문 (시작 5일 후)",
    "5. 견적서 발행 및 송부",
    "6. 계약 서류 송부 (최종 확정)",
    "7. 정규 서비스 개시 안내"
]
selected = st.sidebar.radio("📌 현재 업무 단계 선택", template_options)

# --- 3. 단계별 가이드 및 입력창 ---

if selected == "1. 체험 신청 확인 및 계정 생성":
    with st.expander("✅ 실무 가이드 & 체크리스트", expanded=True):
        st.info("💡 신청 2일 이내 발송")
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.markdown("**📌 실행 가이드**")
            st.write("- 체험 신청 응답 리스트 및 관리대장 기록")
            st.write("- 관리자 페이지 내 학교/교사 계정 생성")
        with col_g2:
            st.markdown("**📎 필수 첨부파일 체크**")
            st.checkbox("1. 서비스 홈페이지 링크", key="f1_1")
            st.checkbox("2. 서비스 소개 파일", key="f1_2")
            st.checkbox("3. (교사용/학생용) 이용 매뉴얼", key="f1_3")
            st.checkbox("4. 퀵 매뉴얼 파일", key="f1_4")
            st.checkbox("5. 이용 확인서", key="f1_5")

    ca, cb = st.columns(2)
    with ca:
        start_date = st.date_input("체험 시작일", value=date.today())
        admin_id = st.text_input("관리자 ID")
    with cb:
        end_date = st.date_input("체험 종료일", value=date.today() + timedelta(days=14))
        admin_pw = st.text_input("관리자 PW")

    if st.button("🚀 1단계 메일 생성하기", type="primary"):
        st.session_state.generated_subject = f"[독서화랑] {school} 체험 신청 감사 및 서비스 이용 안내"
        st.session_state.generated_body = f"안녕하세요, {school} {teacher} 선생님!\n우리 아이들의 즐거운 독서 습관 형성을 돕는 독서화랑 클래스입니다.\n\n신청해주신 체험 서비스가 정상적으로 접수되었습니다. 원활한 체험을 위해 아래 정보를 확인해 주세요.\n\n[서비스 접속 정보]\n체험 기간: {start_date} ~ {end_date}\n접속 URL: https://school.dmy.co.kr/teacher/\n선생님 관리자 ID: {admin_id} / PW: {admin_pw}\n\n[이용 시 확인 사항]\n- 체험용 계정 정보는 종료 후 일괄 삭제됩니다.\n- 콘텐츠의 무단 복제 및 배포는 엄격히 금지됩니다.\n- 체험 종료 후 간단한 피드백(설문)에 협조 부탁드립니다.\n\n독서화랑 클래스가 선생님의 수업 준비에 실질적인 도움이 될 수 있도록 최선을 다하겠습니다. 감사합니다."

elif selected == "2. 미응답 리마인드 (메일 발송 2일 후)":
    with st.expander("✅ 실행 가이드", expanded=True):
        st.write("- 메일 발송 2일 후 문자/메일 발송")
    
    link = st.text_input("신청 내용 다시보기 링크")
    if st.button("🚀 2단계 메일 생성하기", type="primary"):
        st.session_state.generated_subject = f"[독서화랑 클래스] 체험 신청 확인 안내드립니다"
        st.session_state.generated_body = f"안녕하세요, {teacher} 선생님! 독서화랑 클래스입니다.\n\n며칠 전 발송해드린 체험 안내 메일을 혹시 확인하지 못하셨을까 하여 간단히 안내드립니다.\n메일을 받지 못하셨거나 접속에 어려움이 있으신 경우 말씀해 주시면 즉시 다시 안내드리겠습니다!\n\n신청 내용 다시보기: {link}\n\n감사합니다."

elif selected == "3. 체험 준비 지원 (5~7일 후)":
    with st.expander("✅ 실행 가이드", expanded=True):
        st.write("- 체험 신청 후 5~7일간 미접속 시 발송")
    
    link = st.text_input("신청 정보 재확인 링크")
    if st.button("🚀 3단계 메일 생성하기", type="primary"):
        st.session_state.generated_subject = f"[독서화랑] 선생님, 체험 준비를 도와드릴까요?"
        st.session_state.generated_body = f"안녕하세요, 독서화랑 마케팅팀입니다.\n\n{school}에서 신청해주신 체험 서비스가 아직 시작되지 않아 도움을 드리고자 연락드렸습니다.\n초기 세팅이나 로그인 과정에서 궁금한 점이 있으시다면 편하게 말씀해 주세요!\n\n신청 정보 재확인: {link}\n\n감사합니다."

elif selected == "4. 중간 점검 설문 (시작 5일 후)":
    with st.expander("✅ 실행 가이드", expanded=True):
        st.write("- 체험 시작 5일 후 발송")
    
    survey_link = st.text_input("중간 설문조사 링크")
    if st.button("🚀 4단계 메일 생성하기", type="primary"):
        st.session_state.generated_subject = f"[독서화랑] 선생님, 아이들과의 체험은 어떠신가요?"
        st.session_state.generated_body = f"안녕하세요, {teacher} 선생님! 독서화랑 클래스입니다.\n\n현재 진행 중인 체험 서비스가 아이들에게 의미 있는 독서 시간이 되고 있는지 궁금합니다.\n이용 중 불편한 점이나 개선이 필요한 부분은 없으신지 확인하고자 간단한 중간 점검 설문을 준비했습니다.\n1분 정도만 시간을 내어 응답해 주시면 서비스 개선에 큰 도움이 되겠습니다.\n\n중간 설문조사: {survey_link}\n\n감사합니다."

elif selected == "5. 견적서 발행 및 송부":
    with st.expander("✅ 실무 가이드 & 체크리스트", expanded=True):
        st.info("💡 발행 직후 1~2일 이내 송부")
        st.checkbox("독서화랑 class 견적서 1부 첨부 확인", key="f5_1")
    
    benefit = st.text_area("독서화랑만의 핵심 혜택", value="1. 실시간 독서 데이터 리포트 제공\n2. 선생님 수업 편의성 최우선 강화")
    if st.button("🚀 5단계 메일 생성하기", type="primary"):
        st.session_state.generated_subject = f"[독서화랑] {school} 온라인 독서 클래스 도입 견적서 및 행정 서류 송부"
        st.session_state.generated_body = f"안녕하세요, {teacher} 선생님!\n아이들의 즐거운 독서 습관 형성을 돕는 독서화랑 클래스 마케팅팀입니다.\n\n문의하신 서비스 도입을 위해 필요한 견적서와 관련 행정 서류를 준비하여 보내드립니다.\n\n1. 송부 서류 리스트: 독서화랑 class 견적서 1부\n2. 핵심 혜택: {benefit}\n3. 안내 사항: 본 견적서의 유효기간은 발행일로부터 30일입니다.\n\n검토 후 도입 의사를 밝혀주시면 정식 계약 절차와 계정 발급을 신속히 진행하겠습니다. 감사합니다."

elif selected == "6. 계약 서류 송부 (최종 확정)":
    with st.expander("✅ 필수 첨부파일 체크", expanded=True):
        c_l, c_r = st.columns(2)
        with c_l:
            st.checkbox("1. 공식 이용 계약서", key="f6_1")
            st.checkbox("2. 최종 견적서", key="f6_2")
        with c_r:
            st.checkbox("3. 사업자등록증 사본", key="f6_3")
            st.checkbox("4. 통장 사본", key="f6_4")
    
    if st.button("🚀 6단계 메일 생성하기", type="primary"):
        st.session_state.generated_subject = f"[독서화랑] {school} 정식 도입 관련 계약 서류 및 증빙 자료 송부"
        st.session_state.generated_body = f"안녕하세요, {teacher} 선생님!\n독서화랑 클래스 도입을 결정해 주셔서 진심으로 감사드립니다.\n원활한 행정 처리를 위해 결재 및 계약 시 필요한 서류 일체를 준비하여 보내드립니다.\n\n1. 송부 서류 리스트\n- 독서화랑 클래스 이용 계약서(공식) 1부\n- 사업자등록증 사본 1부\n- 통장 사본(입금 계좌 확인용) 1부\n- 최종 견적서(확정 수량 반영) 1부\n\n2. 향후 진행 절차 안내\n- 계약 체결: 보내드린 계약서에 날인하여 회신 주시거나, 전자 계약(S2B/나라장터) 번호를 알려주시면 즉시 응찰하겠습니다.\n- 세금계산서 발행: 서비스 개시 시점에 맞춰 행정실과 협의하여 발행해 드릴 예정입니다.\n\n아이들이 책 읽는 즐거움을 발견하는 의미 있는 시간이 되도록 정성을 다해 준비하겠습니다. 감사합니다."

elif selected == "7. 정규 서비스 개시 안내":
    with st.expander("✅ 실무 가이드 & 체크리스트", expanded=True):
        st.info("💡 계약 후 7일 이내 발송")
        st.checkbox("1. 교사용 ID/PW 정보", key="f7_1")
        st.checkbox("2. 서비스 접속 URL", key="f7_2")
        st.checkbox("3. 이용 매뉴얼 (교사용/학생용)", key="f7_3")
        st.checkbox("4. 세금계산서", key="f7_4")

    ca, cb = st.columns(2)
    with ca:
        start_date = st.date_input("이용 시작일", key="s7")
        admin_id = st.text_input("정규 관리자 ID")
    with cb:
        end_date = st.date_input("이용 종료일", key="e7")
        admin_pw = st.text_input("정규 관리자 PW")

    if st.button("🚀 7단계 메일 생성하기", type="primary"):
        st.session_state.generated_subject = f"[독서화랑] {school} 정규 서비스 개시 안내 및 정산 서류 재송부"
        st.session_state.generated_body = f"안녕하세요, {teacher} 선생님!\n{school}의 정식 도입을 다시 한번 진심으로 환영합니다.\n요청하신 정산 절차가 모두 마무리됨에 따라, 접속 정보와 행정 서류를 최종 안내해 드립니다.\n\n1. 서비스 이용 및 관리자 계정 정보\n- 서비스 URL: https://school.dmy.co.kr/teacher/\n- 이용 기간: {start_date.strftime('%Y.%m.%d')} ~ {end_date.strftime('%Y.%m.%d')}\n- 관리 교사 계정: ID: {admin_id} / PW: {admin_pw}\n\n2. 정산 및 행정 서류\n세금계산서 및 이용 매뉴얼, 학생용 접속 가이드가 본 메일에 동봉되어 있습니다.\n\n3. [특별 지원] 서비스 교육 지원\n선생님께서 클래스를 더욱 원활하게 운영하실 수 있도록 교육을 제공하오니 필요시 말씀 부탁드립니다.\n\n선생님의 학급에 즐거운 독서 변화가 시작되기를 응원합니다! 감사합니다."

# --- 4. 결과 출력 및 Gmail 연동 ---
if st.session_state.generated_subject:
    st.divider()
    st.subheader("✉️ 생성된 메일 검토 및 최종 수정")
    
    # 생성된 내용을 사용자가 최종 수정할 수 있도록 허용
    final_sub = st.text_input("메일 제목 (최종)", value=st.session_state.generated_subject)
    final_body = st.text_area("메일 본문 (최종)", value=st.session_state.generated_body, height=400)

    # 지메일 연동 URL 생성
    params = {
        "view": "cm",
        "fs": "1",
        "to": email,
        "su": final_sub,
        "body": final_body
    }
    gmail_url = f"https://mail.google.com/mail/?{urllib.parse.urlencode(params)}"

    st.link_button("🚀 Gmail 창 열기", gmail_url, type="primary", use_container_width=True)