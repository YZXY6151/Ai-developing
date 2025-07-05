// frontend/src/services/api.ts

const ASR_BASE = import.meta.env.VITE_ASR_URL || 'http://localhost:8181';
const NLP_BASE = import.meta.env.VITE_NLP_URL || 'http://localhost:8182';
const TTS_BASE = import.meta.env.VITE_TTS_URL || 'http://localhost:8183';
const TIMEOUT_MS = 30_000;


interface ChatResponse {
  reply: string;
  meta?: {
    important: boolean;
    timestamp: number;
    persona: string;
    used_memory: boolean;
    memory_ids: string[];
  };
}


async function fetchWithTimeout(input: RequestInfo, init?: RequestInit): Promise<Response> {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), TIMEOUT_MS);
  try {
    const res = await fetch(input, { signal: controller.signal, ...init });
    return res;
  } finally {
    clearTimeout(id);
  }
}

/** 1. 语音识别（ASR） */
export async function recognizeAudio(file: File): Promise<{ transcription: string; language: string }> {
  const form = new FormData();
  form.append('file', file);

  const res = await fetchWithTimeout(`${ASR_BASE}/api/asr/recognize`, {
    method: 'POST',
    body: form,
  });
  if (!res.ok) {
    throw new Error(`ASR 请求失败：${res.status} ${res.statusText}`);
  }
  try {
    return await res.json();
  } catch {
    throw new Error('ASR 返回解析错误，非有效 JSON');
  }
}

/** 2. GPT 对话（NLP + session） */
export async function chatWithSession(session_id: string, user_input: string): Promise<ChatResponse> {
  const res = await fetch(`${NLP_BASE}/api/nlp/chat_with_session`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id, user_input }),
  });
  if (!res.ok) {
    let err = await res.text();
    throw new Error(`NLP 请求失败：${res.status} - ${err}`);
  }
  const json = await res.json()
  return json
}

/** 3. 语音合成（TTS） */
export async function synthesizeSpeech(text: string): Promise<Blob> {
  const res = await fetchWithTimeout(`${TTS_BASE}/api/tts/synthesize`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Accept': 'audio/mpeg' },
    body: JSON.stringify({ text }),
  });
  if (!res.ok) {
    throw new Error(`TTS 请求失败：${res.status} ${res.statusText}`);
  }
  try {
    return await res.blob();
  } catch {
    throw new Error('TTS 返回解析错误，非有效音频流');
  }
}


export async function createSessionWithPersona(persona_id: string, titlename = "临时会话"): Promise<string> {
  const res = await fetch(`${NLP_BASE}/api/nlp/session/create`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      persona_id,
      titlename,
      user_id: "guest"
    }),
  });
  if (!res.ok) throw new Error('Session 创建失败');
  const data = await res.json();
  return data.session_id;
}
