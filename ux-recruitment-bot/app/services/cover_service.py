import html
import time
from pathlib import Path

from app.models.demand import DemandForm


class CoverService:
    """Render a simple horizontal cover poster for WeChat articles."""

    def __init__(self) -> None:
        app_dir = Path(__file__).resolve().parents[1]
        self.output_dir = app_dir / "static" / "generated" / "covers"

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
                "Playwright 未安装，无法自动渲染封面海报。请先运行：pip install playwright && playwright install chromium"
            ) from exc

        self.output_dir.mkdir(parents=True, exist_ok=True)
        output_name = f"cover-{self._safe_name(form.project_id)}-{int(time.time())}.png"
        output_path = self.output_dir / output_name

        title = cover_title or f"招募{form.city}游戏玩家\n参与线下游戏体验"
        page_html = self._build_html(
            deadline=deadline or "待定",
            title=title,
        )

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
            raise RuntimeError(f"封面海报渲染失败：{exc}") from exc

        return {
            "path": str(output_path),
            "url": f"/static/generated/covers/{output_name}",
        }

    def _build_html(self, deadline: str, title: str) -> str:
        title_lines = [line.strip() for line in title.splitlines() if line.strip()]
        title_html = "<br>".join(html.escape(line) for line in title_lines)
        deadline_html = html.escape(deadline)
        title_length = max((len(line) for line in title_lines), default=0)
        line_count = max(len(title_lines), 1)
        title_font_size = 88
        title_top = 210
        title_line_height = 1.28
        if title_length >= 14:
            title_font_size = 78
            title_top = 198
            title_line_height = 1.18
        if title_length >= 17:
            title_font_size = 68
            title_top = 190
            title_line_height = 1.14
        if title_length >= 21 or line_count >= 3:
            title_font_size = 60
            title_top = 182
            title_line_height = 1.14
        return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <style>
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: #ffffff;
      font-family: "Microsoft YaHei", "PingFang SC", "Noto Sans CJK SC", Arial, sans-serif;
    }}
    .cover {{
      position: relative;
      width: 1600px;
      height: 1200px;
      overflow: hidden;
      background: #5d12e8;
    }}
    .panel {{
      position: absolute;
      left: 120px;
      top: 345px;
      width: 1380px;
      height: 500px;
      background: #f7f7f3;
      border: 8px solid #eeeeea;
    }}
    .deadline {{
      position: absolute;
      left: 72px;
      top: 76px;
      color: #050505;
      font-size: 66px;
      line-height: 1.1;
      font-weight: 900;
      letter-spacing: 0;
    }}
    .title {{
      position: absolute;
      left: 72px;
      top: {title_top}px;
      max-width: none;
      color: #050505;
      font-size: {title_font_size}px;
      line-height: {title_line_height};
      font-weight: 900;
      letter-spacing: 0;
      white-space: nowrap;
    }}
    .badge {{
      position: absolute;
      right: -62px;
      top: -68px;
      width: 270px;
      height: 270px;
      color: #111111;
      display: grid;
      place-items: center;
      transform: rotate(-14deg);
    }}
    .badge-shape {{
      position: absolute;
      inset: 0;
      background: #ffd24b;
      clip-path: polygon(
        50% 0%, 58% 15%, 72% 6%, 76% 23%, 93% 20%, 88% 38%,
        100% 50%, 88% 62%, 93% 80%, 76% 77%, 72% 94%, 58% 85%,
        50% 100%, 42% 85%, 28% 94%, 24% 77%, 7% 80%, 12% 62%,
        0% 50%, 12% 38%, 7% 20%, 24% 23%, 28% 6%, 42% 15%
      );
    }}
    .badge-text {{
      position: relative;
      width: 190px;
      text-align: center;
      font-size: 31px;
      line-height: 1.05;
      font-weight: 900;
      transform: rotate(14deg);
    }}
    .dice {{
      position: absolute;
      left: 40px;
      bottom: 102px;
      width: 260px;
      height: 220px;
      transform: rotate(-15deg);
      filter: drop-shadow(0 14px 0 rgba(0,0,0,0.22));
    }}
    .dice .face {{
      position: absolute;
      width: 178px;
      height: 178px;
      border: 10px solid #40566f;
      border-radius: 34px;
      background: linear-gradient(135deg, #ffef79 0 50%, #69ddea 51%);
    }}
    .dice .top {{
      position: absolute;
      left: 30px;
      top: -46px;
      width: 178px;
      height: 92px;
      border: 10px solid #40566f;
      border-bottom: 0;
      border-radius: 34px 34px 8px 8px;
      background: #ef6aa4;
      transform: skewX(-25deg);
    }}
    .dot {{
      position: absolute;
      width: 24px;
      height: 24px;
      border-radius: 50%;
      background: #fff;
    }}
    .d1 {{ left: 50px; top: 70px; }}
    .d2 {{ left: 112px; top: 118px; }}
    .d3 {{ left: 132px; top: 50px; }}
    .d4 {{ left: 70px; top: 128px; }}
    .coin {{
      position: absolute;
      right: 130px;
      top: 300px;
      width: 88px;
      height: 88px;
      border-radius: 50%;
      background: #ffd05a;
      border: 10px solid #f4a329;
      color: #df8020;
      font-size: 64px;
      font-weight: 900;
      text-align: center;
      line-height: 68px;
      transform: rotate(18deg);
    }}
    .mushroom {{
      position: absolute;
      right: 235px;
      top: 350px;
      width: 130px;
      height: 110px;
    }}
    .mushroom::before {{
      content: "";
      position: absolute;
      left: 0;
      top: 0;
      width: 130px;
      height: 76px;
      border-radius: 70px 70px 35px 35px;
      background: radial-gradient(circle at 34px 30px, #eee 0 23px, transparent 24px),
                  radial-gradient(circle at 86px 26px, #eee 0 23px, transparent 24px),
                  #e95d53;
    }}
    .mushroom::after {{
      content: "";
      position: absolute;
      left: 38px;
      top: 54px;
      width: 66px;
      height: 56px;
      border-radius: 10px 10px 30px 30px;
      background: #ffcf7a;
      box-shadow: inset 18px 24px 0 -13px #1b1b1b, inset 48px 24px 0 -13px #1b1b1b;
    }}
    .star {{
      position: absolute;
      right: 260px;
      top: 505px;
      color: #ff9e53;
      font-size: 112px;
      transform: rotate(-12deg);
    }}
    .person {{
      position: absolute;
      right: 18px;
      bottom: -26px;
      width: 330px;
      height: 410px;
    }}
    .head {{
      position: absolute;
      left: 128px;
      top: 25px;
      width: 86px;
      height: 96px;
      border-radius: 46% 46% 48% 48%;
      background: #ffd7d2;
      border-top: 26px solid #2e1719;
    }}
    .body {{
      position: absolute;
      left: 90px;
      top: 125px;
      width: 142px;
      height: 162px;
      border-radius: 28px;
      background: #9d755f;
      transform: rotate(-5deg);
    }}
    .phone {{
      position: absolute;
      left: 96px;
      top: 150px;
      width: 112px;
      height: 64px;
      border-radius: 12px;
      background: #262126;
      transform: rotate(8deg);
    }}
    .chair {{
      position: absolute;
      left: 42px;
      bottom: 20px;
      width: 250px;
      height: 150px;
      border-radius: 50px 50px 34px 34px;
      background: #c7b5ac;
    }}
    .leg {{
      position: absolute;
      width: 76px;
      height: 168px;
      border-radius: 45px;
      background: #ffd7d2;
      bottom: 0;
    }}
    .leg.left {{ left: 84px; transform: rotate(20deg); }}
    .leg.right {{ left: 190px; transform: rotate(-9deg); }}
  </style>
</head>
<body>
  <div class="cover">
    <div class="panel">
      <div class="deadline">活动截止：{deadline_html}</div>
      <div class="title">{title_html}</div>
      <div class="badge"><div class="badge-shape"></div><div class="badge-text">WELCOME<br>WELCOME</div></div>
      <div class="coin">?</div>
      <div class="mushroom"></div>
      <div class="star">★</div>
    </div>
    <div class="dice">
      <div class="top"><span class="dot d3"></span></div>
      <div class="face"><span class="dot d1"></span><span class="dot d2"></span><span class="dot d4"></span></div>
    </div>
    <div class="person">
      <div class="chair"></div>
      <div class="leg left"></div>
      <div class="leg right"></div>
      <div class="body"></div>
      <div class="head"></div>
      <div class="phone"></div>
    </div>
  </div>
</body>
</html>"""

    def _safe_name(self, value: str) -> str:
        safe = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in value).strip("-")
        return safe or "cover"


cover_service = CoverService()
