import pandas as pd
import gspread
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials

# 공통 시트 URL (체험 학교 관리 시트)
TRIAL_SHEET_URL = "https://docs.google.com/spreadsheets/d/1nmAhwBLloq6pFGFIWYahKh4vPQaw08xugCWHURJ076c/"

@st.cache_data(ttl=60)
def load_school_trial_data():
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)

        sh = client.open_by_url(TRIAL_SHEET_URL)
        worksheet = sh.get_worksheet_by_id(414849783) 
        all_values = worksheet.get_all_values()
        raw_rows = all_values[9:] 
        
        data_list = []
        for row in raw_rows:
            if len(row) > 3 and row[3].strip():
                # 안전한 인덱스 접근을 위해 변수화
                s_code = row[18].strip() if len(row) > 18 else "" # S열
                
                data_list.append({
                    "순번": row[0].strip(),             # A (조회 키)
                    "지역명": row[1],                   # B
                    "상세지역명": row[2],                # C
                    "학교명": row[3],                   # D
                    "교사명": row[4],                   # E
                    "교사메일": row[6].strip() if len(row) > 6 else "", # G (수신용)
                    "학교코드": s_code,                 # S
                    "체험교사계정": row[19].strip() if len(row) > 19 else "", # T (접속용)
                    "시작일": row[20] if len(row) > 20 else "", 
                    "종료일": row[21] if len(row) > 21 else "",
                    "계약여부": row[25] if len(row) > 25 else "",
                    # 학생 계정 자동 생성 규칙 적용
                    "학생1_ID": f"{s_code}-0001" if s_code else "",
                    "학생2_ID": f"{s_code}-0002" if s_code else ""
                })
        return pd.DataFrame(data_list)
    except Exception as e:
        st.error(f"데이터 로드 실패: {e}")
        return pd.DataFrame()
    
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