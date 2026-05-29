from pydantic import BaseModel, Field
from typing import Optional


class DemandForm(BaseModel):
    """游戏玩家用研招募需求单"""

    city: str = Field(..., description="活动城市", examples=["杭州"])
    game_category: str = Field(..., description="游戏品类关键词", examples=["SLG"])
    reward_amount: str = Field(..., description="礼金金额", examples=["650元"])
    player_requirement_desc: str = Field(..., description="玩家总体要求描述")
    game_examples: str = Field(..., description="游戏举例，用顿号分隔")
    activity_date: str = Field(..., description="活动时间")
    duration: str = Field(..., description="单次测试时长")
    location: str = Field(..., description="线下地点")
    activity_description: str = Field(
        default="参与一波活动，与工作人员聊聊你的想法",
        description="活动内容简述",
    )
    project_id: str = Field(..., description="项目编号")
    extra_notes: Optional[str] = Field(default=None, description="补充说明（可选）")


class PipelineResult(BaseModel):
    """完整流程结果"""

    success: bool
    title: str = ""
    draft_id: Optional[str] = None 
    message: str


class PreviewResult(BaseModel):
    """文案预览结果，不推送公众号"""

    success: bool
    title: str
    digest: str
    content_html: str
    poster_image_url: Optional[str] = None
    poster_image_path: Optional[str] = None
    cover_image_url: Optional[str] = None
    cover_image_path: Optional[str] = None
    message: str
