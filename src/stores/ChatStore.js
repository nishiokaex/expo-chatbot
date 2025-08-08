import { create } from 'zustand';
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

/**
 * チャット機能のためのZustandストア
 * react-native-paper用にシンプル化されたメッセージ形式
 */

// AsyncStorageのキー
const URL_STORAGE_KEY = 'chatbot_url';

// Zustandストアの作成
export const useChatStore = create((set, get) => ({
  // 状態
  messages: [],
  isLoading: false,
  error: null,
  currentUrl: null,
  vectorStoreStatus: {
    initialized: false,
    current_url: null,
    status: 'not_initialized'
  },
  
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
    const { addMessage, setLoading, setError, ensureVectorStoreReady } = get();
    
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

      // 初回メッセージ時にベクトルストアが未初期化の場合、自動で初期化を試行
      await ensureVectorStoreReady();

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
        adaptiveCard: response.data.adaptiveCard, // Adaptive Card対応
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

  // Adaptive Card送信処理
  submitAdaptiveCard: async (submitData) => {
    const { addMessage, setLoading, setError } = get();
    
    try {
      setLoading(true);
      setError(null);

      // Adaptive Card送信データをログ出力
      console.log('Adaptive Card submitted:', submitData);

      // バックエンドにAdaptive Card送信データを送信
      const apiBaseUrl = process.env.API_SERVER_HOST || '';
      const response = await axios.post(`${apiBaseUrl}/api/adaptive-card-submit`, {
        actionType: submitData.actionType,
        actionId: submitData.actionId,
        data: submitData.data,
      });

      // レスポンスメッセージを追加
      if (response.data.response) {
        const responseMsg = {
          id: Math.random().toString(36).substr(2, 9),
          text: response.data.response,
          timestamp: new Date(),
          isUser: false,
          adaptiveCard: response.data.adaptiveCard,
        };
        addMessage(responseMsg);
      }

    } catch (error) {
      console.error('Adaptive Card送信エラー:', error);
      setError('Adaptive Cardの送信に失敗しました');
      
      // エラーメッセージを追加
      const errorMsg = {
        id: Math.random().toString(36).substr(2, 9),
        text: 'Adaptive Cardの送信でエラーが発生しました。',
        timestamp: new Date(),
        isUser: false,
        isError: true,
      };
      addMessage(errorMsg);
    } finally {
      setLoading(false);
    }
  },

  // URL管理機能
  loadSavedUrl: async () => {
    try {
      const storedUrl = await AsyncStorage.getItem(URL_STORAGE_KEY);
      if (storedUrl) {
        set({ currentUrl: storedUrl });
        return storedUrl;
      }
    } catch (error) {
      console.error('URL読み込みエラー:', error);
    }
    return null;
  },

  saveUrl: async (url) => {
    try {
      await AsyncStorage.setItem(URL_STORAGE_KEY, url);
      set({ currentUrl: url });
    } catch (error) {
      console.error('URL保存エラー:', error);
      throw error;
    }
  },

  clearSavedUrl: async () => {
    try {
      await AsyncStorage.removeItem(URL_STORAGE_KEY);
      set({ currentUrl: null });
    } catch (error) {
      console.error('URL削除エラー:', error);
      throw error;
    }
  },

  // ベクトルストア管理機能
  checkVectorStoreStatus: async () => {
    try {
      const apiBaseUrl = process.env.API_SERVER_HOST || '';
      const response = await axios.get(`${apiBaseUrl}/api/vectorstore-status`);
      set({ vectorStoreStatus: response.data });
      return response.data;
    } catch (error) {
      console.error('ベクトルストア状態取得エラー:', error);
      const errorStatus = {
        initialized: false,
        current_url: null,
        status: 'error'
      };
      set({ vectorStoreStatus: errorStatus });
      return errorStatus;
    }
  },

  setUrl: async (url) => {
    try {
      set({ isLoading: true, error: null });
      
      const apiBaseUrl = process.env.API_SERVER_HOST || '';
      const response = await axios.post(`${apiBaseUrl}/api/set-url`, {
        url: url
      });

      if (response.data.success) {
        // AsyncStorageに保存
        await get().saveUrl(url);
        
        // ベクトルストア状態を更新
        await get().checkVectorStoreStatus();
        
        return { success: true, message: response.data.message };
      } else {
        return { success: false, message: response.data.message };
      }
    } catch (error) {
      console.error('URL設定エラー:', error);
      return { success: false, message: 'URL設定中にエラーが発生しました。' };
    } finally {
      set({ isLoading: false });
    }
  },

  clearVectorStore: async () => {
    try {
      set({ isLoading: true, error: null });
      
      const apiBaseUrl = process.env.API_SERVER_HOST || '';
      const response = await axios.post(`${apiBaseUrl}/api/clear-vectorstore`);

      if (response.data.success) {
        await get().checkVectorStoreStatus();
        return { success: true, message: response.data.message };
      } else {
        return { success: false, message: response.data.message };
      }
    } catch (error) {
      console.error('ベクトルストアクリアエラー:', error);
      return { success: false, message: 'クリア中にエラーが発生しました。' };
    } finally {
      set({ isLoading: false });
    }
  },

  // 初期化時にURLを自動読み込み（初回メッセージ送信前）
  ensureVectorStoreReady: async () => {
    const { checkVectorStoreStatus, loadSavedUrl, setUrl } = get();
    
    // ベクトルストアの状態をチェック
    const status = await checkVectorStoreStatus();
    
    if (!status.initialized) {
      // 保存されたURLがあるかチェック
      const savedUrl = await loadSavedUrl();
      if (savedUrl) {
        // 保存されたURLでベクトルストアを初期化
        await setUrl(savedUrl);
      }
    }
  },
}));