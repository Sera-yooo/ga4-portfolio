# =====================================================================
#  케이스 카탈로그
#  - "어떤 케이스가 있고, 각 케이스는 무슨 입력칸/첨부가 필요한가"의 단일 원천.
#  - 케이스를 늘리려면: 여기에 한 블록 추가 + mail_templates.yaml 에 같은 키 추가.
#
#  각 케이스 항목 설명
#    label       : 화면 드롭다운에 보일 이름
#    group       : 분류(체험 / 계약)
#    channel     : 메일 / 문자
#    template    : mail_templates.yaml 의 최상단 키 (★글자까지 일치★)
#    fields      : 화면에 띄울 입력칸 목록
#                   - name   : {{변수}} 이름
#                   - label  : 입력칸에 보일 이름
#                   - kind   : "text" 또는 "date"
#                   - default: (선택) 기본값
#                   - offset_days: (date 전용, 선택) 오늘+N일을 기본값으로
#    attachments : 이 케이스에서 직접 첨부해야 할 파일 체크리스트
#                   {{sch}} 같은 변수 사용 가능 → 학교명에서 자동 완성
# =====================================================================

CASES = {

    # ---------------- 체험 ----------------
    "trial_mail": {
        "label": "체험 · 메일",
        "group": "체험",
        "channel": "메일",
        "template": "trial_mail",
        "fields": [
            {"name": "sch",   "label": "학교명",      "kind": "text"},
            {"name": "tea",   "label": "선생님 성함", "kind": "text"},
            {"name": "s_str", "label": "체험 시작일", "kind": "date"},
            {"name": "e_str", "label": "체험 종료일", "kind": "date", "offset_days": 31},
        ],
        "attachments": ["서비스 소개서", "사용자별 퀵 가이드"],
    },

    "trial_sms": {
        "label": "체험 · 문자",
        "group": "체험",
        "channel": "문자",
        "template": "trial_sms",
        "fields": [
            {"name": "sch",   "label": "학교명",      "kind": "text"},
            {"name": "tea",   "label": "선생님 성함", "kind": "text"},
            {"name": "s_str", "label": "체험 시작일", "kind": "date"},
            {"name": "e_str", "label": "체험 종료일", "kind": "date", "offset_days": 31},
        ],
        "attachments": [],  # 문자는 첨부 없이, 메일 주소 회신 요청
    },

    # ---------------- 계약 ----------------
    "contract_setup_done": {
        "label": "계약 ① 명단 받음 → 세팅 완료",
        "group": "계약",
        "channel": "메일",
        "template": "contract_setup_done",
        "fields": [
            {"name": "sch",       "label": "학교명",      "kind": "text"},
            {"name": "tea",       "label": "선생님 성함", "kind": "text"},
            {"name": "n_student", "label": "학생 수",     "kind": "text"},
            {"name": "n_teacher", "label": "교사 수",     "kind": "text"},
        ],
        "attachments": [
            "{{sch}}_계정정보_학생·교사명단_안내.xlsx",
            "사용자별 퀵 가이드",
        ],
    },

    "contract_admin": {
        "label": "계약 ② 관리자만 있음 → 정규 개시",
        "group": "계약",
        "channel": "메일",
        "template": "contract_admin",
        "fields": [
            {"name": "sch",     "label": "학교명",          "kind": "text"},
            {"name": "tea",     "label": "선생님 성함",     "kind": "text"},
            {"name": "s_str",   "label": "이용 시작일",     "kind": "date"},
            {"name": "e_str",   "label": "이용 종료일",     "kind": "date", "offset_days": 214},
            {"name": "adm_id",  "label": "관리자 계정(ID)", "kind": "text"},
            {"name": "adm_pw",  "label": "초기 비밀번호",   "kind": "text", "default": "0000"},
            {"name": "n_total", "label": "명단 인원(전체)", "kind": "text"},
        ],
        "attachments": [
            "{{sch}}_계정정보_학생·교사명단_안내.xlsx",
            "사용자별 퀵 가이드(관리/일반/학생)",
        ],
    },

    "contract_request": {
        "label": "계약 ③ 명단 없음 → 명단 요청",
        "group": "계약",
        "channel": "메일",
        "template": "contract_request",
        "fields": [
            {"name": "sch",   "label": "학교명",      "kind": "text"},
            {"name": "tea",   "label": "선생님 성함", "kind": "text"},
            {"name": "s_str", "label": "이용 시작일", "kind": "date"},
            {"name": "e_str", "label": "이용 종료일", "kind": "date", "offset_days": 214},
        ],
        "attachments": [
            "명단 작성 양식 (엑셀)",
        ],
    },
}
