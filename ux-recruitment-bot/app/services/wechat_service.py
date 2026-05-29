# app/services/wechat_service.py
import logging
import time
import httpx
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)


class WechatService:
    """微信公众号服务：封面上传 + 草稿推送"""

    _access_token: Optional[str] = None
    _token_expires_at: float = 0.0

    TOKEN_URL  = "https://api.weixin.qq.com/cgi-bin/token"
    UPLOAD_URL = "https://api.weixin.qq.com/cgi-bin/material/add_material"
    UPLOAD_ARTICLE_IMAGE_URL = "https://api.weixin.qq.com/cgi-bin/media/uploadimg"
    DRAFT_URL  = "https://api.weixin.qq.com/cgi-bin/draft/add"

    # ---------- Access Token ----------
    async def _get_access_token(self) -> str:
        """获取 access_token，提前 5 分钟自动刷新"""
        if self._access_token and time.time() < self._token_expires_at - 300:
            return self._access_token

        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                self.TOKEN_URL,
                params={
                    "grant_type": "client_credential",
                    "appid":  settings.wechat_app_id,      # ✅ 对齐字段名
                    "secret": settings.wechat_app_secret,  # ✅ 对齐字段名
                },
            )
            resp.raise_for_status()
            data = resp.json()

        if "errcode" in data and data["errcode"] != 0:
            raise RuntimeError(
                f"获取 access_token 失败：{data.get('errmsg')}（errcode={data.get('errcode')}）"
            )

        self._access_token = data["access_token"]
        self._token_expires_at = time.time() + data["expires_in"]
        logger.info("access_token 刷新成功")
        return self._access_token

    # ---------- 上传封面图 ----------
    async def _upload_cover_image(
        self,
        access_token: str,
        image_bytes: bytes,
        filename: str,
    ) -> str:
        """上传永久图文素材，返回 media_id"""
        suffix = filename.lower().rsplit(".", 1)[-1]
        mime_map = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png"}
        content_type = mime_map.get(suffix, "image/jpeg")

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                self.UPLOAD_URL,
                params={"access_token": access_token, "type": "image"},
                files={"media": (filename, image_bytes, content_type)},
            )
            resp.raise_for_status()
            data = resp.json()

        if "errcode" in data and data["errcode"] != 0:
            raise RuntimeError(
                f"封面图上传失败：{data.get('errmsg')}（errcode={data.get('errcode')}）"
            )

        media_id: str = data["media_id"]
        logger.info(f"封面图上传成功，media_id={media_id}")
        return media_id

    async def _upload_article_image(
        self,
        access_token: str,
        image_bytes: bytes,
        filename: str,
    ) -> str:
        """上传图文正文图片，返回可插入 content 的图片 URL"""
        suffix = filename.lower().rsplit(".", 1)[-1]
        mime_map = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png"}
        content_type = mime_map.get(suffix, "image/jpeg")

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                self.UPLOAD_ARTICLE_IMAGE_URL,
                params={"access_token": access_token},
                files={"media": (filename, image_bytes, content_type)},
            )
            resp.raise_for_status()
            data = resp.json()

        if "errcode" in data and data["errcode"] != 0:
            raise RuntimeError(
                f"正文图片上传失败：{data.get('errmsg')}（errcode={data.get('errcode')}）"
            )

        image_url: str = data["url"]
        logger.info("正文图片上传成功")
        return image_url

    # ---------- 推送草稿 ----------
    async def _create_draft(
        self,
        access_token: str,
        title: str,
        digest: str,
        content_html: str,
        thumb_media_id: str,
    ) -> str:
        """调用草稿箱接口，返回草稿 media_id"""
        payload = {
            "articles": [
                {
                    "title": title,
                    "author": settings.wechat_author,      # ✅ 对齐字段名
                    "digest": digest,
                    "content": content_html,
                    "thumb_media_id": thumb_media_id,
                    "need_open_comment": 0,
                    "only_fans_can_comment": 0,
                }
            ]
        }

        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                self.DRAFT_URL,
                params={"access_token": access_token},
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()

        if "errcode" in data and data["errcode"] != 0:
            raise RuntimeError(
                f"草稿推送失败：{data.get('errmsg')}（errcode={data.get('errcode')}）"
            )

        draft_id: str = data["media_id"]
        logger.info(f"草稿推送成功，draft_id={draft_id}")
        return draft_id

    # ---------- 对外接口 ----------
    async def push_to_draft(
        self,
        title: str,
        digest: str,
        content_html: str,
        image_bytes: bytes,
        filename: str,
    ) -> str:
        """获取 Token → 上传封面 → 推送草稿，返回草稿 media_id"""
        try:
            access_token    = await self._get_access_token()
            thumb_media_id  = await self._upload_cover_image(access_token, image_bytes, filename)
            draft_id        = await self._create_draft(
                access_token, title, digest, content_html, thumb_media_id
            )
            return draft_id
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"HTTP 请求错误：{e.response.status_code} - {e.response.text}")
        except httpx.TimeoutException:
            raise RuntimeError("请求微信 API 超时，请检查网络或稍后重试")

    async def push_image_article_to_draft(
        self,
        title: str,
        digest: str,
        cover_image_bytes: bytes,
        cover_filename: str,
        body_image_bytes: bytes,
        body_filename: str,
    ) -> str:
        """上传封面 + 上传正文海报图片 + 创建只有图片正文的草稿"""
        try:
            access_token = await self._get_access_token()
            thumb_media_id = await self._upload_cover_image(
                access_token, cover_image_bytes, cover_filename
            )
            body_image_url = await self._upload_article_image(
                access_token, body_image_bytes, body_filename
            )
            content_html = (
                '<p style="text-align:center;margin:0;">'
                f'<img src="{body_image_url}" style="max-width:100%;height:auto;" />'
                "</p>"
            )
            draft_id = await self._create_draft(
                access_token, title, digest, content_html, thumb_media_id
            )
            return draft_id
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"HTTP 请求错误：{e.response.status_code} - {e.response.text}")
        except httpx.TimeoutException:
            raise RuntimeError("请求微信 API 超时，请检查网络或稍后重试")


# 单例实例
wechat_service = WechatService()
