from app.models.demand import DemandForm
from app.templates.recruitment_template import build_recruitment_content_html


class ContentService:
    """Build stable recruitment article content without calling an LLM."""

    def generate_recruitment_content(self, form: DemandForm) -> dict:
        data = {
            "title": self._build_title(form),
            "digest": self._build_digest(form),
            "player_requirement_summary": form.player_requirement_desc,
            "activity_content_summary": form.activity_description,
        }
        data["content_html"] = build_recruitment_content_html(form, data)
        return data

    def _build_title(self, form: DemandForm) -> str:
        return f"{form.city}|{form.game_category}玩家招募|礼金{form.reward_amount}~"

    def _build_digest(self, form: DemandForm) -> str:
        return f"{form.city}{form.game_category}玩家招募，活动礼金{form.reward_amount}，欢迎符合条件的玩家报名。"


content_service = ContentService()
