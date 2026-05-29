# =====================================================================
#  엔진: YAML 본문에 값을 끼워넣고(치환), 빠진 값을 잡아낸다(검증).
#  - 보통 이 파일은 손댈 일이 거의 없습니다.
# =====================================================================
import os
import re
import yaml

# mail_templates.yaml 위치 (이 파일 기준 ../templates/mail_templates.yaml)
_YAML_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "templates", "mail_templates.yaml"
)

_PLACEHOLDER = re.compile(r"\{\{\s*(\w+)\s*\}\}")


def load_templates(path=None):
    """mail_templates.yaml 을 읽어 dict 로 반환."""
    path = path or _YAML_PATH
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def find_placeholders(text):
    """문자열 안의 {{변수}} 이름들을 set 으로 반환."""
    return set(_PLACEHOLDER.findall(text or ""))


def fill(text, ctx):
    """{{변수}} 를 ctx 값으로 치환. 값이 비어 있으면 ⚠️[누락:변수] 로 표시."""
    if not text:
        return ""

    def repl(m):
        key = m.group(1)
        val = ctx.get(key)
        if val is None or str(val).strip() == "":
            return f"⚠️[누락:{key}]"
        return str(val)

    return _PLACEHOLDER.sub(repl, text)


def build(case, ctx, templates=None):
    """케이스(catalog 항목) + 입력값(ctx) -> 완성된 메시지.

    반환: {
        "subject":     제목(치환 완료),
        "body":        본문(치환 완료),
        "attachments": 첨부 체크리스트(치환 완료),
        "missing":     아직 비어 있는 변수 이름 목록,
    }
    """
    templates = templates if templates is not None else load_templates()

    key = case["template"]
    if key not in templates:
        # 이 메시지를 보면: catalog 의 template 값과 YAML 최상단 키가 다른 것.
        raise KeyError(
            "지정된 템플릿 키를 찾을 수 없습니다: '%s'. "
            "mail_templates.yaml 에 있는 키: %s" % (key, list(templates.keys()))
        )

    tpl = templates[key]
    subject = fill(tpl.get("subject", ""), ctx)
    body = fill(tpl.get("body", ""), ctx)
    attachments = [fill(a, ctx) for a in case.get("attachments", [])]

    # 제목 + 본문에 등장하는 모든 변수 중, 값이 빈 것 = 누락
    needed = find_placeholders(tpl.get("subject", "")) | find_placeholders(tpl.get("body", ""))
    missing = sorted(k for k in needed if not str(ctx.get(k, "")).strip())

    return {
        "subject": subject,
        "body": body,
        "attachments": attachments,
        "missing": missing,
    }
