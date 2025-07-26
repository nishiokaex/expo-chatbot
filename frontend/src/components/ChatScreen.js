import React, { useCallback } from 'react';
import { View, StyleSheet, Text } from 'react-native';
import { GiftedChat, Bubble, Send } from 'react-native-gifted-chat';
import { useChatStore } from '../stores/ChatStore';
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context';

/**
 * チャット画面コンポーネント
 * react-native-gifted-chatを使用したチャットUI
 */
export default function ChatScreen() {
  const { 
    messages, 
    isLoading, 
    sendMessage 
  } = useChatStore();

  /**
   * メッセージ送信時のハンドラー
   * @param {Array} messages - 送信されたメッセージ配列
   */
  const onSend = useCallback((messages = []) => {
    const userMessage = messages[0];
    if (userMessage && userMessage.text) {
      sendMessage(userMessage.text);
    }
  }, [sendMessage]);

  /**
   * メッセージバブルのカスタマイズ
   */
  const renderBubble = (props) => {
    return (
      <Bubble
        {...props}
        wrapperStyle={{
          right: {
            backgroundColor: '#2196F3',
          },
          left: {
            backgroundColor: '#f0f0f0',
          },
        }}
        textStyle={{
          right: {
            color: '#fff',
          },
          left: {
            color: '#000',
          },
        }}
      />
    );
  };

  /**
   * 送信ボタンのカスタマイズ
   */
  const renderSend = (props) => {
    return (
      <Send {...props}>
        <View style={styles.sendButton}>
          <Text style={styles.sendButtonText}>送信</Text>
        </View>
      </Send>
    );
  };

  return (
    <SafeAreaProvider>
      <SafeAreaView style={styles.container}>
        <GiftedChat
          messages={messages}
          onSend={onSend}
          user={{
            _id: 1,
          }}
          renderBubble={renderBubble}
          renderSend={renderSend}
          placeholder="メッセージを入力してください..."
          alwaysShowSend
          scrollToBottom
          scrollToBottomStyle={{
            backgroundColor: '#2196F3',
          }}
          isLoadingEarlier={isLoading}
          locale="ja"
        />
      </SafeAreaView>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  sendButton: {
    backgroundColor: '#2196F3',
    borderRadius: 8,
    paddingHorizontal: 16,
    paddingVertical: 8,
    marginBottom: 4,
    marginRight: 4,
    minWidth: 60,
    alignItems: 'center',
    justifyContent: 'center',
  },
  sendButtonText: {
    color: '#fff',
    fontWeight: 'bold',
  },
});