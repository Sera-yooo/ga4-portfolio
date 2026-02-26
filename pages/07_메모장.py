import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="CS 논리 분석", page_icon="🧠", layout="wide")

st.title("🧠 CS 논리/원인 분석실 (RCA)")
st.caption("현상(Data) 뒤에 숨겨진 원인(Logic)을 파헤쳐서 기록하는 공간입니다.")

# -------------------------------------------------------------------
# [1] 분석 기록하기 (Input)
# -------------------------------------------------------------------
with st.expander("📝 새로운 분석 기록하기", expanded=True):
    with st.form("logic_note_form"):
        col1, col2 = st.columns([1, 2])
        
        with col1:
            date_now = datetime.now().strftime("%Y-%m-%d")
            topic = st.text_input("분석 주제", placeholder="예: 탐험도서관 완독 문의 폭증 원인")
            category = st.selectbox("관련 영역", ["회원/로그인", "컨텐츠/학습", "결제/시스템", "UX/UI", "기타"])
            
        with col2:
            # 팀장님이 작성하신 1~5번 내용을 여기에 적는 겁니다.
            logic_content = st.text_area("논리적 분석 내용 (5 Whys / 현상분석)", height=200,
                                       placeholder="1. 현상: 완독했는데 안 된다고 함\n2. 원인: 시각적 피드백(도장)이 없음\n3. 문제: 하단에 작은 마크로만 확인 가능\n4. ...")
            
        # 결론 및 요청사항
        conclusion = st.text_input("💡 결론 및 실행 과제 (Action Item)", 
                                   placeholder="예: 상세페이지에 '완독 성공' 도장 이미지 크게 노출 필요")
        
        submit_btn = st.form_submit_button("💾 분석 노트 저장")

# -------------------------------------------------------------------
# [2] 저장 로직 (구글 시트 'CS_논리노트' 탭에 저장)
# -------------------------------------------------------------------
if submit_btn:
    if not topic or not logic_content:
        st.warning("주제와 분석 내용은 필수입니다!")
    else:
        try:
            scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
            creds = ServiceAccountCredentials.from_json_keyfile_name('service-account.json', scope)
            client = gspread.authorize(creds)
            
            sh = client.open_by_url("https://docs.google.com/spreadsheets/d/1MQVn2jcKiHagQqUyyHR3ew9BLhD520Cv3UTwVMo5_6g/edit?usp=sharing")
            
            # 'CS_논리노트' 시트가 없으면 생성
            try:
                worksheet = sh.worksheet("CS_논리노트")
            except:
                worksheet = sh.add_worksheet(title="CS_논리노트", rows="100", cols="5")
                worksheet.append_row(["작성일", "주제", "카테고리", "논리분석내용", "결론(Action)"])
            
            # 데이터 저장
            worksheet.append_row([date_now, topic, category, logic_content, conclusion])
            st.success("✅ 논리적인 분석이 자산으로 저장되었습니다!")
            st.rerun() # 저장 후 바로 아래 리스트에 뜨게 새로고침
            
        except Exception as e:
            st.error(f"저장 실패: {e}")

# -------------------------------------------------------------------
# [3] 저장된 분석 모아보기 (Viewer) - 여기가 핵심!
# -------------------------------------------------------------------
st.divider()
st.subheader("📚 우리의 분석 히스토리")

try:
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('service-account.json', scope)
    client = gspread.authorize(creds)
    sh = client.open_by_url("https://docs.google.com/spreadsheets/d/1MQVn2jcKiHagQqUyyHR3ew9BLhD520Cv3UTwVMo5_6g/edit?usp=sharing")
    worksheet = sh.worksheet("CS_논리노트")
    
    data = worksheet.get_all_records()
    df_logic = pd.DataFrame(data)
    
    if not df_logic.empty:
        # 최신순 정렬
        df_logic = df_logic.sort_index(ascending=False)
        
        for index, row in df_logic.iterrows():
            with st.chat_message("assistant"): # 아이콘을 로봇이나 뇌 모양으로 하면 간지남
                st.markdown(f"**[{row['작성일']}] {row['주제']}** <span style='background-color:#f0f2f6; padding:2px 6px; border-radius:4px; font-size:0.8em'>{row['카테고리']}</span>", unsafe_allow_html=True)
                
                # 분석 내용은 박스 안에 예쁘게
                st.info(row['논리분석내용'].replace("\n", "  \n")) 
                
                # 결론은 강조
                st.markdown(f"👉 **결론:** :red[{row['결론(Action)']}]")
    else:
        st.info("아직 저장된 분석 노트가 없습니다. 첫 분석을 기록해보세요!")

except:
    st.write("데이터를 불러오는 중이거나 시트가 아직 없습니다.")