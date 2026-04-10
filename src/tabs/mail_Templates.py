import streamlit as st
import yaml
import os

def render():
    st.subheader("✉️ 표준 응대 문구 확인")
    st.info("💡 아래 문구는 `src/templates/mail_templates.yaml` 파일에서 관리됩니다. 수정이 필요하면 해당 파일을 업데이트하세요.")

    # 1. YAML 로드 함수
    def load_templates():
        # 최상위 루트 기준 경로
        file_path = "src/templates/mail_templates.yaml"
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        return None

    templates = load_templates()

    if not templates:
        st.error("⚠️ 문구 파일(YAML)을 찾을 수 없습니다. 경로를 확인해 주세요.")
        return

    # 2. 화면 구성 (탭으로 깔끔하게 분리)
    m_tab1, m_tab2, m_tab3 = st.tabs(["📧 체험(Mail)", "📱 체험(SMS)", "📢 정규 계약"])

    with m_tab1:
        data = templates.get('trial_notice_mail', {})
        st.markdown(f"**제목:** `{data.get('subject', '제목 없음')}`")
        st.code(data.get('body', ''), language="text")
        st.caption("✅ 필수 치환: {{sch}}(학교명), {{tea}}(선생님), {{s_str}}~{{e_str}}(기간)")

    with m_tab2:
        data = templates.get('trial_notice_sms', {})
        st.markdown(f"**제목:** `{data.get('subject', '제목 없음')}`")
        st.code(data.get('body', ''), language="text")
        st.warning("⚠️ 문자는 글자 수 제한이 있으니 복사 후 길이를 확인하세요.")

    with m_tab3:
        data = templates.get('contract_notice', {})
        st.markdown(f"**제목:** `{data.get('subject', '제목 없음')}`")
        st.code(data.get('body', ''), language="text")