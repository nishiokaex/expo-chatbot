import React, { useState, useRef, useEffect } from 'react';
import { View, StyleSheet, FlatList, KeyboardAvoidingView, Platform } from 'react-native';
import { 
  TextInput, 
  IconButton, 
  ActivityIndicator, 
  Surface,
  Snackbar,
  useTheme 
} from 'react-native-paper';
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context';
import { useChatStore } from '../stores/ChatStore';
import MessageBubble from './MessageBubble';

/**
 * チャット画面コンポーネント
 * react-native-paperベースのチャットUI
 */
export default function ChatScreen() {
  const theme = useTheme();
  const [inputText, setInputText] = useState('');
  const flatListRef = useRef(null);
  
  const { 
    messages, 
    isLoading, 
    error,
    sendMessage,
    setError
  } = useChatStore();

  // 新しいメッセージが追加されたら自動スクロール
  useEffect(() => {
    if (messages.length > 0 && flatListRef.current) {
      setTimeout(() => {
        flatListRef.current?.scrollToEnd({ animated: true });
      }, 100);
    }
  }, [messages]);

  /**
   * メッセージ送信ハンドラー
   */
  const handleSend = () => {
    if (inputText.trim() && !isLoading) {
      sendMessage(inputText.trim());
      setInputText('');
    }
  };

  /**
   * メッセージアイテムのレンダリング
   */
  const renderMessage = ({ item }) => (
    <MessageBubble message={item} />
  );

  /**
   * メッセージリストのキー抽出
   */
  const keyExtractor = (item) => item.id;

  /**
   * ローディングインジケーターのレンダリング
   */
  const renderLoadingIndicator = () => {
    if (!isLoading) return null;
    
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator animating size="small" color={theme.colors.primary} />
      </View>
    );
  };

  return (
    <SafeAreaProvider>
      <SafeAreaView style={[styles.container, { backgroundColor: theme.colors.background }]}>
        <KeyboardAvoidingView 
          style={styles.keyboardAvoid}
          behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
          keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}
        >
          {/* メッセージリスト */}
          <FlatList
            ref={flatListRef}
            data={messages}
            renderItem={renderMessage}
            keyExtractor={keyExtractor}
            style={styles.messagesList}
            contentContainerStyle={styles.messagesContainer}
            showsVerticalScrollIndicator={false}
            ListFooterComponent={renderLoadingIndicator}
          />

          {/* 入力エリア */}
          <Surface style={[styles.inputSurface, { backgroundColor: theme.colors.surface }]} elevation={2}>
            <View style={styles.inputContainer}>
              <TextInput
                mode="outlined"
                placeholder="メッセージを入力してください..."
                value={inputText}
                onChangeText={setInputText}
                style={styles.textInput}
                multiline
                maxLength={1000}
                disabled={isLoading}
                onSubmitEditing={handleSend}
                returnKeyType="send"
                blurOnSubmit={false}
              />
              <IconButton
                icon="send"
                mode="contained"
                size={24}
                disabled={!inputText.trim() || isLoading}
                onPress={handleSend}
                style={[
                  styles.sendButton,
                  { 
                    backgroundColor: inputText.trim() && !isLoading 
                      ? theme.colors.primary 
                      : theme.colors.surfaceDisabled 
                  }
                ]}
                iconColor={inputText.trim() && !isLoading 
                  ? theme.colors.onPrimary 
                  : theme.colors.onSurfaceDisabled
                }
              />
            </View>
          </Surface>

          {/* エラー表示 */}
          <Snackbar
            visible={!!error}
            onDismiss={() => setError(null)}
            duration={4000}
            action={{
              label: '閉じる',
              onPress: () => setError(null),
            }}
          >
            {error}
          </Snackbar>
        </KeyboardAvoidingView>
      </SafeAreaView>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  keyboardAvoid: {
    flex: 1,
  },
  messagesList: {
    flex: 1,
  },
  messagesContainer: {
    paddingVertical: 8,
    flexGrow: 1,
  },
  loadingContainer: {
    padding: 16,
    alignItems: 'center',
  },
  inputSurface: {
    paddingVertical: 8,
    paddingHorizontal: 16,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    gap: 8,
  },
  textInput: {
    flex: 1,
    maxHeight: 100,
  },
  sendButton: {
    margin: 0,
  },
});