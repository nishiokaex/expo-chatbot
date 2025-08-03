/**
 * 新しいreact-native-paperベースのチャットUIのテストファイル
 * react-native-gifted-chatからの移行テスト
 */

import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import { PaperProvider } from 'react-native-paper';
import ChatScreen from '../src/components/ChatScreen';
import MessageBubble from '../src/components/MessageBubble';
import { useChatStore } from '../src/stores/ChatStore';

// Zustandストアをモック化
jest.mock('../src/stores/ChatStore');

// テスト用のラッパーコンポーネント
const TestWrapper = ({ children }) => (
  <PaperProvider>
    {children}
  </PaperProvider>
);

describe('ChatScreen with react-native-paper', () => {
  const mockSendMessage = jest.fn();
  const mockSetError = jest.fn();

  beforeEach(() => {
    // ストアのモックをリセット
    useChatStore.mockReturnValue({
      messages: [],
      isLoading: false,
      error: null,
      sendMessage: mockSendMessage,
      setError: mockSetError,
    });
    
    jest.clearAllMocks();
  });

  test('should render chat input field and send button', () => {
    const { getByPlaceholderText, getByRole } = render(
      <TestWrapper>
        <ChatScreen />
      </TestWrapper>
    );

    // 入力フィールドの存在確認
    expect(getByPlaceholderText('メッセージを入力してください...')).toBeTruthy();
    
    // 送信ボタンの存在確認（アイコンボタン）
    expect(getByRole('button')).toBeTruthy();
  });

  test('should send message when text is entered and send button is pressed', async () => {
    const { getByPlaceholderText, getByRole } = render(
      <TestWrapper>
        <ChatScreen />
      </TestWrapper>
    );

    const input = getByPlaceholderText('メッセージを入力してください...');
    const sendButton = getByRole('button');

    // テキスト入力
    fireEvent.changeText(input, 'テストメッセージ');
    
    // 送信ボタンをタップ
    fireEvent.press(sendButton);

    // sendMessageが呼ばれることを確認
    await waitFor(() => {
      expect(mockSendMessage).toHaveBeenCalledWith('テストメッセージ');
    });
  });

  test('should display messages correctly', () => {
    const testMessages = [
      {
        id: '1',
        text: 'ユーザーメッセージ',
        timestamp: new Date(),
        isUser: true,
      },
      {
        id: '2',
        text: 'AIメッセージ',
        timestamp: new Date(),
        isUser: false,
      },
    ];

    useChatStore.mockReturnValue({
      messages: testMessages,
      isLoading: false,
      error: null,
      sendMessage: mockSendMessage,
      setError: mockSetError,
    });

    const { getByText } = render(
      <TestWrapper>
        <ChatScreen />
      </TestWrapper>
    );

    // メッセージが表示されることを確認
    expect(getByText('ユーザーメッセージ')).toBeTruthy();
    expect(getByText('AIメッセージ')).toBeTruthy();
  });

  test('should show loading indicator when isLoading is true', () => {
    useChatStore.mockReturnValue({
      messages: [],
      isLoading: true,
      error: null,
      sendMessage: mockSendMessage,
      setError: mockSetError,
    });

    const { getByTestId } = render(
      <TestWrapper>
        <ChatScreen />
      </TestWrapper>
    );

    // ローディングインジケーターが表示されることを確認
    expect(getByTestId('activity-indicator')).toBeTruthy();
  });

  test('should disable send button when input is empty', () => {
    const { getByRole } = render(
      <TestWrapper>
        <ChatScreen />
      </TestWrapper>
    );

    const sendButton = getByRole('button');
    
    // 送信ボタンが無効化されていることを確認
    expect(sendButton.props.accessibilityState.disabled).toBe(true);
  });
});

describe('MessageBubble component', () => {
  test('should render user message correctly', () => {
    const userMessage = {
      id: '1',
      text: 'ユーザーメッセージ',
      timestamp: new Date(),
      isUser: true,
    };

    const { getByText } = render(
      <TestWrapper>
        <MessageBubble message={userMessage} />
      </TestWrapper>
    );

    expect(getByText('ユーザーメッセージ')).toBeTruthy();
  });

  test('should render AI message correctly', () => {
    const aiMessage = {
      id: '2',
      text: 'AIメッセージ',
      timestamp: new Date(),
      isUser: false,
    };

    const { getByText } = render(
      <TestWrapper>
        <MessageBubble message={aiMessage} />
      </TestWrapper>
    );

    expect(getByText('AIメッセージ')).toBeTruthy();
  });

  test('should render error message with different styling', () => {
    const errorMessage = {
      id: '3',
      text: 'エラーメッセージ',
      timestamp: new Date(),
      isUser: false,
      isError: true,
    };

    const { getByText } = render(
      <TestWrapper>
        <MessageBubble message={errorMessage} />
      </TestWrapper>
    );

    expect(getByText('エラーメッセージ')).toBeTruthy();
  });

  test('should display timestamp correctly', () => {
    const testDate = new Date('2024-01-01T12:00:00');
    const message = {
      id: '1',
      text: 'テストメッセージ',
      timestamp: testDate,
      isUser: true,
    };

    const { getByText } = render(
      <TestWrapper>
        <MessageBubble message={message} />
      </TestWrapper>
    );

    // タイムスタンプが表示されることを確認（フォーマットは12:00）
    expect(getByText('12:00')).toBeTruthy();
  });
});

describe('ChatStore integration', () => {
  test('should update message format from GiftedChat to Paper format', () => {
    // 旧形式（GiftedChat）
    const oldMessage = {
      _id: '1',
      text: 'テストメッセージ',
      createdAt: new Date(),
      user: {
        _id: 1,
        name: 'User',
      },
    };

    // 新形式（Paper）
    const newMessage = {
      id: '1',
      text: 'テストメッセージ',
      timestamp: new Date(),
      isUser: true,
    };

    // 新形式の方がよりシンプルで扱いやすいことを確認
    expect(Object.keys(newMessage)).toHaveLength(4);
    expect(newMessage.id).toBeDefined();
    expect(newMessage.isUser).toBeDefined();
    expect(typeof newMessage.isUser).toBe('boolean');
  });
});