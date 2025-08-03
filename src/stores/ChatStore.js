import { create } from 'zustand';
import axios from 'axios';

/**
 * チャット機能のためのZustandストア
 * react-native-paper用にシンプル化されたメッセージ形式
 */

// Zustandストアの作成
export const useChatStore = create((set, get) => ({
  // 状態
  messages: [],
  isLoading: false,
  error: null,
  
  // アクション
  addMessage: (message) => set((state) => ({ 
    messages: [...state.messages, message] 
  })),

  addMessages: (newMessages) => set((state) => ({ 
    messages: [...state.messages, ...newMessages] 
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
        id: Math.random().toString(36).substr(2, 9),
        text: userMessage,
        timestamp: new Date(),
        isUser: true,
      };
      addMessage(userMsg);

      // バックエンドAPIを呼び出し
      const apiBaseUrl = process.env.API_SERVER_HOST || '';
      const response = await axios.post(`${apiBaseUrl}/api/chat`, {
        message: userMessage
      });

      // AIレスポンスメッセージを追加
      const aiMsg = {
        id: Math.random().toString(36).substr(2, 9),
        text: response.data.response,
        timestamp: new Date(),
        isUser: false,
      };
      addMessage(aiMsg);

    } catch (error) {
      console.error('メッセージ送信エラー:', error);
      setError('メッセージの送信に失敗しました');
      
      // エラーメッセージを追加
      const errorMsg = {
        id: Math.random().toString(36).substr(2, 9),
        text: 'すみません、エラーが発生しました。もう一度お試しください。',
        timestamp: new Date(),
        isUser: false,
        isError: true,
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