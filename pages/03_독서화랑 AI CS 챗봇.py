import streamlit as st
import os
import pandas as pd
import datetime
import google.generativeai as genai

# ==========================================
# [설정] 0. 페이지 설정
# ==========================================
st.set_page_config(page_title="독서화랑 AI 챗봇", page_icon="🤖", layout="wide")

# ==========================================
# [설정] 1. API 키 설정
# ==========================================
MY_API_KEY = st.secrets["gemini_api_key"]

if MY_API_KEY == "여기에_API_키를_붙여넣으세요" or not MY_API_KEY:
    st.error("🚨 API 키가 설정되지 않았습니다.")
    st.stop()
else:
    genai.configure(api_key=MY_API_KEY.strip())

# ==========================================
# [설정] 2. 파일 경로 설정
# ==========================================
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# 지식 데이터 파일들
FILES = {
    "policy": {"path": os.path.join(CURRENT_DIR, "policy.md"), "name": "운영 정책", "type": "md"},
    "faq": {"path": os.path.join(CURRENT_DIR, "faq.csv"), "name": "FAQ DB", "type": "csv"},
    "persona": {"path": os.path.join(CURRENT_DIR, "persona.txt"), "name": "페르소나", "type": "txt"}
}

# [NEW] 로그 저장용 DB 파일 경로 (서버 저장소)
DB_PATH = os.path.join(CURRENT_DIR, "chat_history_db.csv")

# ==========================================
# [함수] 백엔드 로직
# ==========================================
def save_file(uploaded_file, path):
    try:
        with open(path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return True
    except Exception as e:
        st.error(f"저장 실패: {e}")
        return False

def get_file_info(path):
    if os.path.exists(path):
        return datetime.datetime.fromtimestamp(os.path.getmtime(path)).strftime('%Y-%m-%d %H:%M')
    return None 

def create_rag_prompt():
    persona = "당신은 '독서화랑'의 친절한 AI 상담원입니다."
    if os.path.exists(FILES['persona']['path']):
        with open(FILES['persona']['path'], "r", encoding="utf-8") as f:
            persona = f.read()
    
    knowledge = ""
    if os.path.exists(FILES['policy']['path']):
        with open(FILES['policy']['path'], "r", encoding="utf-8") as f:
            knowledge += f"\n[운영 정책]\n{f.read()}\n"
    
    if os.path.exists(FILES['faq']['path']):
        try:
            try:
                df = pd.read_csv(FILES['faq']['path'], encoding='utf-8')
            except UnicodeDecodeError:
                df = pd.read_csv(FILES['faq']['path'], encoding='cp949')
            q_col = next((c for c in df.columns if any(k in c for k in ['질문', 'Q'])), None)
            a_col = next((c for c in df.columns if any(k in c for k in ['답변', 'A'])), None)
            if q_col and a_col:
                faq_text = "\n".join([f"Q: {row[q_col]} / A: {row[a_col]}" for _, row in df.iterrows()])
                knowledge += f"\n[FAQ 데이터베이스]\n{faq_text}\n"
        except:
            pass 

    return f"""
    {persona}
    [참고 지식 데이터]
    {knowledge}
    [지시사항]
    1. 위 지식 데이터를 기반으로 답변하세요.
    2. 지식에 없는 내용은 "죄송합니다, 상담원 연결이 필요합니다."라고 답하세요.
    """

# ==========================================
# [UI] 화면 구성
# ==========================================
st.title("🤖 독서화랑 AI CS 챗봇")
st.markdown("RAG(검색 증강 생성) 기술을 적용하여 **운영 정책**과 **FAQ**를 기반으로 답변합니다.")

tab1, tab2, tab3 = st.tabs(["💬 채팅 상담", "⚙️ 관리자 설정", "📂 상담 내역 (Server DB)"])

# --- 탭 1: 채팅 인터페이스 ---
with tab1:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if user_input := st.chat_input("문의사항을 입력해주세요..."):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.messages.append({"role": "user", "content": user_input, "timestamp": now})
        
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("생각 중..."):
                try:
                    system_prompt = create_rag_prompt()
                    model = genai.GenerativeModel('gemini-2.5-flash') 
                    response = model.generate_content(f"{system_prompt}\n\n사용자 질문: {user_input}")
                    
                    st.write(response.text)
                    now_ai = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    st.session_state.messages.append({"role": "assistant", "content": response.text, "timestamp": now_ai})
                    
                except Exception as e:
                    st.error(f"오류: {e}")

# --- 탭 2: 관리자 설정 ---
with tab2:
    st.header("⚙️ 지식 데이터 관리")
    st.markdown("학습용 파일을 관리합니다.")
    st.divider()
    col1, col2, col3 = st.columns(3)
    for i, (key, info) in enumerate(FILES.items()):
        with [col1, col2, col3][i]:
            last_modified = get_file_info(info['path'])
            if last_modified:
                st.success(f"✅ **{info['name']}**")
                st.caption(f"반영 중 ({last_modified})")
            else:
                st.error(f"❌ **{info['name']}**")
                st.caption("⚠️ 파일 없음")

            if f"uploader_key_{key}" not in st.session_state:
                st.session_state[f"uploader_key_{key}"] = 0
            unique_key = f"{key}_{st.session_state[f'uploader_key_{key}']}"

            uploaded = st.file_uploader(f"{info['name']} 선택", type=info['type'], key=unique_key)
            if uploaded:
                if save_file(uploaded, info['path']):
                    st.session_state[f"uploader_key_{key}"] += 1
                    st.toast(f"{info['name']} 업로드 성공!", icon="🎉")
                    st.rerun()

# --- 탭 3: 상담 내역 (DB 자동 연동) ---
with tab3:
    st.header("📂 전체 상담 이력 (Server DB)")
    st.markdown("서버에 저장된 모든 상담 내역을 **자동으로 불러옵니다.**")
    
    col_left, col_right = st.columns([1, 3])

    # 1. 저장 기능 (현재 대화 -> DB에 추가)
    with col_left:
        st.info("현재 대화 세션을 서버 DB에 영구 저장합니다.")
        if st.button("💾 지금 대화 저장하기 (Append)", type="primary"):
            if st.session_state.messages:
                # 현재 세션 데이터프레임 변환
                new_data = pd.DataFrame(st.session_state.messages)
                if "timestamp" not in new_data.columns: new_data["timestamp"] = "-"
                
                # 저장 로직 (파일이 있으면 이어쓰기 'a', 없으면 새로쓰기 'w')
                if os.path.exists(DB_PATH):
                    new_data.to_csv(DB_PATH, mode='a', header=False, index=False, encoding='utf-8-sig')
                    st.toast("기존 DB에 대화 내용을 추가했습니다!", icon="✅")
                else:
                    new_data.to_csv(DB_PATH, mode='w', header=True, index=False, encoding='utf-8-sig')
                    st.toast("새로운 DB 파일을 생성했습니다!", icon="🎉")
                
                st.rerun() # 화면 갱신해서 바로 아래 표에 보여주기
            else:
                st.warning("저장할 대화 내용이 없습니다.")
    
    # 2. 조회 기능 (DB 읽어오기)
    with col_right:
        if os.path.exists(DB_PATH):
            # CSV 읽어오기
            try:
                history_df = pd.read_csv(DB_PATH)
                
                # 데이터가 있다면 보여주기
                if not history_df.empty:
                    st.write(f"📊 **총 누적 상담 건수:** {len(history_df)}건")
                    
                    # 보기 좋게 가공
                    display_df = history_df.rename(columns={"timestamp": "일시", "role": "구분", "content": "내용"})
                    display_df["구분"] = display_df["구분"].replace({"user": "👤 사용자", "assistant": "🤖 AI"})
                    
                    # 최신순 정렬 (선택사항)
                    # display_df = display_df.sort_index(ascending=False)
                    
                    st.dataframe(display_df, use_container_width=True, height=500)
                    
                    # (보너스) DB 파일 통째로 다운로드
                    with open(DB_PATH, "rb") as f:
                        st.download_button(
                            label="📥 전체 DB 백업 다운로드 (.csv)",
                            data=f,
                            file_name="full_chat_history_db.csv",
                            mime="text/csv"
                        )
                else:
                    st.info("DB 파일은 있지만 데이터가 비어있습니다.")
            except Exception as e:
                st.error(f"DB 읽기 오류: {e}")
        else:
            st.info("아직 저장된 상담 내역(DB)이 없습니다. 왼쪽의 '저장하기' 버튼을 눌러보세요!")