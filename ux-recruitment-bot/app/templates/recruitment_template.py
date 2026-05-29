from html import escape

from app.models.demand import DemandForm

# ── 固定 HTML 片段（直接嵌入，不依赖 LLM 格式化）────────────────
_FIXED_NOTES_HTML = """\
<ol>
  <li>游戏企业工作/市场研究行业/媒体/自媒体行业不可参与，敬请谅解~</li>
  <li>若存在个人信息及游戏经历作假情况、诱导他人参与活动、活动后无故缺席者，\
访谈过程中态度恶劣不配合，则会被永久拉黑且不支付礼金；游戏内容/访谈活动若涉及保密内容，\
请各位入选后谨守保密约定，泄露者将依法追究法律责任。</li>
  <li>游戏公司支付玩家礼金有义务对礼金进行税务代扣。</li>
</ol>"""

_FIXED_PROGRESS_HTML = """\
<ol>
  <li>等待通知：提交报名信息后，可能会收到工作人员电话询问游戏经历，\
活动入选以「联到访客发确认」为准；活动开始前若未收到拨电或好友申请，则默认未入选；\
按要求完成活动后，礼金通常会在 5-10 个工作日内转到绑定收款账户内。</li>
  <li>自助查询：后台回复报名活动的相应编号，即可查询项目进度。</li>
</ol>"""

_FIXED_COMMUNITY_HTML = (
    "<p>这个活动与您的游戏经历不匹配？没关系，"
    "我们还有更多有趣的活动信息在社群，欢迎扫码加入！！！"
    "（若二维码失效，可后台留言小编哦~）</p>"
    "<p>[社群二维码图片]</p>"
)

_FIXED_COPYRIGHT_HTML = (
    "<p>若有转载或商务合作需求，请与后台联系工作人员，"
    "切勿直接转载或者擅自改动。</p>"
)
# ─────────────────────────────────────────────────────────────────


def build_recruitment_prompt(form: DemandForm) -> str:
    """
    构建游戏玩家用研招募推文生成 Prompt。
    LLM 只负责生成短文本，完整 HTML 由后端模板拼装，避免长 JSON 输出损坏。
    """
    extra = f"\n- 补充说明：{form.extra_notes}" if form.extra_notes else ""

    return f"""你是一位游戏用研团队的运营，负责撰写微信公众号游戏玩家招募推文。

请根据以下需求单，生成用于微信公众号招募推文的短文本，并严格按照最后指定的 JSON 格式输出。

【需求单信息】
- 城市：{form.city}
- 游戏品类关键词：{form.game_category}
- 礼金：{form.reward_amount}
- 玩家要求：{form.player_requirement_desc}
- 游戏举例：{form.game_examples}
- 活动时间：{form.activity_date}
- 测试时长：{form.duration}
- 活动地点：{form.location}
- 活动内容：{form.activity_description}
- 项目编号：{form.project_id}{extra}

【写作要求】
- title 控制在 30 字以内
- digest 控制在 50 字以内
- player_requirement_summary 用 1-2 句话概括玩家要求，不要编造需求单以外的硬性条件
- activity_content_summary 用 1 句话描述活动内容，语气自然
- 不要输出 HTML
- 不要输出 Markdown 代码块

【输出格式】严格返回以下 JSON，不输出任何其他内容：
{{
  "title": "{form.city}|{form.game_category}玩家招募|礼金{form.reward_amount}~",
  "digest": "50字以内摘要，用于公众号文章列表展示",
  "player_requirement_summary": "玩家要求短文本",
  "activity_content_summary": "活动内容短文本"
}}"""


def build_recruitment_content_html(form: DemandForm, generated: dict) -> str:
    """根据需求单和 LLM 生成的短文本，稳定拼装公众号正文 HTML。"""
    player_requirement = _html_requirement_text(
        generated.get("player_requirement_summary") or form.player_requirement_desc
    )
    activity_content = _html_text(
        generated.get("activity_content_summary") or form.activity_description
    )
    game_examples = _html_text(form.game_examples)
    progress_block = (
        f"{_FIXED_PROGRESS_HTML}\n"
        f"<p>项目编号：{_html_text(form.project_id)}</p>\n"
        "<p>（注意：查询方式信息较为滞后，仅供参考项目整体进度，"
        "如该招募活动是否已结束）</p>"
    )

    return f"""<h1>{_html_text(form.city)}招募游戏玩家</h1>
<p>{_html_text(form.activity_date)}，{_html_text(form.city)}</p>

<h2>玩家要求</h2>
<p>{player_requirement}</p>
<p>如：{game_examples}</p>

<h2>活动详情</h2>
<p><strong>【活动时间】</strong>{_html_text(form.activity_date)}</p>
<p><strong>【测试时长】</strong>{_html_text(form.duration)}</p>
<p><strong>【活动地点】</strong>{_html_text(form.location)}</p>

<h2>活动内容</h2>
<p>{activity_content}</p>

<h2>活动礼金</h2>
<p><strong>【活动报酬】</strong>礼金 {_html_text(form.reward_amount)}</p>

<h2>报名链接</h2>
<p>欢迎玩家们扫码报名～（报名后无礼金）</p>
<p>[报名二维码图片]</p>

<h2>活动进度查询</h2>
{progress_block}

<h2>注意事项</h2>
{_FIXED_NOTES_HTML}

<h2>玩家社群</h2>
{_FIXED_COMMUNITY_HTML}

<h2>严禁随意转载</h2>
{_FIXED_COPYRIGHT_HTML}"""


def _html_text(value: str) -> str:
    return escape(value or "").replace("\n", "<br>")


def _html_requirement_text(value: str) -> str:
    lines = [line.strip() for line in (value or "").splitlines() if line.strip()]
    if not lines:
        return ""
    formatted = []
    for line in lines:
        separator = "：" if "：" in line else ":" if ":" in line else ""
        if separator:
            label, detail = line.split(separator, 1)
            formatted.append(
                f'<strong style="color:#2E7D32;">{escape(label)}：</strong>{escape(detail).replace("\n", "<br>")}'
            )
        else:
            formatted.append(_html_text(line))
    return "<br>".join(formatted)
