import pandas as pd
import gspread
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials

# 공통 시트 URL (체험 학교 관리 시트)
TRIAL_SHEET_URL = "https://docs.google.com/spreadsheets/d/1nmAhwBLloq6pFGFIWYahKh4vPQaw08xugCWHURJ076c/"

@st.cache_data(ttl=60)
def load_school_trial_data():
    # 체험학교 조회 시트
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)

        sh = client.open_by_url(TRIAL_SHEET_URL)
        worksheet = sh.get_worksheet_by_id(414849783) 
        all_values = worksheet.get_all_values()
        raw_rows = all_values[9:] # 10행부터 데이터 시작
        
        data_list = []
        for row in raw_rows:
            # D열(학교명)이 비어있지 않은 경우만 처리
            if len(row) > 3 and row[3].strip():
                # 안전한 인덱스 접근을 위해 학교코드(S열) 미리 추출 
                s_code = row[19].strip() if len(row) > 18 else "" # S열
                
                data_list.append({
                    "순번": row[0].strip() if len(row) > 0 else "",      # A
                    "지역명": row[1] if len(row) > 1 else "",           # B
                    "상세지역명": row[2] if len(row) > 2 else "",         # C
                    "학교명": row[3].strip(),                            # D
                    "학교연락처": row[4].strip() if len(row) > 5 else "",      # E
                    "교사명": row[5].strip() if len(row) > 4 else "",      # F                    
                    "연락처": row[6].strip() if len(row) > 5 else "",      # G
                    "교사메일": row[7].strip() if len(row) > 6 else "",    # H
                    "유입경로": row[8].strip() if len(row) > 7 else "",    # I
                    
                    # --- 상담 및 상태 정보 ---
                    "상담내용": row[12].strip() if len(row) > 12 else "",       # M열 (13번째 -> index 12)
                    "마지막상담일자": row[13].strip() if len(row) > 13 else "",   # N열 (14번째 -> index 13)
                    "상담상태": row[14].strip() if len(row) > 14 else "",       # O열 (15번째 -> index 14)
                    "진행여부": row[15].strip() if len(row) > 15 else "부",     # P열 (16번째 -> index 15)
                    "진행상태": row[17].strip() if len(row) > 17 else "부",     # R열 (18번째 -> index 17)
                    
                    # --- 계정 및 날짜 정보 ---
                    "학교코드": s_code,                                    # T
                    "체험교사계정": row[20].strip() if len(row) > 20 else "", # U
                    "시작일": row[21] if len(row) > 21 else "",            # V
                    "종료일": row[22] if len(row) > 22 else "",            # W
                    "출력여부": row[23] if len(row) > 23 else "부",         # Z
                    "계약여부": row[26] if len(row) > 26 else "부",         # AA
                    
                    # --- 부가 정보 (필요시) ---
                    "학생1_ID": f"{s_code}-0001" if s_code else "",
                    "학생2_ID": f"{s_code}-0002" if s_code else ""
                })
        return pd.DataFrame(data_list)
    except Exception as e:
        st.error(f"데이터 로드 실패: {e}")
        return pd.DataFrame()
    
def load_trial_consulting_logs():
    """
    체험학교상담로그 시트의 모든 데이터를 불러오는 함수
    컬럼: 체험인덱스, 학교명, 날짜, 상담유형, 상담내용, 담당자
    """
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)

        sh = client.open_by_url(TRIAL_SHEET_URL)
        # '체험학교상담로그' 시트 이름으로 워크시트 가져오기
        worksheet = sh.worksheet("체험학교상담로그") 
        
        all_values = worksheet.get_all_values()
        
        # 첫 줄이 컬럼명인 경우 [1:] 부터, 데이터만 있는 경우 [0:] 부터 사용
        # 보통 1행은 헤더이므로 [1:]을 권장합니다.
        raw_rows = all_values[1:] 
        
        log_data_list = []
        for row in raw_rows:
            # 체험인덱스(A열)가 있는 경우만 처리
            if len(row) > 0 and row[0].strip():
                log_data_list.append({
                    "체험인덱스": row[0].strip(), # A
                    "학교명": row[1].strip() if len(row) > 1 else "",   # B
                    "날짜": row[2].strip() if len(row) > 2 else "",     # C
                    "상담유형": row[3].strip() if len(row) > 3 else "",   # D
                    "상담내용": row[4].strip() if len(row) > 4 else "",   # E
                    "담당자": row[5].strip() if len(row) > 5 else ""      # F
                })
        
        df = pd.DataFrame(log_data_list)
        
        # 날짜 컬럼이 있을 경우 정렬을 위해 날짜형식 변환 (선택 사항)
        if not df.empty and "날짜" in df.columns:
            df["날짜"] = pd.to_datetime(df["날짜"], errors='coerce')
            # 최신순 정렬 (스프레드시트의 INDEX/SORT 함수와 동일한 로직을 위함)
            df = df.sort_values(by="날짜", ascending=False)
            
        return df

    except Exception as e:
        st.error(f"상담 로그 로드 실패: {e}")
        return pd.DataFrame()


def append_new_school_data(data_list):
    # 체험학교 입력 시트

    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        
        sh = client.open_by_url(TRIAL_SHEET_URL)
        worksheet = sh.get_worksheet_by_id(414849783)
        
        # 시트 맨 아래에 새로운 행 추가
        worksheet.append_row(data_list, value_input_option='USER_ENTERED')        
        return True
    except Exception as e:
        st.error(f"데이터 추가 실패: {e}")
        return False
 
    
   
# 총판 체험 계정 관리 시트 URL
CP_TRIAL_URL = "https://docs.google.com/spreadsheets/d/1ZL3p5WKL_c0h5DAbLoFgULx6_n3boF5M27nuKdMPrhM/"

@st.cache_data(ttl=60)
def load_cp_trial_data():
    try:
        # 1. 인증 및 시트 연결
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)

        # 2. 시트 열기 (GID: 0 은 첫 번째 시트를 의미)
        sh = client.open_by_url(CP_TRIAL_URL)
        worksheet = sh.get_worksheet(0) # 첫 번째 탭
        
        all_values = worksheet.get_all_values()
        
        # 3. 32행(인덱스 31)부터 데이터 시작
        raw_rows = all_values[31:] 
        
        data_list = []
        for row in raw_rows:
            # 엑셀의 '0000' 같은 패스워드 보존을 위해 모든 값을 문자열로 처리
            # 총판명(C열/index 2)이 비어있지 않은 경우만 가져옴
            if len(row) > 4 and row[2].strip():
                data_list.append({
                    "지역": str(row[1]).strip(),           # B
                    "총판명": str(row[2]).strip(),         # C
                    "총판담당자": str(row[3]).strip(),      # D
                    "학교명": str(row[4]).strip(),         # E
                    "관리교사계정": str(row[5]).strip(),    # F
                    "관리계정배부일": str(row[6]).strip(),   # G
                    "배포학교명": str(row[8]).strip(),      # I
                    "일반교사계정": str(row[9]).strip(),    # J
                    "일반계정배부일": str(row[10]).strip(),  # K
                    "체험종료일": str(row[12]).strip()      # M
                })
        
        return pd.DataFrame(data_list)
        
    except Exception as e:
        st.error(f"총판 데이터 로드 실패: {e}")
        return pd.DataFrame()
    
# 공통 시트 URL (계약 학교 관리 시트)
def load_contract_school_data():
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)

        sh = client.open_by_url(TRIAL_SHEET_URL)
        # 계약 학교 시트 ID로 변경
        worksheet = sh.get_worksheet_by_id(1104967938) 
        all_values = worksheet.get_all_values()
        
        # A10부터 시작하므로 index 9부터 가져옴
        raw_rows = all_values[9:] 
        
        data_list = []
        for row in raw_rows:
            # 학교명(D열, 인덱스 3)이 비어있지 않은 경우만 처리
            if len(row) > 3 and row[3].strip():
                data_list.append({
                    "순번": row[0].strip(),             # A
                    "지역명": row[1].strip(),           # B
                    "상세지역": row[2].strip(),         # C
                    "학교명": row[3].strip(),           # D
                    "학교고유번호": row[5].strip(),      # F (Index 5)
                    "학교사업자번호": row[6].strip(),      # G (Index 5)
                    "학교코드": row[7].strip(),         # H (Index 7)
                    "이전 체험 현황": row[8].strip(),         # I (Index 8)
		            "체험일": row[9].strip(),         # J (Index 9)
                    "계약교사명": row[10].strip(),       # K (Index 10)
                    "계약교사연락처": row[11].strip(),    # L (Index 11)
                    "계약교사이메일": row[12].strip(),    # M (Index 12)
                    "관리교사명": row[13].strip(),       # N (Index 13)
                    "관리교사연락처": row[14].strip(),    # O (Index 14)
                    "관리교사이메일": row[15].strip(),    # P (Index 15)
                    "계약회차": row[16].strip(),         # Q (Index 16)
                    "계약일": row[17].strip(),           # R (Index 17)
                    "계약학생수": row[18].strip(),       # S (Index 18)
                    "계약단위": row[19].strip(),       # T (Index 19)
                    "시작일": row[20].strip(),           # U (Index 20)
                    "종료일": row[21].strip(),           # V (Index 21)
                    "총금액(vat포함)": row[23].strip(),           # X (Index 23)
                })
        return pd.DataFrame(data_list)
    except Exception as e:
        st.error(f"계약 학교 데이터 로드 실패: {e}")
        return pd.DataFrame()
    
def load_distributor_monitoring_data():
    try:
        # 1. 인증 및 시트 연결
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)

        sheet_url = "https://docs.google.com/spreadsheets/d/1LoiiCRBT9XjAPhT-38RlVk3k8hJaz52Zc4TivtawhgQ/edit"
        sheet = client.open_by_url(sheet_url).worksheet("총판 계정 누적 접속 기록")
        
    # 2. 데이터 가져오기
        all_values = sheet.get_all_values()
        # 헤더(3행)는 무시하고 데이터(4행부터)만 가져옵니다.
        data = all_values[3:] 
        
        # 3. [해결책] 컬럼명을 우리가 직접 순서대로 정의합니다.
        # 시트의 A열부터 J열까지의 순서와 일치해야 합니다.
        fixed_columns = [
            "No", "지역", "총판명", "총판담당자", "학교명", 
            "교사구분", "관리교사계정", "계정배부일", "누적방문", "마지막로그인"
        ]
        
        # 데이터프레임 생성 (데이터 개수와 컬럼 개수 맞춤)
        # 만약 시트에 열이 더 많다면 슬라이싱으로 자릅니다.
        df = pd.DataFrame([row[:10] for row in data], columns=fixed_columns)

        # 4. 데이터 정제
        # 양끝 공백 제거
        df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

        # 병합 셀 처리 (ffill)
        fill_target = ["No", "지역", "총판명", "총판담당자", "학교명"]
        for col in fill_target:
            df[col] = df[col].replace('', None).ffill()

        # 계정이 없는 빈 줄 삭제
        df = df[df["관리교사계정"] != ""]
        
        return df

    except Exception as e:
        st.error(f"❌ 데이터 로드 중 오류 발생: {e}")
        return pd.DataFrame()

# 상담 상태 업데이트 (상담/체험학교 시트 O열)
def update_school_status(index, new_status):
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        
        sh = client.open_by_url(TRIAL_SHEET_URL)
        worksheet = sh.get_worksheet_by_id(414849783) # 아까 사용한 그 시트 ID
        
        # A열(순번)에서 인덱스 위치 찾기
        cell = worksheet.find(str(index))
        if cell:
            # O열(15번째 열) 업데이트
            worksheet.update_cell(cell.row, 15, new_status)
            return True
        return False
    except Exception as e:
        st.error(f"상태 업데이트 실패: {e}")
        return False
    
# 상담 로그 추가 (체험학교상담로그 시트)
def add_consulting_log(index, school_name, c_date, c_type, content, manager):
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        
        sh = client.open_by_url(TRIAL_SHEET_URL)
        worksheet = sh.worksheet("체험학교상담로그")
        
        # 전달받은 날짜 객체를 문자열로 변환
        date_str = c_date.strftime("%Y-%m-%d") if hasattr(c_date, 'strftime') else str(c_date)
        
        # 새 행 데이터
        new_row = [index, school_name, date_str, c_type, content, manager]
        
        # 🚀 [핵심 수정] value_input_option을 추가하여 사용자가 직접 입력하는 방식으로 설정
        # 이렇게 하면 ' 기호가 붙지 않고 숫자와 날짜로 정확히 입력됩니다.
        worksheet.append_row(new_row, value_input_option='USER_ENTERED')
        
        return True
    except Exception as e:
        st.error(f"로그 저장 실패: {e}")
        return False