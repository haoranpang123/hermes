"""消息发布/订阅 — 简单的进程内事件总线 (MVP 阶段)"""

import asyncio
from collections import defaultdict
from typing import Callable, Awaitable

_handlers: dict[str, list[Callable[..., Awaitable[None]]]] = defaultdict(list)


def subscribe(event: str, handler: Callable[..., Awaitable[None]]):
    """订阅事件"""
    _handlers[event].append(handler)


async def publish(event: str, **kwargs):
    """发布事件"""
    for handler in _handlers.get(event, []):
        try:
            await handler(**kwargs)
        except Exception:
            pass  # MVP: 静默处理异常，P1 加日志
