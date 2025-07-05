// src/components/Recorder.tsx
import React, { useEffect, useRef, useState, useCallback } from 'react';

export interface RecorderProps {
  onRecorded: (file: File) => void;
  /** 是否禁用录音按钮 */
  disabled?: boolean;
  maxDurationSec?: number; // 可选：最大录音时长，单位秒
}

export const Recorder: React.FC<RecorderProps> = ({ onRecorded, maxDurationSec = 60, disabled=false}) => {
  const recorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const [isReady, setIsReady] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [error, setError] = useState<string>('');

  // 停止录音并生成文件
  const handleStop = useCallback(() => {
    if (!recorderRef.current) return;
    const blob = new Blob(chunksRef.current, { type: recorderRef.current.mimeType });
    const file = new File([blob], `speech.${blob.type.split('/')[1]}`, { type: blob.type });
    chunksRef.current = []; // 清空
    onRecorded(file);
  }, [onRecorded]);

  useEffect(() => {
    navigator.mediaDevices.getUserMedia({ audio: true })
      .then(stream => {
        const options = [
          'audio/webm',
          'audio/ogg;codecs=opus',
          'audio/mp4'
        ].find(type => MediaRecorder.isTypeSupported(type)) || '';

        const recorder = new MediaRecorder(stream, options ? { mimeType: options } : undefined);
        recorder.ondataavailable = e => {
          if (e.data.size > 0) chunksRef.current.push(e.data);
        };
        recorder.onstop = handleStop;  // 提前绑定
        recorderRef.current = recorder;
        setIsReady(true);
      })
      .catch(err => {
        console.error('获取麦克风失败', err);
        setError('无法获取麦克风权限');
      });
  }, [handleStop]);

  // 录音定时器
  const timerRef = useRef<number | null>(null);
  const start = () => {
    if (!recorderRef.current) return;
    setError('');
    chunksRef.current = [];
    recorderRef.current.start();
    setIsRecording(true);
    // 启动最长录音时长定时
    if (maxDurationSec > 0) {
      timerRef.current = window.setTimeout(() => {
        if (recorderRef.current && isRecording) {
          recorderRef.current.stop();
          setIsRecording(false);
        }
      }, maxDurationSec * 1000);
    }
  };

  const stop = () => {
    if (!recorderRef.current) return;
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }
    recorderRef.current.stop();
    setIsRecording(false);
  };

  return (
    <div>
      <button
        disabled={!isReady || disabled}
        onMouseDown={start}
        onMouseUp={stop}
        onMouseLeave={() => isRecording && stop()}
        onTouchStart={start}
        onTouchEnd={stop}
        style={{
          padding: '8px 16px',
          background: isRecording ? '#e53e3e' : '#38a169',
          color: 'white',
          borderRadius: '9999px',
          opacity: isReady ? 1 : 0.5,
          cursor: isReady ? 'pointer' : 'not-allowed',
          transition: 'background 0.2s',
        }}
      >
        {isRecording ? '录音中...' : isReady ? '按住说话' : '初始化中...'}
      </button>
      {error && <p style={{ color: 'red', marginTop: '8px' }}>{error}</p>}
    </div>
  );
};
