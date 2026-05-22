"""微信 API 封装 — 登录 / 手机号解密 (MVP 阶段简化实现)"""

import httpx
from app.config import get_settings

settings = get_settings()

WX_CODE2SESSION_URL = "https://api.weixin.qq.com/sns/jscode2session"


class WechatAPI:
    """微信小程序 API 客户端"""

    def __init__(self):
        self.app_id = settings.WX_APP_ID
        self.app_secret = settings.WX_APP_SECRET

    async def code2session(self, code: str) -> dict:
        """用 code 换取 openid 和 session_key"""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                WX_CODE2SESSION_URL,
                params={
                    "appid": self.app_id,
                    "secret": self.app_secret,
                    "js_code": code,
                    "grant_type": "authorization_code",
                },
                timeout=10,
            )
            data = resp.json()

            if errcode := data.get("errcode", 0):
                raise ValueError(f"wechat code2session error: [{errcode}] {data.get('errmsg', '')}")

            return {
                "openid": data["openid"],
                "session_key": data.get("session_key", ""),
                "unionid": data.get("unionid"),
            }
