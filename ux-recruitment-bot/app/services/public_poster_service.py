import base64
import html
import re
import time
from pathlib import Path

from app.models.demand import DemandForm


class PublicPosterService:
    """Render a desensitized public recruitment poster for external channels."""

    def __init__(self) -> None:
        app_dir = Path(__file__).resolve().parents[1]
        self.app_dir = app_dir
        self.output_dir = app_dir / "static" / "generated" / "public-posters"
        self.template_path = app_dir / "static" / "shuige-template.png"

    async def render_public_poster(
        self,
        form: DemandForm,
        poster_date: str | None = None,
        signup_qr: bytes | None = None,
        signup_qr_content_type: str | None = None,
        community_qr: bytes | None = None,
        community_qr_content_type: str | None = None,
    ) -> dict:
        try:
            from playwright.async_api import async_playwright
        except ImportError as exc:
            raise RuntimeError(
                "Playwright 未安装，无法自动渲染脱敏海报。请先运行：pip install playwright && playwright install chromium"
            ) from exc

        self.output_dir.mkdir(parents=True, exist_ok=True)
        output_name = f"public-poster-{self._safe_name(form.project_id)}-{int(time.time())}.png"
        output_path = self.output_dir / output_name
        page_html = self._build_html(
            form=form,
            poster_date=poster_date or form.activity_date,
            signup_qr=self._to_data_url(signup_qr, signup_qr_content_type),
            community_qr=self._to_data_url(community_qr, community_qr_content_type),
        )

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                context = await browser.new_context(
                    viewport={"width": 800, "height": 5200},
                    device_scale_factor=2,
                )
                page = await context.new_page()
                await page.set_content(page_html, wait_until="load")
                await page.locator(".poster").screenshot(path=str(output_path))
                await context.close()
                await browser.close()
        except Exception as exc:
            raise RuntimeError(f"脱敏公众号海报渲染失败：{exc}") from exc

        return {
            "path": str(output_path),
            "url": f"/static/generated/public-posters/{output_name}",
        }

    def _build_html(
        self,
        form: DemandForm,
        poster_date: str,
        signup_qr: str | None,
        community_qr: str | None,
    ) -> str:
        city = html.escape(form.city.strip())
        poster_date_html = self._format_multiline(poster_date)
        requirement_html = self._format_requirement(form.player_requirement_desc)
        activity_html = self._format_multiline(form.activity_description)
        duration_html = self._format_multiline(form.duration)
        reward_html = self._format_multiline(form.reward_amount)
        signup_qr_html = self._qr_html(signup_qr, "报名二维码")
        community_qr_html = self._qr_html(community_qr, "社群二维码")
        signup_notice_html = self._format_paragraphs(
            "我们是一家专注于手游以及泛娱乐领域市场研究与用户调研的咨询服务团队，长期服务于各类游戏厂商、互联网平台及品牌客户，帮助他们了解玩家需求、用户体验和市场反馈。\n"
            "我们会不定期发布各类市场调研招募需求，包括但不限于：一对一深度访谈、线上/线下问卷调研、游戏试玩测试、产品体验反馈、玩家座谈会、社区共创活动等。无论你是重度游戏玩家、轻度休闲玩家，还是对游戏、动漫、影视、潮玩等内容感兴趣的用户，都有机会参与到我们的调研项目中。\n"
            "参与调研不仅可以表达自己的真实想法，帮助产品优化和内容改进，也有机会获得相应的调研报酬、礼品奖励或测试资格。欢迎大家关注我们，及时了解最新招募信息，参与更多有趣、有价值的市场调研活动！"
        )
        public_notice_html = self._format_paragraphs(
            "1. 所有调研项目均以真实用户反馈为基础，请根据自身情况如实填写报名信息。\n"
            "2. 不同项目会有不同的筛选条件，如游戏经历、设备情况、年龄区间、所在城市等，报名后是否入选以项目匹配结果为准。\n"
            "3. 部分项目可能涉及保密内容，入选用户需遵守相关保密要求，不随意传播测试内容、问卷截图或访谈信息。\n"
            "4. 调研报酬或奖励形式会在具体招募信息中说明，请以当次项目规则为准。\n"
            "5. 我们不会要求用户缴纳任何费用，也不会索要与调研无关的敏感信息，请注意甄别信息安全。"
        )

        return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <style>
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: #c9f4f8;
      font-family: "SimSun", "Songti SC", "Microsoft YaHei", serif;
    }}
    .poster {{
      position: relative;
      width: 800px;
      min-height: 0;
      overflow: hidden;
      color: #17617f;
      background:
        radial-gradient(circle at 82% 8%, rgba(255,255,255,.86) 0 2px, transparent 3px),
        radial-gradient(circle at 16% 20%, rgba(255,255,255,.72) 0 1px, transparent 2px),
        radial-gradient(ellipse at 72% 34%, rgba(255,255,255,.42), transparent 30%),
        radial-gradient(ellipse at 20% 72%, rgba(186,255,222,.38), transparent 28%),
        linear-gradient(150deg, #c5f5e2 0%, #b7f0ff 28%, #63d4ec 54%, #d4fff0 100%);
      padding: 28px 0 72px;
    }}
    .grid-line-x,
    .grid-line-y {{
      position: absolute;
      pointer-events: none;
      opacity: .58;
      background: rgba(255,255,255,.78);
    }}
    .grid-line-x {{ left: 0; right: 0; height: 2px; }}
    .grid-line-y {{ top: 0; bottom: 0; width: 2px; }}
    .poster::before {{
      content: "";
      position: absolute;
      inset: 0;
      pointer-events: none;
      opacity: .48;
      background:
        repeating-linear-gradient(92deg, rgba(255,255,255,.42) 0 2px, transparent 2px 260px),
        repeating-linear-gradient(0deg, rgba(255,255,255,.32) 0 2px, transparent 2px 320px),
        radial-gradient(ellipse at 72% 18%, transparent 0 56px, rgba(255,255,255,.44) 58px 62px, transparent 64px),
        radial-gradient(ellipse at 82% 62%, transparent 0 84px, rgba(255,255,255,.34) 86px 91px, transparent 93px);
    }}
    .poster::after {{
      content: "";
      position: absolute;
      inset: 0;
      pointer-events: none;
      background:
        radial-gradient(circle at 8% 6%, rgba(255,255,255,.75) 0 1px, transparent 2px),
        radial-gradient(circle at 92% 48%, rgba(255,255,255,.65) 0 1px, transparent 2px);
      background-size: 96px 96px, 130px 130px;
    }}
    .top-kicker {{
      position: relative;
      z-index: 1;
      display: flex;
      justify-content: space-between;
      width: 650px;
      margin: 10px auto 4px;
      color: #17617f;
      font-size: 13px;
      font-style: italic;
      opacity: .85;
    }}
    .hero {{
      position: relative;
      z-index: 1;
      width: 650px;
      margin: 0 auto 6px;
      height: 210px;
    }}
    .title {{
      position: absolute;
      left: 42px;
      top: 28px;
      color: #07557b;
      font-size: 86px;
      line-height: 1;
      font-weight: 400;
      letter-spacing: 0;
    }}
    .title::before,
    .title::after {{
      content: "*";
      position: absolute;
      color: #07557b;
      font-size: 34px;
      font-family: "Times New Roman", serif;
    }}
    .title::before {{ left: -38px; top: 54px; }}
    .title::after {{ right: -34px; top: -8px; }}
    .script {{
      position: absolute;
      left: 250px;
      top: 96px;
      color: #56c7e1;
      font-family: "Brush Script MT", "Segoe Script", cursive;
      font-size: 74px;
      font-weight: 400;
      font-style: italic;
      text-shadow: -1px -1px 0 rgba(255,255,255,.75), 1px 1px 0 rgba(255,255,255,.75);
    }}
    .sheet {{
      position: relative;
      z-index: 1;
      width: 580px;
      margin: -10px 0 0 50px;
      padding: 34px 34px 54px;
      background: #fffdf0;
    }}
    .section {{
      position: relative;
      margin: 0 0 54px;
      padding-top: 2px;
    }}
    .section:last-child {{ margin-bottom: 0; }}
    .section::after {{
      content: "";
      position: absolute;
      right: -92px;
      top: 10px;
      width: 54px;
      height: 138px;
      border-radius: 0 14px 14px 0;
      background: #08acd2;
    }}
    .section.short-tab::after {{ height: 110px; }}
    .section.no-tab::after {{ display: none; }}
    .section-title {{
      display: flex;
      align-items: center;
      gap: 10px;
      margin: 0 0 24px;
      color: #07557b;
      font-size: 31px;
      font-weight: 800;
      line-height: 1.2;
      text-shadow: 1px 1px 0 rgba(0, 90, 120, .18);
    }}
    .section-title::before {{
      content: "";
      width: 26px;
      height: 26px;
      border: 2px solid #4d9fc0;
      border-radius: 50%;
      background: #fffdf0;
      flex: 0 0 auto;
    }}
    .content {{
      color: #17617f;
      font-size: 24px;
      line-height: 1.68;
      letter-spacing: 0;
      word-break: break-word;
    }}
    .content strong,
    .accent {{
      color: #17617f;
      font-weight: 800;
    }}
    .detail-list {{ display: grid; gap: 22px; }}
    .detail-row {{
      display: grid;
      grid-template-columns: 132px minmax(0, 1fr);
      gap: 12px;
      align-items: baseline;
      color: #17617f;
      font-size: 24px;
      line-height: 1.55;
    }}
    .detail-label {{ white-space: nowrap; }}
    .qr-wrap {{
      display: grid;
      place-items: center;
      margin: 28px auto 0;
      width: 304px;
      min-height: 304px;
      border-radius: 10px;
      background: #08acd2;
      color: #17617f;
      font-size: 14px;
    }}
    .qr-wrap img {{
      width: 238px;
      height: 238px;
      object-fit: contain;
      background: #fff;
      padding: 8px;
    }}
    .notice {{
      width: 100%;
      margin: 8px auto 0;
      font-size: 23px;
      line-height: 1.72;
      text-align: left;
      text-indent: 2em;
    }}
    .rules {{
      font-size: 22px;
      line-height: 1.68;
    }}
    .bubble {{
      position: absolute;
      right: -76px;
      top: -46px;
      width: 72px;
      height: 72px;
      border-radius: 50%;
      background: rgba(8,172,210,.72);
      box-shadow: 38px -26px 0 rgba(8,172,210,.58), -34px 26px 0 rgba(8,172,210,.58);
    }}
  </style>
</head>
<body>
  <main class="poster">
    <div class="grid-line-x" style="top:260px"></div>
    <div class="grid-line-x" style="top:1220px"></div>
    <div class="grid-line-x" style="top:2400px"></div>
    <div class="grid-line-y" style="left:50px"></div>
    <div class="grid-line-y" style="right:54px"></div>
    <div class="top-kicker"><span>游戏招募</span><span>Gaming Recruitment</span></div>
    <header class="hero">
      <div class="title">玩家招募</div>
      <div class="script">Recruitment</div>
    </header>
    <section class="sheet">
      <article class="section">
        <h2 class="section-title">玩家要求</h2>
        <div class="content">{requirement_html}</div>
      </article>

      <article class="section">
        <h2 class="section-title">活动详情</h2>
        <div class="detail-list">
          <div class="detail-row"><span class="detail-label">活动时间:</span><span>{poster_date_html}</span></div>
          <div class="detail-row"><span class="detail-label">活动时长:</span><span>{duration_html}</span></div>
          <div class="detail-row"><span class="detail-label">活动地点:</span><span>{city}</span></div>
        </div>
      </article>

      <article class="section short-tab">
        <h2 class="section-title">活动内容</h2>
        <div class="content">{activity_html}</div>
      </article>

      <article class="section short-tab">
        <h2 class="section-title">活动礼金</h2>
        <div class="content">{reward_html}</div>
      </article>

      <article class="section short-tab">
        <div class="bubble"></div>
        <h2 class="section-title">报名链接</h2>
        <div class="content">欢迎玩家们扫码报名~</div>
        <div class="qr-wrap">{signup_qr_html}</div>
      </article>

      <article class="section no-tab">
        <h2 class="section-title">报名须知</h2>
        <div class="content notice">{signup_notice_html}</div>
      </article>

      <article class="section no-tab">
        <h2 class="section-title">注意事项</h2>
        <div class="content rules">{public_notice_html}</div>
      </article>

      <article class="section no-tab">
        <h2 class="section-title">联系方式</h2>
        <div class="content">更多的活动资讯会在社群同步，欢迎扫码加入</div>
        <div class="qr-wrap">{community_qr_html}</div>
      </article>
    </section>
  </main>
</body>
</html>"""

    def _format_requirement(self, value: str) -> str:
        lines = [line.strip() for line in value.splitlines() if line.strip()]
        html_lines = []
        for index, line in enumerate(lines):
            escaped = html.escape(line)
            match = re.match(r"^([^:：]+)([:：])(.*)$", line)
            numbered = re.match(r"^(\d+[、.．]\s*[^，,：:、.．]*)(.*)$", line)
            if match:
                label, colon, rest = match.groups()
                html_lines.append(
                    f'<span class="accent">{html.escape(label + colon)}</span>{html.escape(rest)}'
                )
            elif numbered:
                label, rest = numbered.groups()
                html_lines.append(
                    f'<span class="accent">{html.escape(label)}</span>{html.escape(rest)}'
                )
            elif index == 0:
                html_lines.append(f'<span class="accent">{escaped}</span>')
            else:
                html_lines.append(escaped)
        return "<br>".join(html_lines)

    def _format_multiline(self, value: str) -> str:
        return "<br>".join(html.escape(line.strip()) for line in value.splitlines() if line.strip())

    def _format_paragraphs(self, value: str) -> str:
        return "<br>".join(html.escape(line.strip()) for line in value.splitlines() if line.strip())

    def _qr_html(self, data_url: str | None, label: str) -> str:
        if data_url:
            return f'<img src="{data_url}" alt="{html.escape(label)}">'
        return '<span>二维码</span>'

    def _template_data_url(self) -> str:
        if not self.template_path.exists():
            raise RuntimeError(f"脱敏海报模板不存在：{self.template_path}")
        encoded = base64.b64encode(self.template_path.read_bytes()).decode("ascii")
        return f"data:image/png;base64,{encoded}"

    def _safe_name(self, value: str) -> str:
        safe = re.sub(r"[^a-zA-Z0-9_-]+", "-", value).strip("-")
        return safe or "public-poster"

    def _to_data_url(self, image: bytes | None, content_type: str | None) -> str | None:
        if not image:
            return None
        mime = content_type or "image/png"
        encoded = base64.b64encode(image).decode("ascii")
        return f"data:{mime};base64,{encoded}"


public_poster_service = PublicPosterService()