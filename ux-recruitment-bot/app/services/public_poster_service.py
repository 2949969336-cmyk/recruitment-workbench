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
        self.output_dir = app_dir / "static" / "generated" / "public-posters"

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
                    viewport={"width": 900, "height": 2200},
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

        return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <style>
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: #fff;
      font-family: "Microsoft YaHei", "PingFang SC", Arial, sans-serif;
    }}
    .poster {{
      position: relative;
      width: 800px;
      min-height: 2100px;
      overflow: hidden;
      color: #201612;
      background:
        radial-gradient(circle at 12% 6%, rgba(255,255,255,.9), transparent 22%),
        linear-gradient(158deg, #f9f9f7 0%, #fff3bc 52%, #ffc66e 100%);
      padding: 34px 42px 44px;
    }}
    .spark-row {{
      display: flex;
      gap: 8px;
      margin-left: 4px;
      margin-bottom: 8px;
    }}
    .spark-row span {{
      width: 28px;
      height: 28px;
      background: #000;
      border-radius: 50%;
      display: block;
    }}
    .hero {{
      position: relative;
      margin-bottom: 28px;
    }}
    .title {{
      font-size: 68px;
      line-height: 1;
      font-weight: 900;
      letter-spacing: 0;
      font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
    }}
    .subtitle {{
      width: 520px;
      margin: 8px 0 0 38px;
      padding: 8px 24px 12px;
      border: 4px solid #1c1715;
      background: #fff;
      transform: skewX(-8deg);
      font-family: "Courier New", monospace;
      font-size: 30px;
      line-height: 1;
    }}
    .hero-badge {{
      position: absolute;
      right: 6px;
      top: -14px;
      width: 132px;
      height: 132px;
      border-radius: 30px;
      background: linear-gradient(135deg, #ffb94b, #ffefe2);
      display: grid;
      place-items: center;
      color: #f79628;
      font-size: 72px;
      font-weight: 900;
      filter: drop-shadow(0 8px 12px rgba(120,74,22,.2));
    }}
    .play {{
      position: absolute;
      left: -28px;
      top: 190px;
      width: 150px;
      height: 118px;
      display: grid;
      place-items: center;
      transform: rotate(-12deg);
      z-index: 2;
    }}
    .play::before {{
      content: "";
      position: absolute;
      inset: 0;
      background: #fff0a8;
      border: 4px solid #1c1715;
      clip-path: polygon(50% 0, 61% 20%, 84% 10%, 80% 34%, 100% 50%, 80% 66%, 84% 90%, 61% 80%, 50% 100%, 39% 80%, 16% 90%, 20% 66%, 0 50%, 20% 34%, 16% 10%, 39% 20%);
    }}
    .play span {{
      position: relative;
      font-size: 34px;
      font-weight: 900;
    }}
    .side {{
      position: absolute;
      right: 18px;
      top: 280px;
      writing-mode: vertical-rl;
      font-family: "Times New Roman", serif;
      font-size: 18px;
      letter-spacing: 5px;
    }}
    .card {{
      position: relative;
      margin: 34px 18px 0;
      padding: 26px 30px;
      min-height: 172px;
      background: #fff;
      border: 7px solid #211511;
      box-shadow: 14px 14px 0 #211511;
      line-height: 1.65;
      font-size: 25px;
    }}
    .card h2 {{
      margin: 0 0 12px;
      font-size: 28px;
      line-height: 1.2;
      color: #111;
    }}
    .card p {{
      margin: 0;
    }}
    .accent {{
      color: #f0a13b;
      font-weight: 800;
    }}
    .detail-line {{
      display: grid;
      grid-template-columns: 128px minmax(0, 1fr);
      gap: 0;
      margin: 7px 0;
    }}
    .detail-key {{
      font-weight: 800;
      white-space: nowrap;
    }}
    .detail-value {{
      min-width: 0;
      word-break: keep-all;
      overflow-wrap: break-word;
    }}
    .qr-card {{
      min-height: 390px;
      display: grid;
      grid-template-columns: 1fr 230px;
      gap: 22px;
      align-items: center;
    }}
    .qr-box {{
      width: 230px;
      height: 230px;
      border: 3px dashed #d8d8d8;
      border-radius: 12px;
      display: grid;
      place-items: center;
      color: #9a9a9a;
      text-align: center;
      font-size: 22px;
      background: #fafafa;
      overflow: hidden;
    }}
    .qr-box img {{
      width: 100%;
      height: 100%;
      object-fit: contain;
      background: #fff;
    }}
    .eyes {{
      position: absolute;
      right: -18px;
      top: -60px;
      width: 210px;
      height: 120px;
    }}
    .eye {{
      position: absolute;
      width: 88px;
      height: 118px;
      border: 4px solid #111;
      border-radius: 56% 56% 48% 48%;
      background: #fff;
      transform: rotate(-18deg);
    }}
    .eye::after {{
      content: "";
      position: absolute;
      left: 26px;
      top: 54px;
      width: 42px;
      height: 46px;
      border-radius: 50%;
      background: #201612;
    }}
    .eye:nth-child(2) {{ left: 62px; top: -10px; }}
    .eye:nth-child(3) {{ left: 120px; top: 0; }}
    .sticker {{
      position: absolute;
      right: -10px;
      top: -28px;
      padding: 8px 20px;
      border-radius: 50%;
      background: #fff9e7;
      font-size: 22px;
      font-weight: 900;
      transform: rotate(12deg);
    }}
    .footer {{
      margin-top: 54px;
      text-align: center;
      font-family: "Times New Roman", serif;
      font-size: 22px;
      letter-spacing: 7px;
    }}
  </style>
</head>
<body>
  <main class="poster">
    <div class="spark-row"><span></span><span></span><span></span><span></span></div>
    <section class="hero">
      <div class="title">玩家招募</div>
      <div class="subtitle">GameRecruitment</div>
      <div class="hero-badge">招</div>
    </section>
    <div class="play"><span>PLAY</span></div>
    <div class="side">GAME TESTING RECRUITMENT</div>

    <section class="card">
      <h2>玩家要求</h2>
      <p>{requirement_html}</p>
    </section>

    <section class="card">
      <div class="eyes"><div class="eye"></div><div class="eye"></div><div class="eye"></div></div>
      <h2>活动详情</h2>
      <div class="detail-line"><span class="detail-key">活动时间</span><span class="detail-value">{poster_date_html}</span></div>
      <div class="detail-line"><span class="detail-key">测试时长</span><span class="detail-value">{duration_html}</span></div>
      <div class="detail-line"><span class="detail-key">活动城市</span><span class="detail-value">{city}</span></div>
    </section>

    <section class="card">
      <h2>活动内容</h2>
      <p>{activity_html}</p>
    </section>

    <section class="card">
      <div class="sticker">游戏世界任你闯荡</div>
      <h2>活动礼金</h2>
      <p><span class="accent">{reward_html}</span></p>
    </section>

    <section class="card qr-card">
      <div>
        <h2>报名链接</h2>
        <p>扫码填写报名问卷，报名后等待工作人员联系。</p>
      </div>
      {signup_qr_html}
    </section>

    <section class="card qr-card">
      <div>
        <h2>玩家社群</h2>
        <p>更多活动信息会同步在社群，欢迎扫码加入。</p>
      </div>
      {community_qr_html}
    </section>

    <section class="card">
      <h2>注意事项</h2>
      <p>请如实填写报名信息；若存在个人信息或游戏经历作假、入选后无故缺席等情况，将影响后续活动参与。</p>
    </section>

    <div class="footer">GAME TESTING RECRUITMENT</div>
  </main>
</body>
</html>"""

    def _format_requirement(self, value: str) -> str:
        lines = [line.strip() for line in value.splitlines() if line.strip()]
        html_lines = []
        for index, line in enumerate(lines):
            escaped = html.escape(line)
            match = re.match(r"^([^:：]+)([:：])(.*)$", line)
            numbered = re.match(r"^(\d+[、.．]\s*[^，,；;。]*)(.*)$", line)
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

    def _qr_html(self, data_url: str | None, label: str) -> str:
        if data_url:
            return f'<div class="qr-box"><img src="{data_url}" alt="{html.escape(label)}"></div>'
        return f'<div class="qr-box">请上传<br>{html.escape(label)}</div>'

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
