# =====================================================================
#  시트 열 이름 → 표준 변수 매핑
#
#  지금은 화면에서 직접 입력하므로 이 파일을 쓰지 않아도 됩니다.
#  나중에 구글시트/엑셀 자동완성을 붙일 때만 아래를 채우세요.
#
#  방법:
#   1) COLUMN_MAP 에  "시트의 열 이름": "표준 변수명"  을 채운다.
#      (표준 변수명은 catalog.py 의 field name 과 동일: sch, tea, s_str ...)
#   2) 순번 검색으로 찾은 시트 한 줄(row)을 row_to_context(row) 에 넘기면
#      입력칸을 채울 dict 가 나온다.
# =====================================================================

COLUMN_MAP = {
    # "학교명":     "sch",
    # "교사명":     "tea",
    # "시작일":     "s_str",
    # "종료일":     "e_str",
    # "관리자계정": "adm_id",
    # "명단인원":   "n_total",
    # "학생수":     "n_student",
    # "교사수":     "n_teacher",
}


def row_to_context(row):
    """시트 한 줄(pandas Series 또는 dict) -> 표준 변수 dict.

    COLUMN_MAP 이 비어 있으면 빈 dict 를 반환합니다(=직접 입력 모드).
    """
    ctx = {}
    for col, var in COLUMN_MAP.items():
        try:
            present = col in row
        except TypeError:
            present = hasattr(row, "index") and col in row.index
        if present:
            val = row[col]
            ctx[var] = "" if val is None else str(val).strip()
    return ctx
