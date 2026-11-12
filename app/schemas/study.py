from pydantic import BaseModel, Field

class StudyRequest(BaseModel):
    """英语纠错接口的请求体。"""
    text: str = Field(..., description="待检查的英文文本，不能为空")