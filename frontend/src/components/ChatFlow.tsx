// frontend/src/components/ChatFlow.tsx

import React, { useState, useEffect } from 'react';
import { chatWithSession, synthesizeSpeech, createSessionWithPersona } from '../services/api';

type Status = 'idle' | 'processing';
type Persona = 'gentle' | 'tsundere' | 'energetic' | 'cool';

const personaMap: Record<Persona, string> = {
  gentle: '温柔主播',
  tsundere: '傲娇主播',
  energetic: '活泼主播',
  cool: '冷静主播',
};

interface MetaData {
  important: boolean;
  timestamp: number;
  persona: string;
  used_memory: boolean;
  memory_ids: string[];
  memory_summary?: string;
}

interface ChatResponse {
  reply: string;
  meta?: MetaData;
}

export const ChatFlow: React.FC = () => {
  const [status, setStatus] = useState<Status>('idle');
  const [input, setInput] = useState('');
  const [message, setMessage] = useState('');
  const [reply, setReply] = useState('');
  const [error, setError] = useState('');
  const [persona, setPersona] = useState<Persona>(() => localStorage.getItem('persona') as Persona || 'gentle');
  const [sessionId, setSessionId] = useState<string>('');
  const [meta, setMeta] = useState<MetaData | null>(null);

  const sendText = async () => {
    const text = input.trim();
    if (!text || !sessionId) return;

    setStatus('processing');
    setMessage(text);
    setInput('');
    setError('');

    try {
      const { reply, meta }: ChatResponse = await chatWithSession(sessionId, text);
      setReply(reply);
      setMeta(meta || null);
      console.log('🧠 Meta:', meta);

      if (meta?.used_memory) {
        console.log('📌 使用的记忆:', meta.memory_summary);
      }

      const blob = await synthesizeSpeech(reply);
      const url = URL.createObjectURL(blob);
      const audio = new Audio(url);
      audio.onended = () => URL.revokeObjectURL(url);
      audio.play();
    } catch (err: any) {
      setError(err.message || '未知错误');
    } finally {
      setStatus('idle');
    }
  };

  useEffect(() => {
    const cached = localStorage.getItem('session_id');
    if (cached) {
      setSessionId(cached);
    } else {
      createSessionWithPersona(persona)
        .then(id => {
          setSessionId(id);
          localStorage.setItem('session_id', id);
        })
        .catch(err => {
          console.error('❌ 创建 session 失败:', err);
          setError('会话创建失败，请重试');
        });
    }
  }, [persona]);

  return (
    <div className="p-4 space-y-4">
      {/* persona 选择 */}
      <div className="flex gap-2 items-center">
        <label>角色：</label>
        <select
          className="border rounded px-2 py-1"
          value={persona}
          onChange={e => {
            const newPersona = e.target.value as Persona;
            setPersona(newPersona);
            localStorage.setItem('persona', newPersona);
            setReply('');
            setMessage('');
            setInput('');
            setError('');
            setSessionId('');
            localStorage.removeItem('session_id');

            // ✅ 立即创建新的 session，并绑定对应 persona
            createSessionWithPersona(newPersona)
              .then(id => {
                setSessionId(id);
                localStorage.setItem('session_id', id);
              })
              .catch(err => {
                console.error('❌ 创建新 persona 的 session 失败:', err);
                setError('角色切换失败，请重试');
              });
          }}
          disabled={status === 'processing'}
        >
          {Object.entries(personaMap).map(([key, label]) => (
            <option key={key} value={key}>
              {label}
            </option>
          ))}
        </select>
      </div>

      {/* 输入区 */}
      <div className="flex gap-2">
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && sendText()}
          className="flex-1 border rounded px-2"
          placeholder="输入文字后回车或点击发送"
          disabled={status === 'processing'}
        />
        <button
          onClick={sendText}
          disabled={!input.trim() || status === 'processing'}
          className="px-4 py-1 bg-blue-600 text-white rounded"
        >
          发送
        </button>
      </div>

      {/* 展示区 */}
      {error && <p className="text-red-600">{error}</p>}

      {message && (
        <div className="border p-2 rounded space-y-2">
          <p><strong>你：</strong>{message}</p>
          <p><strong>主播：</strong>{reply}</p>
          {/* {meta && (
            <div className="text-sm text-gray-400 mt-1 border-t pt-2">
              <p>🧠 当前人格：<strong>{personaMap[meta.persona as Persona] || meta.persona}</strong></p>
              <p>🗂️ 是否使用记忆：{meta.used_memory ? "✅ 是" : "❌ 否"}</p>
              {meta.used_memory && meta.memory_summary && (
                <p>📝 引用记忆摘要：{meta.memory_summary}</p>
              )}
            </div>
          )} */}

        </div>
      )}
    </div>
  );
};
