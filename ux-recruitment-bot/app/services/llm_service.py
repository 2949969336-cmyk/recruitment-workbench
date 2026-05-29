import json
import logging
import re
from openai import AsyncOpenAI
from app.config import settings
from app.models.demand import DemandForm
from app.templates.recruitment_template import (
    build_recruitment_content_html,
    build_recruitment_prompt,
)

logger = logging.getLogger(__name__)


class LLMService:
    """封装对硅基流动（OpenAI 兼容）的调用"""

    def __init__(self) -> None:
        self._client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
        )

    async def generate_recruitment_content(self, form: DemandForm) -> dict:
        """
        根据需求单生成微信推文内容。

        Returns:
            {
                "title": "文章标题",
                "digest": "文章摘要（<50字）",
                "content_html": "正文 HTML"
            }
        """
        prompt = build_recruitment_prompt(form)
        logger.info(f"调用 LLM 模型：{settings.model_name}")

        response = await self._client.chat.completions.create(
            model=settings.model_name,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "你是一名游戏用研团队的运营，专门撰写微信公众号游戏玩家招募推文。"
                        "请严格按照用户要求的 JSON 格式返回，不要输出任何额外内容。"
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,   # 降低随机性，保证结构稳定
            max_tokens=1200,
            response_format={"type": "json_object"},
        )

        raw_text = response.choices[0].message.content.strip()
        logger.info("LLM 响应已接收，开始解析...")
        return self._parse_response(raw_text, form)

    # ──────────────────────────────────────────
    # 私有方法
    # ──────────────────────────────────────────

    def _parse_response(self, raw_text: str, form: DemandForm) -> dict:
        """解析 LLM 返回的 JSON，带容错处理"""
        # 移除可能的 markdown 代码块包裹
        if "```json" in raw_text:
            raw_text = raw_text.split("```json")[1].split("```")[0].strip()
        elif "```" in raw_text:
            raw_text = raw_text.split("```")[1].split("```")[0].strip()
        elif "{" in raw_text and "}" in raw_text:
            raw_text = raw_text[raw_text.find("{") : raw_text.rfind("}") + 1]

        try:
            data = json.loads(raw_text)
        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析失败: {e}\n原始内容片段: {raw_text[:300]}")
            data = self._build_fallback_response(form, raw_text)

        # 校验必要字段
        if "activity_content_summary" not in data and "content_summary" in data:
            data["activity_content_summary"] = data["content_summary"]

        data["title"] = self._build_title(form)
        data["digest"] = self._build_digest(form)
        data["player_requirement_summary"] = form.player_requirement_desc
        data["activity_content_summary"] = form.activity_description

        data["content_html"] = build_recruitment_content_html(form, data)

        logger.info(f"✅ 内容生成成功，标题：{data['title']}")
        return data

    def _build_fallback_response(self, form: DemandForm, raw_text: str) -> dict:
        """LLM JSON 损坏时，从原文尽量捞字段，捞不到就用需求单兜底。"""
        logger.warning("启用 LLM 兜底解析，使用需求单生成稳定预览内容")

        def pick_value(key: str) -> str | None:
            match = re.search(rf'"{key}"\s*:\s*"([^"]*)"', raw_text)
            if match:
                value = match.group(1).strip()
                return value or None
            return None

        return {
            "title": self._build_title(form),
            "digest": self._build_digest(form),
            "player_requirement_summary": pick_value("player_requirement_summary")
            or form.player_requirement_desc,
            "activity_content_summary": pick_value("activity_content_summary")
            or pick_value("content_summary")
            or form.activity_description,
        }

    def _build_title(self, form: DemandForm) -> str:
        return f"{form.city}|{form.game_category}玩家招募|礼金{form.reward_amount}~"

    def _build_digest(self, form: DemandForm) -> str:
        return f"{form.city}{form.game_category}玩家招募，活动礼金{form.reward_amount}，欢迎符合条件的玩家报名。"



# 单例实例
llm_service = LLMService()
