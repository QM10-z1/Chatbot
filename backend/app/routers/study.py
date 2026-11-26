from fastapi import APIRouter, HTTPException
from app.llm import call_model
from app.schemas.study import StudyRequest

router = APIRouter(tags=["Study"])


STUDY_SYSTEM_PROMPT = (
    "你是一位专业的英语老师。请指出用户提供的英文中的语法或用词问题，"
    "并给出修改建议。请用中文简要回答，格式清晰。"
)

@router.post("/study/correct")
def study_correct(req: StudyRequest):
    if not req.text or req.text.strip() == "":
        raise HTTPException(status_code=400, detail="text 不能为空")
    messages = [
        {"role": "system", "content": STUDY_SYSTEM_PROMPT},
        {"role": "user", "content": req.text},
    ]
    feedback = call_model(messages)
    return {"original": req.text, "feedback": feedback}