import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Card, Text, Avatar, useTheme } from 'react-native-paper';

/**
 * メッセージバブルコンポーネント
 * react-native-paperベースのチャットメッセージ表示
 */
const MessageBubble = ({ message }) => {
  const theme = useTheme();
  const { text, isUser, timestamp, isError } = message;

  // エラーメッセージの場合の色設定
  const getMessageColors = () => {
    if (isError) {
      return {
        backgroundColor: theme.colors.errorContainer,
        textColor: theme.colors.onErrorContainer,
      };
    }
    
    if (isUser) {
      return {
        backgroundColor: theme.colors.primary,
        textColor: theme.colors.onPrimary,
      };
    }
    
    return {
      backgroundColor: theme.colors.surfaceVariant,
      textColor: theme.colors.onSurfaceVariant,
    };
  };

  const colors = getMessageColors();

  // タイムスタンプのフォーマット
  const formatTime = (date) => {
    return new Date(date).toLocaleTimeString('ja-JP', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <View style={[
      styles.container,
      isUser ? styles.userMessage : styles.aiMessage
    ]}>
      {/* AIメッセージの場合のアバター */}
      {!isUser && (
        <Avatar.Icon
          size={32}
          icon="robot"
          style={[styles.avatar, { backgroundColor: theme.colors.secondary }]}
        />
      )}
      
      {/* メッセージバブル */}
      <Card
        style={[
          styles.bubble,
          { backgroundColor: colors.backgroundColor },
          isUser ? styles.userBubble : styles.aiBubble
        ]}
        elevation={1}
      >
        <Card.Content style={styles.content}>
          <Text
            variant="bodyMedium"
            style={[
              styles.messageText,
              { color: colors.textColor }
            ]}
          >
            {text}
          </Text>
          <Text
            variant="labelSmall"
            style={[
              styles.timestamp,
              { color: colors.textColor, opacity: 0.7 }
            ]}
          >
            {formatTime(timestamp)}
          </Text>
        </Card.Content>
      </Card>

      {/* ユーザーメッセージの場合のアバター */}
      {isUser && (
        <Avatar.Icon
          size={32}
          icon="account"
          style={[styles.avatar, { backgroundColor: theme.colors.primary }]}
        />
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    marginVertical: 4,
    marginHorizontal: 16,
    alignItems: 'flex-end',
  },
  userMessage: {
    justifyContent: 'flex-end',
  },
  aiMessage: {
    justifyContent: 'flex-start',
  },
  avatar: {
    marginHorizontal: 8,
  },
  bubble: {
    maxWidth: '75%',
    minWidth: '20%',
    borderRadius: 16,
  },
  userBubble: {
    borderBottomRightRadius: 4,
  },
  aiBubble: {
    borderBottomLeftRadius: 4,
  },
  content: {
    paddingVertical: 8,
    paddingHorizontal: 12,
  },
  messageText: {
    lineHeight: 20,
  },
  timestamp: {
    marginTop: 4,
    textAlign: 'right',
  },
});

export default MessageBubble;