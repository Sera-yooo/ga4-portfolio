import streamlit as st
import src.style_utils as style

# 1. 페이지 설정
st.set_page_config(page_title="독서화랑 팀 통합 리소스", layout="wide")
style.apply_common_style()

def display_excel_list():
    st.markdown("### 🗂️ 팀 통합 리소스 관리")
    st.info("💡 모든 업무용 시트와 관리 시스템 계정을 한곳에서 관리합니다.")

    # 탭 구성
    tab1, tab2, tab3, tab4 = st.tabs(["🏛️ 내부 운영/회의", "🏫 B2G 관리", "🏠 B2C/재원생", "🔐 관리 시스템/계정"])

    # --- 카테고리 1: 내부 운영 및 회의 ---
    with tab1:
        st.write("")
        col1, col2 = st.columns(2)
        with col1:
            style.render_excel_link("내부 오류 요청 리스트", "https://docs.google.com/spreadsheets/d/1rkynolHXlzVDqwJMG3iNmd3Dze3KnzZHStcNCT2_sTI/", "시스템 및 서비스 내부 오류 리포트")
            style.render_excel_link("정기 회의록", "https://docs.google.com/spreadsheets/d/1r3QI_pHDA9eKyQTiUXnNl5rveAV0bkhDvbm1P-Thbm4/", "팀 주간/정기 회의 기록")
        with col2:
            style.render_excel_link("2026 마케팅본부 주간업무", "https://docs.google.com/spreadsheets/d/1cbbdK1jZlay460Q5DFnzncPCtIR-q3zN1_IjiPJf4Qc/", "마케팅 본부 전체 주간 현황")
            style.render_excel_link("2026 연구도서 지원 관리", "https://docs.google.com/spreadsheets/d/1BOfRV0RiaVMQS-0ojm5Pdb886Ih81R4i/edit?gid=473895659#gid=473895659", "연구 목적 도서 지원 히스토리")

    # --- 카테고리 2: B2G 관리 ---
    with tab2:
        st.write("")
        c1, c2 = st.columns(2)
        with c1:
            style.render_excel_link("교육청 공고 관리", "https://docs.google.com/spreadsheets/d/118azg5IUjsGcfnguKK9Bc2dDUUXvt_AFpFHRNU4dL9w/", "지역별 교육청 공고 모니터링")
            style.render_excel_link("26년 AI 선도학교", "https://docs.google.com/spreadsheets/d/1ktjLxG5IJuu1QiQXQpC2Tynd-3J65KwK/", "26년 타겟 선도학교 명단")
            style.render_excel_link("총판 관리 시트", "https://docs.google.com/spreadsheets/d/1LoiiCRBT9XjAPhT-38RlVk3k8hJaz52Zc4TivtawhgQ/", "파트너사 및 총판별 계약 현황")
            style.render_excel_link("학교 관리 시트", "https://docs.google.com/spreadsheets/d/1nmAhwBLloq6pFGFIWYahKh4vPQaw08xugCWHURJ076c/", "B2G 전체 학교 통합 관리")
            style.render_excel_link("도입문의 설문 데이터", "https://docs.google.com/spreadsheets/d/1nrQe-mI4kHWQ1JItIS-WDypEaDX88sDy-CjrH5_nXCo/", "홈페이지/채널 도입문의 결과")
            style.render_excel_link("체험신청 설문 데이터", "https://docs.google.com/spreadsheets/d/1q_hB7JzWUC9_1Vx_q8nVeHfekZeD3h-0A-MFPi7XKBo/", "학교 체험 신청서 인입 현황")
        with c2:
            style.render_excel_link("체험계정 발급 (총판/본사)", "https://docs.google.com/spreadsheets/d/1ZL3p5WKL_c0h5DAbLoFgULx6_n3boF5M27nuKdMPrhM/", "B2G 전용 체험 ID 관리")
            style.render_excel_link("독서화랑 클래스 CS 가이드", "https://docs.google.com/spreadsheets/d/1RUKAv5IqgcIv-2-H8sU5JVrusMfGwjpHswU55kg8k30/", "클래스 관련 CS 응대 매뉴얼")
            style.render_excel_link("연구부-디딤유 소통 (B2G)", "https://docs.google.com/spreadsheets/d/1YOBP7gulI7JFTsSWe35wW_0rmSN4p3C2Xee7hSUEzQw/", "B2G 관련 부서간 협업 소통")
            style.render_excel_link("독서화랑 클래스 도서", "https://docs.google.com/spreadsheets/d/1TDnfp_64YSviZNp96_WwrZ4pqC5q6TqtvgsTLZYqlyI/", "클래스 운영 도서 리스트")

    # --- 카테고리 3: B2C/재원생 관리 ---
    with tab3:
        st.write("")
        cl1, cl2 = st.columns(2)
        with cl1:
            style.render_excel_link("CS 운영 관리", "https://docs.google.com/spreadsheets/d/1HbOG1FE2sAonh_xHsxHHJIiFGV0fdteY/", "B2C 고객 상담 및 운영 관리")
            style.render_excel_link("체험계정 발급 (B2C)", "https://docs.google.com/spreadsheets/d/1fRD_NAG8ucp0lUA8dPHk8GljYMNgpZ6V_Fuhm6s0kwk/", "개인 체험 회원 계정 관리")
        with cl2:
            style.render_excel_link("연구부-디딤유 소통 (B2C)", "https://docs.google.com/spreadsheets/d/1ez_xh5TKmfZcS2yw-uU56dAg-ZcyNvo-gh-3Ie-xF0g/", "B2C 관련 부서간 협업 소통")

    # --- 카테고리 4: 관리 시스템 및 계정 정보 ---
    with tab4:
        st.write("")
        col_admin_1, col_admin_2 = st.columns(2)
        
        with col_admin_1:
            st.markdown("##### 🌐 주요 어드민 및 운영")
            style.render_admin_card("퍼스트 펭귄", "https://syshub.dmy.co.kr/zDsmyAdm/login.php", 
                             [{"label": "호연 님", "id": "유호연", "pw": "dsmy1111@"}])
            
            style.render_admin_card("[B2C] 독서화랑 관리자", "https://book.dmy.co.kr/zTodakAdm/login.php", 
                             [{"label": "어드민", "id": "dmybookadm", "pw": "dmybookpass"}])
            
            style.render_admin_card("[B2G] 독서화랑 클래스 관리자", "https://school.dmy.co.kr/zSchoolAdm/login.php", 
                             [{"label": "어드민", "id": "schooladm", "pw": "schoolpass"}])
            
            st.markdown("##### 📩 발송 및 홍보")
            style.render_admin_card("반값문자", "https://www.halfsms.co.kr/", 
                             [{"label": "어드민", "id": "ehransdus", "pw": "dsmy@@9964"}])
            style.render_admin_card("독서화랑 클래스 홍보사이트", "https://school.dmy.co.kr/pt.php", 
                             [{"label": "홍보 페이지", "id": "-", "pw": "-"}])

        with col_admin_2:
            st.markdown("##### 🧪 테스트 및 공유 계정")
            style.render_admin_card("독서화랑 사용자 (B2C/B2G)", "https://book.dmy.co.kr/", 
                             [{"label": "사용자 1", "id": "hwarang1234", "pw": "123456"},
                              {"label": "사용자 2", "id": "testminsung", "pw": "123456"}])
            
            style.render_admin_card("클래스 사용자 및 CS메일", "https://book.dmy.co.kr/", 
                             [{"label": "클래스 테스트", "id": "test01@didim.com", "pw": "0000"},
                              {"label": "CS 지메일", "id": "dsmycs001@gmail.com", "pw": "Nonsul25@@"}])

            st.markdown("##### 💼 파트너 및 기타")
            style.render_admin_card("에듀집", "https://edzip.kr/", 
                             [{"label": "기본 계정", "id": "dsmy2014@naver.com", "pw": "hwarang13579!"}])
            
            style.render_admin_card("네이버 (출판사 연구지원)", "https://www.naver.com", 
                             [{"label": "연구지원용", "id": "dsmy2014", "pw": "nonsul9964@"}])

            st.info(f"📞 **디딤유 연락처** \n- 이용범 대표님: 010-3107-3706 \n- 김영옥 과장님: 010-7565-2685")

    st.divider()
    st.caption("새로운 업무 시트나 관리자 계정이 추가되면 리스트를 업데이트해 주세요.")

if __name__ == "__main__":
    display_excel_list()