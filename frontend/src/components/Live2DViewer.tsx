// frontend/src/components/Live2DViewer.tsx
import React, { useEffect, useRef } from 'react';
import * as PIXI from 'pixi.js';
import { Live2DModel } from 'pixi-live2d-display';

export const Live2DViewer: React.FC = () => {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // 1) 创建 PIXI 应用
    const canvas = document.createElement('canvas');
    const app = new PIXI.Application({
      view: canvas,
      width: 400,
      height: 600,
      backgroundAlpha: 0,
    });
    ref.current?.appendChild(canvas);

    // 2) 加载模型（按文件夹结构加载它引用的所有资源）
    Live2DModel.from('/live2d/hiyori/hiyori_free_t08.model3.json')
      .then(model => {
        model.scale.set(0.3);
        model.position.set(200, 400);
        app.stage.addChild(model);

        // 默认动作
        model.motion('TapBody');

        // 借助 ChatFlow 里发的事件联动
        window.addEventListener('startTalking', () => model.motion('TapBody'));
      })
      .catch(err => console.error('Live2D 加载失败：', err));

    // 3) 卸载时销毁
    return () => app.destroy(true, true);
  }, []);

  return <div ref={ref} style={{ width: 400, height: 600 }} />;
};
