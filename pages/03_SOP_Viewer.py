import streamlit as st
import base64
import os

# 1. 페이지 설정
st.set_page_config(page_title="운영 SOP 통합 관리", layout="wide")

# 2. PDF 표시 함수
def display_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

# 3. 자동으로 파일 목록 읽어오기
SOP_DIR = "src/assets/SOP"

def get_sop_files():
    # 폴더가 없으면 빈 리스트 반환
    if not os.path.exists(SOP_DIR):
        return []
    # .pdf 파일만 필터링해서 가져오기
    files = [f for f in os.listdir(SOP_DIR) if f.endswith(".pdf")]
    return sorted(files) # 이름순 정렬

all_files = get_sop_files()

# 4. 카테고리 분류 (파일명에 포함된 [키워드] 기준)
# 예: [독서화랑 클래스]가 포함된 파일들만 필터링
categories = ["🏛️ [B2G] 독서화랑 클래스", "🏠 [B2C] 독서화랑", "📢 마케팅 및 기타"]

with st.sidebar:
    st.header("📂 문서 필터")
    selected_category = st.selectbox("영역 선택", categories)
    
    # 선택된 카테고리에 맞는 파일만 필터링 (파일명의 앞부분으로 구분)
    category_keyword = selected_category.split("]")[0].split("[")[-1] # "독서화랑 클래스" 추출
    filtered_files = [f for f in all_files if category_keyword in f]

    if filtered_files:
        # 파일명에서 버전이나 날짜를 제외하고 깔끔한 이름만 보여주고 싶다면 
        # 리스트에 보여줄 때는 정제해서 보여줄 수 있습니다.
        selected_file_name = st.radio("문서 선택", filtered_files)
        full_path = os.path.join(SOP_DIR, selected_file_name)
    else:
        st.warning("해당 카테고리에 등록된 PDF가 없습니다.")
        full_path = None

# 5. 메인 화면 출력
if full_path:
    st.subheader(f"📄 {selected_file_name}")
    display_pdf(full_path)
else:
    st.info("왼쪽 사이드바에서 열람할 문서를 선택해 주세요.")