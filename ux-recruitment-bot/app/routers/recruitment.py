import logging
from pathlib import Path
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional
from app.models.demand import DemandForm, PipelineResult, PreviewResult
from app.services.content_service import content_service
from app.services.cover_service import cover_service
from app.services.llm_service import llm_service
from app.services.poster_service import poster_service
from app.services.qr_service import qr_service
from app.services.wechat_service import wechat_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/recruitment", tags=["游戏玩家用研招募"])

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/jpg"}
MAX_IMAGE_SIZE = 2 * 1024 * 1024  # 2MB
GENERATED_STATIC_ROOT = Path(__file__).resolve().parents[1] / "static" / "generated"


@router.post(
    "/generate-preview",
    response_model=PreviewResult,
    summary="生成招募推文预览，不推送公众号",
)
async def generate_recruitment_preview(
    city: str = Form(..., description="活动城市", examples=["杭州"]),
    game_category: str = Form(..., description="游戏品类关键词", examples=["SLG"]),
    reward_amount: str = Form(..., description="礼金金额", examples=["650元"]),
    player_requirement_desc: str = Form(..., description="玩家总体要求描述"),
    game_examples: str = Form(..., description="游戏举例，用顿号分隔"),
    activity_date: str = Form(..., description="活动时间"),
    duration: str = Form(..., description="单次测试时长"),
    location: str = Form(..., description="线下地点"),
    activity_description: str = Form(
        default="参与一波活动，与工作人员聊聊你的想法",
        description="活动内容简述",
    ),
    project_id: str = Form(..., description="项目编号"),
    extra_notes: Optional[str] = Form(default=None, description="补充说明（可选）"),
    use_llm: bool = Form(default=False, description="是否调用 LLM 润色文案"),
    include_poster: bool = Form(default=False, description="是否同时生成海报 PNG"),
    include_cover: bool = Form(default=False, description="是否同时生成横版封面海报"),
    poster_date: Optional[str] = Form(default=None, description="海报顶部展示日期，如 5.19-5.20"),
    cover_deadline: Optional[str] = Form(default=None, description="封面海报上的活动截止日期"),
    cover_title: Optional[str] = Form(default=None, description="封面海报主标题，可换行"),
    signup_link: Optional[str] = Form(default=None, description="报名链接，未上传二维码时自动生成二维码"),
    community_link: Optional[str] = Form(default=None, description="社群链接，未上传二维码时自动生成二维码"),
    signup_qr: Optional[UploadFile] = File(default=None, description="报名二维码 PNG/JPG"),
    community_qr: Optional[UploadFile] = File(default=None, description="社群二维码 PNG/JPG"),
) -> PreviewResult:
    """
    安全预览流程：
    1. 接收需求单
    2. LLM 生成招募推文
    3. 返回标题、摘要和正文 HTML
    """
    form = DemandForm(
        city=city,
        game_category=game_category,
        reward_amount=reward_amount,
        player_requirement_desc=player_requirement_desc,
        game_examples=game_examples,
        activity_date=activity_date,
        duration=duration,
        location=location,
        activity_description=activity_description,
        project_id=project_id,
        extra_notes=extra_notes,
    )

    try:
        if use_llm:
            logger.info("Preview: LLM 润色招募内容...")
            content = await llm_service.generate_recruitment_content(form)
        else:
            logger.info("Preview: 模板生成招募内容...")
            content = content_service.generate_recruitment_content(form)
        poster_result = None
        cover_result = None
        if include_poster:
            logger.info("Preview: 渲染招募海报...")
            signup_qr_bytes = await _read_optional_image(signup_qr, "报名二维码")
            community_qr_bytes = await _read_optional_image(community_qr, "社群二维码")
            signup_qr_content_type = signup_qr.content_type if signup_qr_bytes and signup_qr else None
            community_qr_content_type = (
                community_qr.content_type if community_qr_bytes and community_qr else None
            )

            if signup_qr_bytes is None:
                signup_qr_bytes = qr_service.generate_png(signup_link)
                signup_qr_content_type = "image/png" if signup_qr_bytes else None
            if community_qr_bytes is None:
                community_qr_bytes = qr_service.generate_png(community_link)
                community_qr_content_type = "image/png" if community_qr_bytes else None

            poster_result = await poster_service.render_recruitment_poster(
                form=form,
                poster_date=poster_date,
                signup_qr=signup_qr_bytes,
                signup_qr_content_type=signup_qr_content_type,
                community_qr=community_qr_bytes,
                community_qr_content_type=community_qr_content_type,
            )
        if include_cover:
            logger.info("Preview: 渲染封面海报...")
            cover_result = await cover_service.render_cover(
                form=form,
                deadline=cover_deadline,
                cover_title=cover_title,
            )

        return PreviewResult(
            success=True,
            title=content["title"],
            digest=content["digest"],
            content_html=content["content_html"],
            poster_image_url=poster_result["url"] if poster_result else None,
            poster_image_path=poster_result["path"] if poster_result else None,
            cover_image_url=cover_result["url"] if cover_result else None,
            cover_image_path=cover_result["path"] if cover_result else None,
            message="预览生成成功，尚未推送到公众号草稿箱。",
        )
    except RuntimeError as e:
        logger.error(f"预览生成失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def _read_optional_image(file: Optional[UploadFile], label: str) -> Optional[bytes]:
    if file is None or not file.filename:
        return None
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"{label}格式不支持：{file.content_type}，请上传 JPG 或 PNG",
        )
    image_bytes = await file.read()
    if len(image_bytes) == 0:
        return None
    if len(image_bytes) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"{label}超过 2MB 限制（当前：{len(image_bytes) / 1024 / 1024:.1f}MB）",
        )
    return image_bytes


@router.post(
    "/publish-preview-draft",
    response_model=PipelineResult,
    summary="将当前预览内容推送到公众号草稿箱",
)
async def publish_preview_draft(
    title: str = Form(..., description="文章标题"),
    digest: str = Form(..., description="文章摘要"),
    content_html: str = Form(..., description="公众号正文 HTML"),
    cover_image_path: str = Form(..., description="本次生成的封面图本地路径"),
    poster_image_path: Optional[str] = Form(default=None, description="本次生成的长海报本地路径"),
) -> PipelineResult:
    """
    将工作台当前预览结果推送为公众号草稿。
    只创建草稿，不直接发布。
    """
    try:
        cover_path = _resolve_generated_file(cover_image_path)
        poster_path = _resolve_generated_file(poster_image_path or cover_image_path)

        cover_image_bytes = cover_path.read_bytes()
        body_image_bytes = poster_path.read_bytes()
        if len(cover_image_bytes) == 0:
            raise HTTPException(status_code=400, detail="封面图文件为空")
        if len(body_image_bytes) == 0:
            raise HTTPException(status_code=400, detail="正文海报文件为空")

        draft_id = await wechat_service.push_image_article_to_draft(
            title=title,
            digest=digest,
            cover_image_bytes=cover_image_bytes,
            cover_filename=cover_path.name,
            body_image_bytes=body_image_bytes,
            body_filename=poster_path.name,
        )

        return PipelineResult(
            success=True,
            title=title,
            draft_id=draft_id,
            message="草稿已成功推送到公众号草稿箱。",
        )
    except HTTPException:
        raise
    except RuntimeError as e:
        logger.error(f"草稿推送失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _resolve_generated_file(file_path: str) -> Path:
    root = GENERATED_STATIC_ROOT.resolve()
    candidate = Path(file_path).resolve()
    if root not in candidate.parents:
        raise HTTPException(status_code=400, detail="封面图路径不在允许的生成目录内")
    if not candidate.exists() or not candidate.is_file():
        raise HTTPException(status_code=404, detail="找不到封面图文件")
    return candidate


@router.post(
    "/publish-draft",
    response_model=PipelineResult,
    summary="一键生成招募推文并推送至微信草稿箱",
)
async def publish_recruitment_draft(
    # ── 需求单字段 ──
    city: str = Form(..., description="活动城市", examples=["杭州"]),
    game_category: str = Form(..., description="游戏品类关键词", examples=["SLG"]),
    reward_amount: str = Form(..., description="礼金金额", examples=["650元"]),
    player_requirement_desc: str = Form(..., description="玩家总体要求描述"),
    game_examples: str = Form(..., description="游戏举例，用顿号分隔"),
    activity_date: str = Form(..., description="活动时间"),
    duration: str = Form(..., description="单次测试时长"),
    location: str = Form(..., description="线下地点"),
    activity_description: str = Form(
        default="参与一波活动，与工作人员聊聊你的想法",
        description="活动内容简述",
    ),
    project_id: str = Form(..., description="项目编号"),
    extra_notes: Optional[str] = Form(default=None, description="补充说明（可选）"),
    # ── 封面图 ──
    cover_image: UploadFile = File(..., description="从 Canva 导出的封面图 JPG/PNG"),
) -> PipelineResult:
    """
    完整流程：
    1. 接收需求单 + 封面图
    2. LLM 生成招募推文
    3. 上传封面到微信素材库
    4. 推送到草稿箱
    """
    # ── 校验封面图 ──
    if cover_image.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"封面图格式不支持：{cover_image.content_type}，请上传 JPG 或 PNG",
        )

    image_bytes = await cover_image.read()

    if len(image_bytes) == 0:
        raise HTTPException(status_code=400, detail="封面图文件为空")

    if len(image_bytes) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"封面图超过 2MB 限制（当前：{len(image_bytes) / 1024 / 1024:.1f}MB）",
        )

    # ── 组装需求单 ──
    form = DemandForm(
        city=city,
        game_category=game_category,
        reward_amount=reward_amount,
        player_requirement_desc=player_requirement_desc,
        game_examples=game_examples,
        activity_date=activity_date,
        duration=duration,
        location=location,
        activity_description=activity_description,
        project_id=project_id,
        extra_notes=extra_notes,
    )

    try:
        # Step 1: LLM 生成推文内容
        logger.info("Step 1: LLM 生成招募内容...")
        content = await llm_service.generate_recruitment_content(form)

        # Step 2: 上传封面 + 推送草稿
        logger.info("Step 2: 上传封面并推送到草稿箱...")
        draft_id = await wechat_service.push_to_draft(
            title=content["title"],
            digest=content["digest"],
            content_html=content["content_html"],
            image_bytes=image_bytes,
            filename=cover_image.filename or "cover.jpg",
        )

        return PipelineResult(
            success=True,
            title=content["title"],
            draft_id=draft_id,
            message="🎉 草稿已成功推送到公众号草稿箱，请登录公众号后台审核发布！",
        )

    except RuntimeError as e:
        logger.error(f"流程失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
