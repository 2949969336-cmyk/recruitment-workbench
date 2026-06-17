import html
import time
from pathlib import Path

from app.models.demand import DemandForm


class PublicCoverService:
    """Render a desensitized horizontal cover for the public WeChat account."""

    def __init__(self) -> None:
        app_dir = Path(__file__).resolve().parents[1]
        self.output_dir = app_dir / "static" / "generated" / "public-covers"

    async def render_cover(
        self,
        form: DemandForm,
        deadline: str | None = None,
        cover_title: str | None = None,
    ) -> dict:
        try:
            from playwright.async_api import async_playwright
        except ImportError as exc:
            raise RuntimeError(
                "Playwright 未安装，无法自动渲染脱敏封面。请先运行：pip install playwright && playwright install chromium"
            ) from exc

        self.output_dir.mkdir(parents=True, exist_ok=True)
        output_name = f"public-cover-{self._safe_name(form.project_id)}-{int(time.time())}.png"
        output_path = self.output_dir / output_name

        title = cover_title or f"招募{form.city}游戏玩家\n参与线下游戏体验"
        page_html = self._build_html(deadline=deadline or "待定", title=title)

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                context = await browser.new_context(
                    viewport={"width": 1600, "height": 1200},
                    device_scale_factor=2,
                )
                page = await context.new_page()
                await page.set_content(page_html, wait_until="load")
                await page.locator(".cover").screenshot(path=str(output_path))
                await context.close()
                await browser.close()
        except Exception as exc:
            raise RuntimeError(f"脱敏封面渲染失败：{exc}") from exc

        return {
            "path": str(output_path),
            "url": f"/static/generated/public-covers/{output_name}",
        }

    def _build_html(self, deadline: str, title: str) -> str:
        title_lines = [line.strip() for line in title.splitlines() if line.strip()]
        title_html = "".join(f'<span class="title-line">{html.escape(line)}</span>' for line in title_lines)
        deadline_html = html.escape(deadline)
        title_length = max((len(line) for line in title_lines), default=0)
        line_count = max(len(title_lines), 1)
        title_font_size = 92
        if title_length >= 15:
            title_font_size = 82
        if title_length >= 19:
            title_font_size = 72
        if title_length >= 24 or line_count >= 3:
            title_font_size = 64

        return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <style>
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: #ffffff;
      font-family: "Microsoft YaHei UI", "Microsoft YaHei", "PingFang SC", Arial, sans-serif;
    }}
    .cover {{
      position: relative;
      width: 1600px;
      height: 1200px;
      overflow: hidden;
      color: #07557b;
      background:
        radial-gradient(circle at 17% 18%, rgba(255,255,255,.82) 0 9%, transparent 22%),
        radial-gradient(circle at 80% 32%, rgba(255,255,255,.62) 0 7%, transparent 22%),
        radial-gradient(circle at 72% 86%, rgba(210,255,238,.68) 0 8%, transparent 24%),
        linear-gradient(150deg, #c5f5e2 0%, #b7f0ff 33%, #63d4ec 62%, #d4fff0 100%);
    }}
    .cover::before {{
      content: "";
      position: absolute;
      inset: 0;
      opacity: .38;
      background:
        linear-gradient(90deg, rgba(255,255,255,.72) 1px, transparent 1px),
        linear-gradient(0deg, rgba(255,255,255,.72) 1px, transparent 1px);
      background-size: 132px 132px;
    }}
    .cover::after {{
      content: "";
      position: absolute;
      inset: 34px;
      border: 2px solid rgba(255,255,255,.62);
      pointer-events: none;
    }}
    .noise {{
      position: absolute;
      inset: 0;
      background:
        radial-gradient(circle at 12% 72%, rgba(7,85,123,.16) 0 1px, transparent 2px),
        radial-gradient(circle at 58% 30%, rgba(255,255,255,.55) 0 1px, transparent 2px);
      background-size: 60px 60px, 82px 82px;
      opacity: .42;
    }}
    .sheet {{
      position: absolute;
      left: 140px;
      top: 205px;
      width: 1120px;
      height: 770px;
      background: #fffdf0;
      box-shadow: 28px 28px 0 rgba(7,85,123,.16);
      border: 1px solid rgba(7,85,123,.08);
    }}
    .sheet::before {{
      content: "";
      position: absolute;
      left: 38px;
      top: 38px;
      width: 18px;
      height: 18px;
      border: 3px solid #4d9fc0;
      border-radius: 50%;
      background: #fffdf0;
    }}
    .sheet::after {{
      content: "";
      position: absolute;
      right: -86px;
      top: 124px;
      width: 94px;
      height: 232px;
      border-radius: 0 22px 22px 0;
      background: #08acd2;
    }}
    .kicker {{
      position: absolute;
      left: 92px;
      top: 68px;
      color: #17617f;
      font-family: "Times New Roman", serif;
      font-size: 22px;
      font-style: italic;
      letter-spacing: .08em;
    }}
    .script {{
      position: absolute;
      left: 462px;
      top: 222px;
      color: #56c7e1;
      font-family: "Brush Script MT", "Segoe Script", cursive;
      font-size: 104px;
      line-height: 1;
      font-weight: 400;
      transform: rotate(-4deg);
    }}
    .deadline {{
      position: absolute;
      left: 92px;
      top: 104px;
      font-size: 44px;
      line-height: 1;
      font-weight: 700;
      color: #17617f;
    }}
    .title {{
      position: absolute;
      left: 72px;
      top: 206px;
      width: 1080px;
      color: #07557b;
      font-size: {title_font_size}px;
      line-height: 1.14;
      font-weight: 700;
      letter-spacing: 0;
    }}
    .title-line {{
      display: block;
      white-space: nowrap;
    }}
    .title strong {{
      color: #08acd2;
    }}
    .tag {{
      position: absolute;
      left: 92px;
      bottom: 76px;
      padding: 20px 34px;
      border-radius: 999px;
      background: rgba(8,172,210,.16);
      color: #07557b;
      font-size: 30px;
      font-weight: 700;
    }}
    .side-text {{
      position: absolute;
      right: 178px;
      top: 355px;
      writing-mode: vertical-rl;
      color: #07557b;
      font-size: 24px;
      letter-spacing: .22em;
      font-family: "Times New Roman", serif;
    }}
    .bubble {{
      position: absolute;
      border-radius: 50%;
      background: rgba(8,172,210,.68);
      mix-blend-mode: multiply;
    }}
    .b1 {{ width: 120px; height: 120px; right: 255px; bottom: 228px; }}
    .b2 {{ width: 86px; height: 86px; right: 198px; bottom: 300px; opacity: .72; }}
    .b3 {{ width: 62px; height: 62px; right: 300px; bottom: 330px; opacity: .65; }}
    .spark {{
      position: absolute;
      color: rgba(255,255,255,.95);
      font-size: 90px;
      line-height: 1;
      text-shadow: 0 0 18px rgba(8,172,210,.36);
    }}
    .s1 {{ left: 75px; top: 88px; }}
    .s2 {{ right: 155px; top: 146px; transform: rotate(18deg); }}
    .s3 {{ left: 106px; bottom: 120px; transform: rotate(-18deg); }}
    .footer {{
      position: absolute;
      left: 142px;
      bottom: 92px;
      color: #17617f;
      font-family: "Times New Roman", serif;
      font-size: 28px;
      letter-spacing: .28em;
    }}
  </style>
</head>
<body>
  <div class="cover">
    <div class="noise"></div>
    <div class="kicker">Gaming Recruitment</div>
    <div class="script">Recruitment</div>
    <div class="sheet">
      <div class="deadline">活动截止：{deadline_html}</div>
      <div class="title">{title_html}</div>
      <div class="tag">游戏世界任你闯荡</div>
    </div>
    <div class="side-text">GAME TESTING RECRUITMENT</div>
    <div class="bubble b1"></div>
    <div class="bubble b2"></div>
    <div class="bubble b3"></div>
    <div class="spark s1">✧</div>
    <div class="spark s2">✦</div>
    <div class="spark s3">✧</div>
    <div class="footer">GAME TESTING RECRUITMENT</div>
  </div>
</body>
</html>"""

    def _safe_name(self, value: str) -> str:
        safe = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in value).strip("-")
        return safe or "public-cover"


public_cover_service = PublicCoverService()
