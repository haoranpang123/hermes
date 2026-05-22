"""自定义异常类"""


class AppException(Exception):
    """应用基础异常"""

    def __init__(self, code: int, message: str, data: dict | None = None):
        self.code = code
        self.message = message
        self.data = data or {}
        super().__init__(message)


class UnauthorizedError(AppException):
    """未登录 (code=1002)"""

    def __init__(self, message: str = "请先登录"):
        super().__init__(code=1002, message=message)


class ForbiddenError(AppException):
    """无权限 (code=1003)"""

    def __init__(self, message: str = "无权限访问"):
        super().__init__(code=1003, message=message)


class NotFoundError(AppException):
    """资源不存在 (code=1004)"""

    def __init__(self, message: str = "资源不存在"):
        super().__init__(code=1004, message=message)


class BusinessError(AppException):
    """业务规则限制 (code=1005)"""

    def __init__(self, message: str, data: dict | None = None):
        super().__init__(code=1005, message=message, data=data)


class ValidationError(AppException):
    """参数错误 (code=1001)"""

    def __init__(self, message: str = "参数错误"):
        super().__init__(code=1001, message=message)


class WechatAPIError(AppException):
    """微信接口错误 (code=2001)"""

    def __init__(self, message: str = "微信接口错误"):
        super().__init__(code=2001, message=message)
