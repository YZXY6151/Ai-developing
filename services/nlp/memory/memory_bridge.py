from datetime import datetime
from services.nlp.db.memory_db import store_short_term_memory
from services.nlp.utils.memory_logger import log_memory_event


def write_memory_from_dialog(session_id: str, user_input: str, ai_response: str, important: bool = False):
    """
    将一轮对话（用户输入+AI回复）写入短期记忆。
    可用于自动记忆或未来扩展为智能评估。
    """

    if not user_input.strip() and not ai_response.strip():
        log_memory_event("SKIP_WRITE_MEMORY", session_id=session_id, detail="空输入和回复，跳过")
        return

    # 保存用户输入
    if user_input.strip():
        store_short_term_memory(session_id, content=user_input.strip(), important=important)
    
    # 保存 AI 回复
    if ai_response.strip():
        store_short_term_memory(session_id, content=ai_response.strip(), important=important)

    log_memory_event("AUTO_WRITE_MEMORY", session_id=session_id, detail=f"保存用户输入 + AI 回复，重要: {important}")
