import re
import time
import base64
from pathlib import Path

from app.models.demand import DemandForm


class PosterService:
    """Render the existing HTML poster tool to a PNG with a headless browser."""

    def __init__(self) -> None:
        app_dir = Path(__file__).resolve().parents[1]
        project_root = app_dir.parent
        workspace_root = project_root.parent

        self.poster_html = (
            workspace_root
            / "poster-generator"
            / "player-recruitment-poster-standalone.html"
        )
        self.output_dir = app_dir / "static" / "generated" / "posters"

    async def render_recruitment_poster(
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
                "Playwright 未安装，无法自动渲染海报。请先运行：pip install playwright && playwright install chromium"
            ) from exc

        if not self.poster_html.exists():
            raise RuntimeError(f"找不到海报 HTML 文件：{self.poster_html}")

        self.output_dir.mkdir(parents=True, exist_ok=True)
        output_name = f"poster-{self._safe_name(form.project_id)}-{int(time.time())}.png"
        output_path = self.output_dir / output_name

        poster_data = {
            "city": form.city,
            "eventDate": poster_date or form.activity_date,
            "playerRequirement": form.player_requirement_desc,
            "activityTime": form.activity_date,
            "testDuration": form.duration,
            "activityLocation": form.location,
            "activityContent": form.activity_description,
            "baseReward": "0",
            "transportSubsidy": "0",
            "rewardAmount": form.reward_amount,
            "signupHint": "欢迎玩家们扫码报名~（报名问卷无礼金）",
            "projectCode": form.project_id,
            "communityText": (
                "这个活动与您的游戏经历不匹配？\n"
                "没关系，我们还有更多有趣的活动信息在社群，欢迎扫码加入！！！"
            ),
        }
        qr_data = {
            "signup": self._to_data_url(signup_qr, signup_qr_content_type),
            "community": self._to_data_url(community_qr, community_qr_content_type),
        }

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                context = await browser.new_context(
                    viewport={"width": 1400, "height": 1800},
                    device_scale_factor=2,
                )
                page = await context.new_page()
                await page.goto(self.poster_html.as_uri(), wait_until="load")
                await page.evaluate(
                    """
                    ({ data, qr }) => {
                        for (const [id, value] of Object.entries(data)) {
                            const el = document.getElementById(id);
                            if (el) {
                                el.value = value;
                            }
                        }
                        if (qr.signup) {
                            signupQRData = qr.signup;
                        }
                        if (qr.community) {
                            communityQRData = qr.community;
                        }
                        if (typeof updatePoster === "function") {
                            updatePoster();
                        }
                        const escapeHtml = (value) => String(value || "")
                            .replaceAll("&", "&amp;")
                            .replaceAll("<", "&lt;")
                            .replaceAll(">", "&gt;")
                            .replaceAll('"', "&quot;")
                            .replaceAll("'", "&#039;");
                        const toLines = (value) => escapeHtml(value).replaceAll("\\n", "<br>");
                        const setMultiline = (id, value) => {
                            const el = document.getElementById(id);
                            if (el) {
                                el.innerHTML = toLines(value);
                            }
                        };
                        const injectSmartLayoutStyle = () => {
                            const style = document.createElement("style");
                            style.textContent = `
                                #playerRequirementContent .requirement-line {
                                    margin-bottom: 6px;
                                }
                                #playerRequirementContent .requirement-label {
                                    display: inline;
                                    font-weight: 700;
                                    color: #2E7D32;
                                }
                                .detail-row {
                                    margin-bottom: 8px;
                                }
                                .detail-grid {
                                    display: grid;
                                    grid-template-columns: max-content minmax(0, 1fr);
                                    column-gap: 4px;
                                    align-items: start;
                                }
                                .detail-key {
                                    color: #666;
                                    font-size: 14px;
                                    font-weight: 600;
                                    white-space: nowrap;
                                    line-height: 1.55;
                                }
                                .detail-grid .detail-value {
                                    color: #333;
                                    font-size: 14px;
                                    line-height: 1.55;
                                    min-width: 0;
                                    word-break: keep-all;
                                    overflow-wrap: break-word;
                                }
                            `;
                            document.head.appendChild(style);
                        };
                        const setRequirements = (value) => {
                            const el = document.getElementById("playerRequirementContent");
                            if (!el) {
                                return;
                            }
                            const lines = String(value || "")
                                .split("\\n")
                                .map((line) => line.trim())
                                .filter(Boolean);
                            el.innerHTML = lines.map((line, index) => {
                                const match = line.match(/^([^:：]+)[:：](.*)$/);
                                if (match) {
                                    return `<div class="requirement-line"><span class="requirement-label">${escapeHtml(match[1])}：</span>${escapeHtml(match[2].trim())}</div>`;
                                }
                                const numberedMatch = line.match(/^(\\d+[、.．]\\s*.*?)([，,]\\s*如[:：]?.*)$/);
                                if (numberedMatch) {
                                    return `<div class="requirement-line"><span class="requirement-label">${escapeHtml(numberedMatch[1])}</span>${escapeHtml(numberedMatch[2])}</div>`;
                                }
                                if (index === 0) {
                                    return `<div class="requirement-line"><span class="requirement-label">${escapeHtml(line)}</span></div>`;
                                }
                                return `<div class="requirement-line">${escapeHtml(line)}</div>`;
                            }).join("");
                        };
                        const setDetail = (id, label, value) => {
                            const el = document.getElementById(id);
                            const row = el ? el.closest(".detail-row") : null;
                            if (!row) {
                                return;
                            }
                            row.innerHTML = `
                                <div class="detail-grid">
                                    <span class="detail-key">${label}</span>
                                    <span class="detail-value" id="${id}">${toLines(value)}</span>
                                </div>
                            `;
                        };
                        injectSmartLayoutStyle();
                        setRequirements(data.playerRequirement);
                        setDetail("activityTimeValue", "【活动时间】", data.activityTime);
                        setDetail("testDurationValue", "【测试时长】", data.testDuration);
                        setDetail("activityLocationValue", "【活动地点】", data.activityLocation);
                        setMultiline("activityContentValue", data.activityContent);
                        setMultiline("rewardAmount", data.rewardAmount);
                        const gamepad = document.querySelector(".deco-gamepad");
                        if (gamepad) {
                            gamepad.style.bottom = "-52px";
                            gamepad.style.right = "-8px";
                            gamepad.style.zIndex = "3";
                        }
                        const player = document.querySelector(".deco-player");
                        if (player) {
                            player.style.top = "50px";
                            player.style.right = "2px";
                            player.style.width = "64px";
                            player.style.height = "64px";
                            player.style.zIndex = "2";
                        }
                    }
                    """,
                    {"data": poster_data, "qr": qr_data},
                )
                await page.locator("#poster").screenshot(path=str(output_path))
                await context.close()
                await browser.close()
        except NotImplementedError as exc:
            raise RuntimeError(
                "Playwright 无法在当前 Windows 事件循环中启动浏览器。请重启后端服务后再试。"
            ) from exc
        except Exception as exc:
            raise RuntimeError(f"海报渲染失败：{exc}") from exc

        return {
            "path": str(output_path),
            "url": f"/static/generated/posters/{output_name}",
        }

    def _safe_name(self, value: str) -> str:
        safe = re.sub(r"[^a-zA-Z0-9_-]+", "-", value).strip("-")
        return safe or "poster"

    def _to_data_url(self, image: bytes | None, content_type: str | None) -> str | None:
        if not image:
            return None
        mime = content_type or "image/png"
        encoded = base64.b64encode(image).decode("ascii")
        return f"data:{mime};base64,{encoded}"


poster_service = PosterService()
