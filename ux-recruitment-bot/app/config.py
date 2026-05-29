# app/config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # AI（硅基流动 / OpenAI 兼容）
    openai_api_key: str
    openai_base_url: str = "https://api.siliconflow.cn/v1"
    model_name: str = "Qwen/Qwen2.5-7B-Instruct"

    # 微信公众号
    wechat_app_id: str
    wechat_app_secret: str
    wechat_author: str = "网易游戏用户体验中心"   

    class Config:
        env_file = ".env"


settings = Settings()