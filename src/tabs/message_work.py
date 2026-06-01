# =====================================================================
#  메일/문자 생성 탭 (UI)
#
#  바뀐 점
#   1) 케이스 선택 = 셀렉트 박스 → 버튼
#   2) 학교명·선생님·기간 = 순번으로 시트에서 자동 로드 (직접 입력 X)
#   3) 입력할 때마다 다시 그리지 않음 → "생성" 버튼을 누른 순간에만 본문 생성
#      (계약 수동 입력칸은 st.form 으로 묶어 버벅임 제거)
#
#  발송은 자동화하지 않습니다. 본문을 복사해서 직접 보내세요.
# =====================================================================
import pandas as pd
import streamlit as st

from src.data_loader import load_school_trial_data, load_contract_school_data
from src.mail import catalog, engine

 
# ---------- 작은 도우미들 ----------
def _fmt_date(v):
    """시트 날짜값(문자/날짜 무엇이든) -> 'YYYY-MM-DD'."""
    if v is None or str(v).strip() == "":    
        return ""
    s = str(v).strip()
    try:
        return pd.to_datetime(s).strftime("%Y-%m-%d")
    except Exception:
        return s[:10]


def _find_row(df, no):
    """순번(A열)으로 시트 한 줄 찾기. 없으면 None."""
    if df is None or df.empty or not str(no).strip():
        return None
    hit = df[df["순번"].astype(str).str.strip() == str(no).strip()]
    return hit.iloc[0] if not hit.empty else None


def _show_result(result):
    """생성 결과(제목/본문/첨부/누락) 화면 출력."""
    if result["missing"]:
        st.warning(
            "⚠️ 아직 빈 값: " + ", ".join(result["missing"])
            + "  → 본문에 ⚠️[누락:…] 로 표시됩니다. 채운 뒤 다시 생성하세요."
        )
    if result.get("attachments"):
        st.markdown("**📎 첨부 체크리스트 (직접 첨부하세요)**")
        st.markdown("\n".join(f"- {a}" for a in result["attachments"]))
    st.markdown("**📌 제목**")
    st.code(result["subject"], language="text")
    st.markdown("**📌 본문**")
    st.code(result["body"], language="text")
    st.success("👆 위 박스 우측 상단의 복사 아이콘을 눌러 사용하세요.")


# ---------- 메인 ----------
def render():
    st.subheader("📩 독서화랑 메일/문자 생성기")
    st.caption("순번으로 학교 정보를 불러오고, 버튼을 누르면 그때 본문이 생성됩니다. (발송은 직접)")

    tab_trial, tab_contract = st.tabs(["🔍 체험 학교 안내 (메일/문자)", "📣 정규 계약 학교 안내"])

    # =================================================================
    # [체험] 메일 / 문자
    # =================================================================
    with tab_trial:
        df = load_school_trial_data()
        no = st.text_input("체험 시트 순번(A열) 입력", key="mw_trial_no")
        row = _find_row(df, no)

        # 순번이 바뀌면 이전에 생성한 결과를 지운다(다른 학교 본문이 남는 것 방지)
        if st.session_state.get("mw_trial_last_no") != no:
            st.session_state.pop("mw_trial_result", None)
            st.session_state["mw_trial_last_no"] = no

        if no and row is None:
            st.error("❌ 해당 순번을 찾을 수 없습니다.")

        if row is not None:
            st.success(f"✅ [{row['학교명']}] 정보 로드 완료")

            ctx = {
                "sch": row.get("학교명", ""),
                "tea": row.get("교사명", ""),
                "s_str": _fmt_date(row.get("시작일", "")),
                "e_str": _fmt_date(row.get("종료일", "")),
            }

            with st.container(border=True):
                c1, c2 = st.columns(2)
                c1.text_input("학교명", value=ctx["sch"], disabled=True)
                c2.text_input("체험 기간", value=f"{ctx['s_str']} ~ {ctx['e_str']}",
                              disabled=True)
                c1.text_input("선생님 성함", value=ctx["tea"], disabled=True)
                st.caption("선생님 성함이 비어 있으면 시트 F열을 확인하세요. (계정은 항상 TEST 고정)")

            b1, b2 = st.columns(2)
            gen = None
            if b1.button("📧 체험 메일 생성", type="primary", use_container_width=True, key="mw_t_mail"):
                gen = "trial_mail"
            if b2.button("📱 체험 문자 생성", use_container_width=True, key="mw_t_sms"):
                gen = "trial_sms"

            if gen:
                st.session_state["mw_trial_result"] = engine.build(catalog.CASES[gen], ctx)

            if st.session_state.get("mw_trial_result"):
                st.divider()
                _show_result(st.session_state["mw_trial_result"])

    # =================================================================
    # [계약] 세팅완료 / 정규개시 / 명단요청
    # =================================================================
    with tab_contract:
        cdf = load_contract_school_data()
        cno = st.text_input("계약 시트 순번(A열) 입력", key="mw_c_no")
        crow = _find_row(cdf, cno)

        # 순번이 바뀌면 이전에 생성한 결과 + 직접 입력값(교사수/인원/비번)을 모두 초기화
        if st.session_state.get("mw_contract_last_no") != cno:
            for k in ("mw_contract_result", "mw_c_pw", "mw_c_nt", "mw_c_ntot"):
                st.session_state.pop(k, None)
            st.session_state["mw_contract_last_no"] = cno

        if cno and crow is None:
            st.error("❌ 해당 순번을 찾을 수 없습니다.")

        if crow is not None:
            st.success(f"✅ [{crow['학교명']}] 정보 로드 완료")

            # 시트에서 자동으로 채워지는 값
            # 관리교사명/관리교사이메일이 비어 있으면 = 아직 관리교사 미정.
            # 다른 값으로 메꾸지 않고 빈 채로 둬서 누락(⚠️)으로 잡히게 한다.
            base = {
                "sch": str(crow.get("학교명", "")).strip(),
                "tea": str(crow.get("관리교사명", "")).strip(),
                "s_str": _fmt_date(crow.get("시작일", "")),
                "e_str": _fmt_date(crow.get("종료일", "")),
                "adm_id": str(crow.get("관리교사이메일", "")).strip(),
                "n_student": str(crow.get("계약학생수", "")).strip(),
            }

            # 입력칸 + 버튼을 form 으로 묶음 → 버튼 누르기 전엔 다시 안 그려짐(버벅임 X)
            with st.form("mw_contract_form"):
                c1, c2 = st.columns(2)
                c1.text_input("계약 학교명", value=base["sch"], disabled=True)
                c2.text_input("이용 기간", value=f"{base['s_str']} ~ {base['e_str']}",
                              disabled=True)
                c1.text_input("담당 선생님", value=base["tea"], disabled=True)
                c2.text_input("관리자 ID (메일)", value=base["adm_id"], disabled=True)

                st.markdown("###### ✍️ 직접 입력 (시트에 없는 값만)")
                d1, d2, d3 = st.columns(3)
                adm_pw = d1.text_input("초기 비밀번호", value="0000", key="mw_c_pw")
                n_teacher = d2.text_input("교사 수 (① 세팅완료용)", value="", key="mw_c_nt")
                n_total = d3.text_input("명단 인원 전체 (② 정규개시용)", value="", key="mw_c_ntot")

                st.caption("아래에서 보낼 메일 종류를 누르면 그때 본문이 생성됩니다.")
                bc1, bc2, bc3 = st.columns(3)
                s1 = bc1.form_submit_button("① 세팅완료", use_container_width=True)
                s2 = bc2.form_submit_button("② 정규개시", use_container_width=True)
                s3 = bc3.form_submit_button("③ 명단요청", use_container_width=True)

            # form 제출 시점의 값으로 ctx 구성
            ctx = dict(base)
            ctx["adm_pw"] = adm_pw
            ctx["n_teacher"] = n_teacher
            ctx["n_total"] = n_total

            gen = None
            if s1:
                gen = "contract_setup_done"
            elif s2:
                gen = "contract_admin"
            elif s3:
                gen = "contract_request"

            if gen:
                st.session_state["mw_contract_result"] = engine.build(catalog.CASES[gen], ctx)

            if st.session_state.get("mw_contract_result"):
                st.divider()
                _show_result(st.session_state["mw_contract_result"])
