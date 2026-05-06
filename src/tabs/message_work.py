import streamlit as st
import pandas as pd
import sys
import os
from datetime import date, timedelta

# 1. 경로 설정 및 모듈 로드
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

from src.modules.message_manager import MessageTemplateManager
from src.data_loader import load_school_trial_data, load_contract_school_data 

# --- [공통 함수 1] 날짜 안전하게 파싱 ---
def safe_parse_date(date_str, default_date):
    try:
        if not date_str or pd.isna(date_str):
            return default_date
        return pd.to_datetime(date_str).date()
    except:
        return default_date

# --- [공통 함수 2] 매뉴얼 링크 자동 생성 ---
def get_manual_links(selected_docs):
    links = []
    if "상세 가이드 링크" in selected_docs:
        links.append("- 상세 메뉴얼 다운로드 : https://drive.google.com/drive/folders/1EOoPtolllNWbUgst_ki8hv-purrh3to0")
        #links.append("- 일반교사용: https://drive.google.com/drive/folders/15oAEQMXyBwh95_xEbdTQuvKr3aRBP_is")
    if "학운위 체크리스트" in selected_docs:
        links.append("- 학운위 체크리스트 다운로드: https://drive.google.com/file/d/1Prg8hOxVQ396BDREX1OAvtJBi0flTExF")
        #links.append("- 학운위(PPT): https://docs.google.com/presentation/d/1YPrYwDKA3IJYIuWs2fRSc4v0C4pV3u8I")
    
    if links:
        return "\n[상세 매뉴얼 및 자료 다운로드]\n" + "\n".join(links) + "\n"
    return ""

# --- [메인 렌더링 함수] ---
def render():
    st.subheader("📩 독서화랑 CS 메시지 자동 생성기")
    
    mm = MessageTemplateManager()
    
    tab_trial, tab_contract = st.tabs([
        "🔍 체험 학교 안내 (메일/문자)", 
        "🎓 정규 계약 학교 안내"
    ])

    # =========================================================
    # [탭 1] 체험 학교 안내 (첨부파일 선택 + 버튼 분리형)
    # =========================================================
    with tab_trial:
        db_trial = load_school_trial_data()
        search_no = st.text_input("체험 시트 순번(A열) 입력", key="trial_search_no")
        
        if search_no and not db_trial.empty:
            match = db_trial[db_trial['순번'] == search_no.strip()]
            if not match.empty:
                row = match.iloc[0]
                
                # 데이터 세션 동기화
                st.session_state["t_sch"] = row['학교명']
                st.session_state["t_tea"] = row['교사명']
                st.session_state["t_id"] = row['체험교사계정']
                
                st.success(f"✅ [{row['학교명']}] 정보 로드 완료")
                
                with st.container(border=True):
                    c1, c2 = st.columns(2)
                    with c1:
                        t_sch = st.text_input("학교명", key="t_sch")
                        t_tea = st.text_input("선생님 성함", key="t_tea")
                        t_id = st.text_input("관리자 ID", key="t_id")
                    with c2:
                        t_start = safe_parse_date(row['시작일'], date.today())
                        t_end_raw = safe_parse_date(row['종료일'], None)
                        
                        t_default = [t_start, t_end_raw] if t_end_raw else [t_start, t_start]
                        t_dates = st.date_input("체험 기간", t_default, key="t_dates_picker")
                        
                        if not t_end_raw:
                            st.caption("⚠️ 종료일 정보가 없어 '미정'으로 표시됩니다.")

                # 첨부 서류 선택 영역 (링크 생성용 옵션 추가)
                t_docs = st.multiselect(
                    "📄 포함 서류 선택 (체험용)",
                    ["서비스 소개서", "사용자별 퀵 가이드", "상세 가이드 링크", "학운위 체크리스트"],
                    default=["서비스 소개서", "사용자별 퀵 가이드"],
                    key="t_docs_sel"
                )

                # 버튼 영역 (2열 배치)
                btn_col1, btn_col2 = st.columns(2)
                selected_type = None
                
                with btn_col1:
                    if st.button("📧 메일 버전 생성", use_container_width=True):
                        selected_type = "mail"
                with btn_col2:
                    if st.button("💬 문자 버전 생성", use_container_width=True):
                        selected_type = "sms"

                # 메시지 생성 로직
                if selected_type:
                    s_str = t_dates[0].strftime('%Y-%m-%d')
                    e_str = t_dates[1].strftime('%Y-%m-%d') if len(t_dates) > 1 and t_end_raw else "(미정/협의 필요)"

                    # 1. 매뉴얼 링크 자동 생성 (함수 호출)
                    manual_section = get_manual_links(t_docs)

                    # 2. 링크 전용 항목을 제외한 일반 첨부파일 목록 가공
                    attachment_list = [f"- {doc}" for doc in t_docs if doc not in ["상세 가이드 링크", "학운위 체크리스트"]]
                    attachment_text = "\n".join(attachment_list) if attachment_list else "없음"

                    template_key = "trial_notice_mail" if selected_type == "mail" else "trial_notice_sms"
                    
                    subject, body = mm.get_rendered_message(
                        template_key,
                        sch=t_sch, tea=t_tea, a_id=t_id, a_pw="0000",
                        s_str=s_str, 
                        e_str=e_str,
                        s1_id=row['학생1_ID'], s2_id=row['학생2_ID'],
                        manual_section=manual_section,     # 링크 삽입
                        attachment_text=attachment_text    # 첨부파일 삽입
                    )
                    
                    st.divider()
                    label = "📧 메일 버전" if selected_type == "mail" else "💬 문자 버전"
                    st.info(f"**[{label}] 생성 결과**")
                    
                    if selected_type == "mail":
                        st.markdown(f"**제목:** {subject}")
                    st.code(body, language="plaintext")
            else:
                st.error("❌ 해당 순번의 체험 데이터를 찾을 수 없습니다.")

    # =========================================================
    # [탭 2] 계약 학교 안내 (명단 세팅 현황 수동 입력 버전)
    # =========================================================
    with tab_contract:
        db_contract = load_contract_school_data()
        c_search_no = st.text_input("계약 시트 순번(A열) 입력", key="contract_search_no")

        if c_search_no and not db_contract.empty:
            c_match = db_contract[db_contract['순번'] == c_search_no.strip()]
            if not c_match.empty:
                c_row = c_match.iloc[0]
                
                # 담당자 정보 세팅
                d_name = c_row['관리교사명'] if c_row['관리교사명'] else c_row['계약교사명']
                d_email = c_row['관리교사이메일'] if c_row['관리교사이메일'] else c_row['계약교사이메일']

                st.session_state["c_sch_in"] = c_row['학교명']
                st.session_state["c_tea_in"] = d_name
                st.session_state["c_id_in"] = d_email
                
                st.success(f"✅ [{c_row['학교명']}] 정보 로드 완료")

                with st.container(border=True):
                    cc1, cc2 = st.columns(2)
                    with cc1:
                        c_sch = st.text_input("계약 학교명", key="c_sch_in")
                        c_tea = st.text_input("담당 선생님", key="c_tea_in")
                        c_id = st.text_input("관리자 ID (메일)", key="c_id_in")
                    with cc2:
                        c_start = safe_parse_date(c_row['시작일'], date.today())
                        c_end_raw = safe_parse_date(c_row['종료일'], None)
                        
                        default_dates = [c_start, c_end_raw] if c_end_raw else [c_start, c_start]
                        c_dates = st.date_input("이용 기간", default_dates, key="c_dates_picker_c")
                        
                        if not c_end_raw:
                            st.caption("⚠️ 종료일 정보가 없어 '미정'으로 표시됩니다.")

                        c_setup = st.text_area(
                            "명단 세팅 현황", 
                            value="전달해주신 명단 및 계약 인원(00명) 세팅 완료",
                            key="c_setup_in"
                        )

                # 선택지에 링크 자동 생성 트리거들 모두 포함
                c_docs = st.multiselect(
                    "📄 포함 서류 선택",
                    ["사용자별 퀵 가이드", "상세 가이드 링크", "서비스 소개서", "학생 계정 명단", "학생/교사 업로드용 양식","학운위 체크리스트"],
                    default=["사용자별 퀵 가이드", "상세 가이드 링크", "학생/교사 업로드용 양식", "학운위 체크리스트"],
                    key="c_docs_sel"
                )

                if st.button("🚀 정규 계약 안내문 생성", type="primary", use_container_width=True):
                    s_str = c_dates[0].strftime('%Y-%m-%d')
                    if len(c_dates) > 1 and c_end_raw:
                        e_str = c_dates[1].strftime('%Y-%m-%d')
                    else:
                        e_str = "(미정/협의 필요)"

                    # 1. 매뉴얼 링크 자동 생성
                    manual_section = get_manual_links(c_docs)
                    
                    # 2. 첨부파일 목록 동적 생성
                    a_list = []
                    if "사용자별 퀵 가이드" in c_docs:
                        a_list.append("- 1. 사용자별 퀵 가이드: 관리 선생님용 / 일반 선생님용 / 학생용")
                    
                    for doc in c_docs:
                        # 이미 처리된 항목은 제외
                        if doc not in ["상세 가이드 링크", "학운위 체크리스트", "사용자별 퀵 가이드"]:
                            # 양식 파일 이름 커스텀
                            if doc == "학생/교사 업로드용 양식":
                                a_list.append(f"[{c_sch}_독서화랑_계정_신청서_교사학생] 엑셀 파일")                            
                            else:
                                a_list.append(f"- {doc}")

                    attachment_text = "\n".join(a_list) if a_list else "없음"
                    setup_info = c_setup if c_setup.strip() else ""

                    subject, body = mm.get_rendered_message(
                        "contract_notice",
                        sch=c_sch, tea=c_tea, a_id=c_id, a_pw="0000",
                        s_str=s_str, 
                        e_str=e_str,
                        student_setup_info=setup_info,
                        contract_manual_section=manual_section, # 링크 삽입
                        attachment_text=attachment_text         # 첨부파일 삽입
                    )
                    
                    st.divider()
                    st.info(f"**제목:** {subject}")
                    st.code(body, language="plaintext")
            else:
                st.error("❌ 해당 순번의 데이터를 찾을 수 없습니다.")

if __name__ == "__main__":
    render()