import { create } from 'zustand';
import axios from 'axios';

/**
 * チャット機能のためのZustandストア
 */

// Zustandストアの作成
export const useChatStore = create((set, get) => ({
  // 状態
  messages: [],
  isLoading: false,
  error: null,
  
  // アクション
  addMessage: (message) => set((state) => ({ 
    messages: [message, ...state.messages] 
  })),

  addMessages: (newMessages) => set((state) => ({ 
    messages: [...newMessages, ...state.messages] 
  })),

  setLoading: (loading) => set({ isLoading: loading }),

  setError: (error) => set({ error }),

  sendMessage: async (userMessage) => {
    const { addMessage, setLoading, setError } = get();
    
    try {
      setLoading(true);
      setError(null);

      // ユーザーメッセージを即座に追加
      const userMsg = {
        _id: Math.random().toString(36).substr(2, 9),
        text: userMessage,
        createdAt: new Date(),
        user: {
          _id: 1,
          name: 'User',
        },
      };
      addMessage(userMsg);

      // バックエンドAPIを呼び出し
      const apiBaseUrl = process.env.API_SERVER_HOST;
      const response = await axios.post(`${apiBaseUrl}/api/chat`, {
        message: userMessage
      });

      // AIレスポンスメッセージを追加
      const aiMsg = {
        _id: Math.random().toString(36).substr(2, 9),
        text: response.data.response,
        createdAt: new Date(),
        user: {
          _id: 2,
          name: 'ChatBot',
        },
      };
      addMessage(aiMsg);

    } catch (error) {
      console.error('メッセージ送信エラー:', error);
      setError('メッセージの送信に失敗しました');
      
      // エラーメッセージを追加
      const errorMsg = {
        _id: Math.random().toString(36).substr(2, 9),
        text: 'すみません、エラーが発生しました。もう一度お試しください。',
        createdAt: new Date(),
        user: {
          _id: 2,
          name: 'ChatBot',
        },
      };
      addMessage(errorMsg);
    } finally {
      setLoading(false);
    }
  },

  clearMessages: () => set({ 
    messages: [], 
    error: null 
  }),
}));