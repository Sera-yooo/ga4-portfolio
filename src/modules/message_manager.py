import yaml
import os

class MessageTemplateManager:
    def __init__(self, template_file="mail_templates.yaml"):
        """
        메시지 템플릿을 관리하는 클래스
        :param template_file: 사용할 YAML 파일명 (templates 폴더 내 위치)
        """
        base_path = os.path.dirname(os.path.abspath(__file__))
        # 현재 위치가 src/modules이므로 상위로 이동 후 templates 폴더 참조
        self.template_path = os.path.join(base_path, "..", "templates", template_file)
        self.templates = self._load_templates()

    def _load_templates(self):
        """YAML 파일을 안전하게 로드"""
        if not os.path.exists(self.template_path):
            print(f"⚠️ 경고: 템플릿 파일을 찾을 수 없습니다. ({self.template_path})")
            return {}
        
        try:
            with open(self.template_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"❌ 오류: YAML 로드 실패 - {e}")
            return {}

    def get_rendered_message(self, template_key, **kwargs):
        """
        템플릿 키를 기반으로 본문을 렌더링
        사용법: mm.get_rendered_message("trial_notice", sch="북원초", tea="김은영")
        """
        template = self.templates.get(template_key)
        if not template:
            return "제목 없음", "지정된 템플릿 키를 찾을 수 없습니다."

        subject = template.get('subject', '')
        body = template.get('body', '')

        # {{변수명}} 형태의 문자열을 전달받은 인자값으로 치환
        for key, value in kwargs.items():
            placeholder = f"{{{{{key}}}}}"
            subject = subject.replace(placeholder, str(value))
            body = body.replace(placeholder, str(value))

        return subject, body

    def refresh(self):
        """서버 재시작 없이 YAML 파일 내용을 새로고침"""
        self.templates = self._load_templates()
        return "✅ 템플릿 새로고침 완료"