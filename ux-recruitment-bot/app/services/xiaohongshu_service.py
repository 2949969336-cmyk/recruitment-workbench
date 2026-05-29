import html
import time
from pathlib import Path

from app.models.demand import DemandForm


class XiaohongshuService:
    """Render a vertical Xiaohongshu-style recruitment poster."""

    def __init__(self) -> None:
        app_dir = Path(__file__).resolve().parents[1]
        self.output_dir = app_dir / "static" / "generated" / "xiaohongshu"

    async def render_poster(self, form: DemandForm) -> dict:
        try:
            from playwright.async_api import async_playwright
        except ImportError as exc:
            raise RuntimeError(
                "Playwright 未安装，无法自动渲染小红书海报。请先运行：pip install playwright && playwright install chromium"
            ) from exc

        self.output_dir.mkdir(parents=True, exist_ok=True)
        output_name = f"xhs-{self._safe_name(form.project_id)}-{int(time.time())}.png"
        output_path = self.output_dir / output_name
        page_html = self._build_html(form)

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                context = await browser.new_context(
                    viewport={"width": 800, "height": 1365},
                    device_scale_factor=2,
                )
                page = await context.new_page()
                await page.set_content(page_html, wait_until="load")
                await page.locator(".xhs-poster").screenshot(path=str(output_path))
                await context.close()
                await browser.close()
        except Exception as exc:
            raise RuntimeError(f"小红书海报渲染失败：{exc}") from exc

        return {
            "path": str(output_path),
            "url": f"/static/generated/xiaohongshu/{output_name}",
        }

    def _build_html(self, form: DemandForm) -> str:
        city = html.escape(form.city.strip())
        game = html.escape(form.game_category.strip())
        requirement = self._format_requirement(form.player_requirement_desc)
        activity = self._format_multiline(form.activity_description)
        date = self._format_multiline(form.activity_date)
        reward = self._format_multiline(form.reward_amount)
        location = self._format_multiline(form.location)
        duration = self._format_multiline(form.duration)

        return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <style>
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: #ffffff;
      font-family: "Songti SC", "SimSun", "Noto Serif CJK SC", serif;
    }}
    .xhs-poster {{
      position: relative;
      width: 800px;
      min-height: 1365px;
      overflow: hidden;
      color: #140f0d;
      background:
        radial-gradient(circle at 96% 2%, rgba(255, 232, 134, 0.8), transparent 34%),
        linear-gradient(135deg, #f7f6f0 0%, #fff7dd 58%, #ffe184 100%);
      padding: 28px 38px 26px;
    }}
    .pixel-spark {{
      position: absolute;
      left: 30px;
      top: 28px;
      width: 190px;
      height: 46px;
      background:
        radial-gradient(circle at 12% 50%, #000 0 18px, transparent 19px),
        radial-gradient(circle at 36% 50%, #000 0 18px, transparent 19px),
        radial-gradient(circle at 60% 50%, #000 0 18px, transparent 19px),
        radial-gradient(circle at 84% 50%, #000 0 18px, transparent 19px);
      filter: contrast(200%);
    }}
    .burst {{
      position: absolute;
      right: -14px;
      top: 0;
      width: 205px;
      height: 165px;
      display: grid;
      place-items: center;
      transform: rotate(-12deg);
    }}
    .burst::before {{
      content: "";
      position: absolute;
      inset: 0;
      background: #fff0a9;
      border: 4px solid #000;
      clip-path: polygon(50% 0, 60% 16%, 75% 7%, 78% 25%, 97% 22%, 86% 40%, 100% 50%, 86% 60%, 97% 78%, 78% 75%, 75% 93%, 60% 84%, 50% 100%, 40% 84%, 25% 93%, 22% 75%, 3% 78%, 14% 60%, 0 50%, 14% 40%, 3% 22%, 22% 25%, 25% 7%, 40% 16%);
    }}
    .burst span {{
      position: relative;
      font-family: Arial, sans-serif;
      font-size: 38px;
      font-weight: 900;
      transform: rotate(-4deg);
    }}
    .hero {{
      margin-top: 72px;
      padding-bottom: 28px;
      position: relative;
    }}
    .title {{
      position: relative;
      z-index: 1;
      font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
      font-size: 86px;
      line-height: 0.96;
      font-weight: 900;
      letter-spacing: 0;
      text-shadow: 3px 0 #000;
    }}
    .subtitle {{
      position: relative;
      z-index: 2;
      width: 650px;
      margin: -3px 0 0 36px;
      padding: 8px 34px 14px;
      border: 5px solid #000;
      background: #fff;
      transform: skewX(-8deg);
      font-family: "Courier New", monospace;
      font-size: 36px;
      line-height: 1.05;
      letter-spacing: -1px;
    }}
    .card {{
      position: relative;
      margin: 26px 14px 0;
      padding: 28px 34px;
      background:
        linear-gradient(rgba(0,0,0,0.028) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,0,0,0.028) 1px, transparent 1px),
        #ffffff;
      background-size: 18px 18px;
      border: 7px solid #211511;
      box-shadow: 15px 15px 0 #211511;
      font-size: 33px;
      line-height: 1.72;
    }}
    .card.small {{
      margin-top: 58px;
      padding: 26px 34px 64px;
      min-height: 420px;
    }}
    .label {{
      font-weight: 700;
      white-space: nowrap;
    }}
    .accent {{
      color: #f4a536;
      white-space: nowrap;
    }}
    .block {{
      margin: 0 0 20px;
    }}
    .right-text {{
      position: absolute;
      right: 20px;
      top: 470px;
      writing-mode: vertical-rl;
      font-family: "Times New Roman", serif;
      font-size: 26px;
      letter-spacing: 8px;
    }}
    .sticker {{
      position: absolute;
      right: 34px;
      top: -34px;
      padding: 10px 22px;
      border-radius: 50%;
      background: #fff7dd;
      font-family: "Microsoft YaHei", sans-serif;
      font-size: 24px;
      font-weight: 900;
      transform: rotate(12deg);
    }}
    .eyes {{
      position: absolute;
      right: -8px;
      bottom: -62px;
      width: 300px;
      height: 180px;
    }}
    .eye {{
      position: absolute;
      width: 120px;
      height: 170px;
      border: 4px solid #000;
      border-radius: 56% 56% 48% 48%;
      background: #fff;
      transform: rotate(-20deg);
    }}
    .eye::after {{
      content: "";
      position: absolute;
      left: 34px;
      top: 74px;
      width: 56px;
      height: 62px;
      border-radius: 50%;
      background: #211511;
    }}
    .eye:nth-child(2) {{ left: 86px; top: -12px; }}
    .eye:nth-child(3) {{ left: 166px; top: 0; }}
    .footer {{
      margin-top: 62px;
      text-align: center;
      font-family: "Times New Roman", serif;
      font-size: 30px;
      letter-spacing: 7px;
    }}
  </style>
</head>
<body>
  <div class="xhs-poster">
    <div class="pixel-spark"></div>
    <div class="burst"><span>PLAY</span></div>
    <div class="hero">
      <div class="title">{city}玩家招募</div>
      <div class="subtitle">{city}-GameRecruitment</div>
    </div>

    <section class="card">
      <p class="block"><span class="label">【玩家要求】</span> 我们希望您是 {requirement}</p>
      <p class="block"><span class="label">【活动内容】</span><br>{activity}</p>
    </section>

    <section class="card small">
      <div class="sticker">游戏世界任你闯荡</div>
      <p class="block"><span class="label">【活动时间】</span><br>{date}</p>
      <p class="block"><span class="label">【测试时长】</span><br>{duration}</p>
      <p class="block"><span class="label">【活动地点】</span><br>{location}</p>
      <p class="block"><span class="label">【活动礼金】</span><br>{reward}</p>
      <p class="block"><span class="label">【报名方式】</span><br>私聊报名</p>
      <div class="eyes"><div class="eye"></div><div class="eye"></div><div class="eye"></div></div>
    </section>

    <div class="right-text">GAME TESTING RECRUITMENT</div>
    <div class="footer">GAME TESTING RECRUITMENT</div>
  </div>
</body>
</html>"""

    def _format_requirement(self, value: str) -> str:
        first_line = next((line.strip() for line in value.splitlines() if line.strip()), "")
        if "：" in first_line:
            name, detail = first_line.split("：", 1)
            return f'<span class="accent">{html.escape(name.strip())}</span>{html.escape(detail.strip())}'
        elif ":" in first_line:
            name, detail = first_line.split(":", 1)
            return f'<span class="accent">{html.escape(name.strip())}</span>{html.escape(detail.strip())}'
        return html.escape(first_line or value.strip()).replace("\n", "<br>")

    def _format_multiline(self, value: str) -> str:
        return "<br>".join(html.escape(line.strip()) for line in value.splitlines() if line.strip())

    def _safe_name(self, value: str) -> str:
        safe = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in value).strip("-")
        return safe or "xiaohongshu"


xiaohongshu_service = XiaohongshuService()
