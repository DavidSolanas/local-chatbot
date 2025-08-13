from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from backend.app.schemas.chat import ChatRequest
from backend.app.services.llm_service import LLMService

router = APIRouter()
llm = LLMService()

@router.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    def token_generator():
        for token in llm.stream_response(
            message=req.message,
            system_prompt=req.system_prompt,
            max_new_tokens=req.max_new_tokens,
            temperature=req.temperature,
            top_p=req.top_p,
        ):
            yield token
    return StreamingResponse(token_generator(), media_type="text/plain")