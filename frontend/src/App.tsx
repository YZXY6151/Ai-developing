// frontend/src/App.tsx
import React from 'react';
import { ChatFlow } from './components/ChatFlow';
import './App.css';

interface ErrorBoundaryState {
  hasError: boolean;
  errorInfo?: string;
}

export class ErrorBoundary extends React.Component<React.PropsWithChildren<{}>, ErrorBoundaryState> {
  state: ErrorBoundaryState = { hasError: false };

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, errorInfo: error.message };
  }


  componentDidCatch(error: Error, info: React.ErrorInfo) {
    console.error('ErrorBoundary 捕获到错误:', error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex items-center justify-center h-screen bg-gray-100 p-4">
          <div className="bg-white p-6 rounded-lg shadow-md text-red-600">
            <h1 className="text-2xl mb-2">很抱歉，出现了错误。</h1>
            <p>错误信息：{this.state.errorInfo}</p>
          </div>
        </div>
      );
    }
    return <>{this.props.children}</>;
  }
}

export default function App() {
  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">
        <header className="mb-6">
          <h1 className="text-3xl font-bold">AI 虚拟主播演示</h1>
        </header>
        <main className="w-full max-w-5xl">
          <ChatFlow />
        </main>
      </div>
    </ErrorBoundary>
  );
}
