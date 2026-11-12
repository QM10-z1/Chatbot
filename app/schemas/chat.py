from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    """普通对话与流式对话共用的请求体。"""
    session_id: str = Field(..., description="会话 ID,首次使用会自动创建")
    message: str = Field(..., description="用户消息，不能为空")

class ChatResponse(BaseModel):
    """普通对话接口的响应体。"""
    session_id: str = Field(..., description="会话 ID")
    reply: str = Field(..., description="模型返回的完整回复")