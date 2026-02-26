import streamlit as st
import datetime

# --- 0. 공통 정보 설정 (전역 변수) ---
# 이 부분만 수정하면 모든 메일 템플릿의 문의처가 한 번에 변경됩니다.
CONTACT_INFO = """[문의]
서비스 문의: 사이트 하단 [이용문의] 클릭
메일: dsmycs001@gmail.com
전화: 02-593-9964"""

# --- 1. 기본 화면 설정 ---
st.set_page_config(page_title="독서화랑 CS 메일 생성기", page_icon="📚", layout="wide")

st.title("📚 독서화랑 메일 자동 생성기")
st.markdown("왼쪽에서 템플릿을 선택하고 정보를 입력하면 발송용 메일 본문이 완성됩니다.")
st.divider()

# --- 2. 템플릿 선택 (사이드바 활용) ---
template_options = [
    "1. 체험 신청 확인 및 계정 생성",
    "2. 미응답 메세지 재발송",
    "3. 체험 중간 설문 메세지",
    "4. 계약 전환 상담",
    "5. 견적서 발행",
    "6. 계약의사 확인 후 계약서 송부",
    "7. 계정 생성 및 정규 서비스 개시 안내"
]

with st.sidebar:
    st.header("📌 발송 단계 선택")
    selected = st.radio("템플릿을 선택하세요:", template_options)

# --- 3. 템플릿별 동적 입력창 및 결과 생성 ---

if selected == "1. 체험 신청 확인 및 계정 생성":
    st.subheader("📝 1단계: 체험 신청 확인")
    col1, col2 = st.columns(2)
    with col1:
        school = st.text_input("학교명 (예: 서울초)")
        teacher = st.text_input("교사명")
    with col2:
        # 텍스트 입력 대신 달력 위젯(date_input) 사용
        start_date = st.date_input("시작일")
        end_date = st.date_input("종료일")
    
    col3, col4 = st.columns(2)
    with col3:
        admin_id = st.text_input("관리자 ID")
    with col4:
        admin_pw = st.text_input("관리자 PW")

    st.subheader("📎 필수 첨부/확인 사항")
    chk1 = st.checkbox("1. 서비스 홈페이지 링크")
    chk2 = st.checkbox("2. 서비스 소개 파일")
    chk3 = st.checkbox("3. (교사용/학생용)이용안내 매뉴얼")
    chk4 = st.checkbox("4. 퀵 매뉴얼 파일")
    chk5 = st.checkbox("5. 이용 확인서")

    if st.button("메일 생성하기", type="primary"):
        if chk1 and chk2 and chk3 and chk4 and chk5:
            st.success("✅ 첨부파일 및 확인 사항 체크 완료!")
            # strftime을 사용해 날짜를 원하는 형식으로 변경
            mail_text = f"""제목: [독서화랑] {school} 체험 신청 감사 및 서비스 이용 안내

안녕하세요, {school} {teacher} 선생님!
우리 아이들을 위한 똑똑한 독서 파트너, 독서화랑 클래스입니다.

신청해주신 체험 서비스가 정상적으로 접수되었습니다. 원활한 체험을 위해 아래 정보를 확인해 주세요.

[서비스 접속 정보]

체험 기간: {start_date.strftime('%Y.%m.%d')} ~ {end_date.strftime('%Y.%m.%d')}
접속 URL: [https://school.dmy.co.kr/teacher/]
선생님 관리자 ID: {admin_id} / PW: {admin_pw}

[이용 시 확인 사항]
체험용 계정 정보는 종료 후 일괄 삭제됩니다.
콘텐츠의 무단 복제 및 배포는 엄격히 금지됩니다.
체험 종료 후 간단한 피드백(설문)에 협조 부탁드립니다.

아이들이 독서의 즐거움을 느끼고 선생님의 수업이 더 편리해질 수 있도록 최선을 다하겠습니다. 감사합니다.

{CONTACT_INFO}"""
            st.code(mail_text, language="text")
        else:
            st.error("⚠️ 필수 첨부파일 및 확인 사항을 모두 체크해 주세요.")

elif selected == "2. 미응답 메세지 재발송":
    st.subheader("📝 2단계: 미응답 리마인드")
    teacher = st.text_input("교사명")
    title_idea = st.text_input("제목 입력 (예: 체험 안내 메일 확인 부탁드립니다 😊)", value="체험 안내 메일 확인 부탁드립니다 😊")
    link = st.text_input("신청 내용 다시보기 링크")

    if st.button("메일 생성하기", type="primary"):
        mail_text = f"""제목: [독서화랑 클래스] {title_idea}

안녕하세요, {teacher} 선생님! 며칠 전 보내드린 체험 안내 메일을 혹시 놓치셨을까 하여 짧게 문자 남깁니다. 😊

혹시 메일을 받지 못하셨거나 접속에 어려움이 있으시다면 언제든 답장이나 아래 링크로 말씀해 주세요. 바로 다시 안내해 드리겠습니다!

신청 내용 다시보기: [{link}]

{CONTACT_INFO}"""
        st.code(mail_text, language="text")

elif selected == "3. 체험 중간 설문 메세지":
    st.subheader("📝 3단계: 중간 점검 설문")
    teacher = st.text_input("교사명")
    survey_link = st.text_input("설문 링크 URL")

    if st.button("메일 생성하기", type="primary"):
        mail_text = f"""제목: [독서화랑] 선생님, 아이들과의 체험은 어떠신가요?

안녕하세요, {teacher} 선생님! 독서화랑 클래스와 함께하는 독서 시간이 아이들에게 즐거운 경험이 되고 있는지 궁금합니다. 😊

이용 중 불편한 점은 없으셨나요? 
더 나은 서비스를 위해 짧은 [중간 점검 설문]을 준비했습니다. 1분만 시간을 내어 주시면 큰 도움이 되겠습니다.

중간 설문조사: [{survey_link}]

{CONTACT_INFO}"""
        st.code(mail_text, language="text")

elif selected == "4. 계약 전환 상담":
    st.subheader("📝 4단계: 계약 전환 유도")
    teacher = st.text_input("교사명")
    end_date = st.date_input("체험 종료일")
    benefits = st.text_area("🎁 정규 전환 특별 혜택 (직접 입력)", value="1. 전교생 대상 독서 리포트 무료 제공\n2. 연간 결제 시 1개월 추가 혜택")

    st.subheader("📎 필수 첨부/확인 사항")
    chk1 = st.checkbox("1. 정규 도입 제안서")

    if st.button("메일 생성하기", type="primary"):
        if chk1:
            st.success("✅ 첨부파일 확인 완료!")
            mail_text = f"""제목: [독서화랑] 체험 종료 및 정규 도입 혜택 안내

안녕하세요, {teacher} 선생님.
아이들과 함께한 체험이 {end_date.strftime('%Y.%m.%d')}에 만료될 예정입니다. 
지금의 독서 습관을 정규 과정으로 이어가실 수 있도록 특별 혜택을 안내해 드립니다.

🎁 정규 전환 특별 혜택
{benefits}

아이들의 독서 근육이 튼튼해질 수 있도록 끝까지 함께하겠습니다. 감사합니다.

{CONTACT_INFO}"""
            st.code(mail_text, language="text")
        else:
            st.error("⚠️ 필수 첨부파일(정규 도입 제안서)을 체크해 주세요.")

elif selected == "5. 견적서 발행":
    st.subheader("📝 5단계: 견적서 송부")
    school = st.text_input("학교명/기관명")
    teacher = st.text_input("교사명/담당자명")
    core_benefits = st.text_area("독서화랑 클래스만의 핵심 혜택 (선택사항)")

    st.subheader("📎 필수 첨부/확인 사항")
    chk1 = st.checkbox("1. 독서화랑 class 견적서")

    if st.button("메일 생성하기", type="primary"):
        if chk1:
            st.success("✅ 첨부파일 확인 완료!")
            mail_text = f"""제목: [독서화랑] {school} 온라인 독서 클래스 도입 견적서 및 행정 서류 송부

안녕하세요, {teacher} 선생님! (혹은 담당자님)
우리 아이들을 위한 똑똑한 독서 파트너, 독서화랑 클래스 마케팅팀입니다.

문의하신 서비스 도입을 위해 필요한 견적서와 관련 행정 서류를 준비하여 보내드립니다. 독서화랑 클래스는 단순한 도서 제공을 넘어, 선생님의 수업 편의성과 아이들의 독서 역량 강화를 최우선으로 생각합니다.

1. 송부 서류 리스트
독서화랑 class 견적서 1부

2. 독서화랑 클래스만의 핵심 혜택
{core_benefits}

3. 안내 사항
본 견적서의 유효기간은 발행일로부터 30일입니다.
추가 서류가 필요하신 경우 말씀해 주시면 즉시 재발행해 드리겠습니다.

검토 후 도입 의사를 밝혀주시면 정식 계약 절차와 계정 발급을 신속히 진행하도록 하겠습니다. 

아이들이 책과 더 가까워지는 즐거운 변화를 독서화랑이 함께하겠습니다.

감사합니다.

{CONTACT_INFO}"""
            st.code(mail_text, language="text")
        else:
            st.error("⚠️ 필수 첨부파일(독서화랑 class 견적서)을 체크해 주세요.")

elif selected == "6. 계약의사 확인 후 계약서 송부":
    st.subheader("📝 6단계: 계약 서류 송부")
    school = st.text_input("학교명/기관명")
    teacher = st.text_input("교사명/담당자명")
    core_benefits = st.text_area("독서화랑 클래스만의 핵심 혜택 (선택사항)")

    st.subheader("📎 필수 첨부/확인 사항 [수의계약]")
    chk1 = st.checkbox("1. 계약서")
    chk2 = st.checkbox("2. 견적서(최종)")
    chk3 = st.checkbox("3. 사업자등록증")
    chk4 = st.checkbox("4. 통장사본")

    if st.button("메일 생성하기", type="primary"):
        if chk1 and chk2 and chk3 and chk4:
            st.success("✅ 첨부파일 확인 완료!")
            mail_text = f"""제목: [독서화랑] {school} 정식 도입 관련 계약 서류 및 행정 증빙 자료 송부

안녕하세요, {teacher} 선생님!
우리 아이들을 위한 똑똑한 독서 파트너, 독서화랑 클래스 마케팅팀입니다.

독서화랑 클래스 도입을 결정해 주셔서 진심으로 감사드립니다. 
원활한 행정 처리를 위해 {teacher}께서 결재 및 계약 시 필요한 서류 일체를 준비하여 보내드립니다.

1. 송부 서류 리스트
독서화랑 클래스 이용 계약서(공식) 1부
사업자등록증 사본 1부
통장 사본(입금 계좌 확인용) 1부
최종 견적서(확정 수량 반영) 1부

2. 독서화랑 클래스만의 핵심 혜택
{core_benefits}

3. 향후 진행 절차 안내
계약 체결: 보내드린 계약서에 날인하여 회신 주시거나, 학교장터(S2B) 혹은 나라장터를 통한 전자 계약 번호를 알려주시면 즉시 응찰하겠습니다.
세금계산서 발행: 서비스 개시 시점에 맞춰 행정실(정산 담당자)과 협의하여 발행해 드릴 예정입니다.

문의 사항: 추가로 필요한 행정 서류(등기부등본, 완납증명서 등)가 있으시면 언제든 말씀해 주세요.

아이들이 책 읽는 즐거움을 발견하는 의미 있는 시간이 되도록 정성을 다해 준비하겠습니다.

감사합니다.

{CONTACT_INFO}"""
            st.code(mail_text, language="text")
        else:
            st.error("⚠️ 수의계약에 필요한 4가지 서류를 모두 체크해 주세요.")

elif selected == "7. 계정 생성 및 정규 서비스 개시 안내":
    st.subheader("📝 7단계: 정규 서비스 개시")
    school = st.text_input("학교명")
    teacher = st.text_input("관리 교사명")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("이용 시작일")
        admin_id = st.text_input("발급 ID")
    with col2:
        end_date = st.date_input("이용 종료일")
        admin_pw = st.text_input("발급 PW")

    st.subheader("📎 필수 첨부/확인 사항")
    chk1 = st.checkbox("1. 교사용 ID/PW")
    chk2 = st.checkbox("2. 서비스 URL: [독서화랑 클래스 접속 링크]")
    chk3 = st.checkbox("3. (교사용/학생용)이용안내 매뉴얼")
    chk4 = st.checkbox("4. 세금 계산서")

    if st.button("메일 생성하기", type="primary"):
        if chk1 and chk2 and chk3 and chk4:
            st.success("✅ 첨부파일 및 정보 확인 완료!")
            mail_text = f"""제목: [독서화랑] {school} 정규 서비스 개시 안내 및 정산 서류(세금계산서) 재송부

안녕하세요, {teacher} 선생님!
우리 아이들을 위한 똑똑한 독서 파트너, 독서화랑 클래스입니다.

{school}의 정식 도입을 다시 한번 진심으로 환영합니다. 
요청하신 정산 절차가 모두 마무리됨에 따라, 정규 클래스 접속 정보와 행정 서류를 최종 안내해 드립니다.

1. 서비스 이용 및 관리자 계정 정보
서비스 URL: https://school.dmy.co.kr/teacher/
이용 기간: {start_date.strftime('%Y.%m.%d')} ~ {end_date.strftime('%Y.%m.%d')}
관리 교사 계정: ID: {admin_id} / PW: {admin_pw}

2. 정산 완료 및 행정 서류 안내
세금계산서: 협의된 정산 일정에 따라 발행된 전자세금계산서를 본 메일에 동봉합니다. (또는 행정실에도 별도 전달되었습니다.)

첨부 서류: 1. 독서화랑 클래스 학생용/교사용 이용 매뉴얼 2. 학생용 접속 가이드 3. 정산 증빙 서류

3. [특별 지원] 서비스 교육 지원 
선생님께서 클래스를 더욱 원활하게 운영하실 수 있도록 시연 및 활용법 교육을 제공합니다.
지원 내용: 관리자 페이지 활용법, 학생 독서 데이터 확인 방법, 수업 적용 팁
신청 방법: 교육 지원이 필요하신 경우 원하시는 날짜와 시간을 회신 주시면 일정을 조율하여 신속히 도와드리겠습니다.

이용 중 궁금하신 점은 언제든 말씀해 주세요.

선생님의 학급에 즐거운 독서 변화가 시작되기를 응원합니다!

{CONTACT_INFO}"""
            st.code(mail_text, language="text")
        else:
            st.error("⚠️ 필수 첨부파일 및 확인 사항을 모두 체크해 주세요.")