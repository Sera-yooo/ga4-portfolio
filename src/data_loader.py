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
                s_code = row[18].strip() if len(row) > 18 else "" # S열
                
                data_list.append({
                    "순번": row[0].strip() if len(row) > 0 else "",      # A
                    "지역명": row[1] if len(row) > 1 else "",           # B
                    "상세지역명": row[2] if len(row) > 2 else "",         # C
                    "학교명": row[3].strip(),                            # D
                    "교사명": row[4].strip() if len(row) > 4 else "",      # E
                    "연락처": row[5].strip() if len(row) > 5 else "",      # F
                    "교사메일": row[6].strip() if len(row) > 6 else "",    # G
                    "유입경로": row[7].strip() if len(row) > 7 else "",    # H
                    
                    # --- 상담 및 상태 정보 ---
                    "1차상담": row[11].strip() if len(row) > 11 else "",   # L
                    "2차상담": row[12].strip() if len(row) > 12 else "",   # M
                    "3차상담": row[13].strip() if len(row) > 13 else "",   # N
                    "진행상태": row[14].strip() if len(row) > 14 else "부", # O
                    "진행여부": row[17].strip() if len(row) > 17 else "",   # R
                    
                    # --- 계정 및 날짜 정보 ---
                    "학교코드": s_code,                                    # S
                    "체험교사계정": row[19].strip() if len(row) > 19 else "", # T
                    "시작일": row[20] if len(row) > 20 else "",            # U
                    "종료일": row[21] if len(row) > 21 else "",            # V
                    "출력여부": row[22] if len(row) > 22 else "부",         # W
                    "계약여부": row[25] if len(row) > 25 else "부",         # Z
                    
                    # --- 부가 정보 (필요시) ---
                    "학생1_ID": f"{s_code}-0001" if s_code else "",
                    "학생2_ID": f"{s_code}-0002" if s_code else ""
                })
        return pd.DataFrame(data_list)
    except Exception as e:
        st.error(f"데이터 로드 실패: {e}")
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
        worksheet.append_row(data_list)
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