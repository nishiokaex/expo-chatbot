import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Card, Text, Avatar, useTheme } from 'react-native-paper';
import AdaptiveCard from './adaptive-cards/AdaptiveCard';

/**
 * メッセージバブルコンポーネント
 * react-native-paperベースのチャットメッセージ表示
 * Adaptive Cards対応
 */
const MessageBubble = ({ message, onAdaptiveCardSubmit }) => {
  const theme = useTheme();
  const { text, isUser, timestamp, isError, adaptiveCard } = message;

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
          isUser ? styles.userBubble : styles.aiBubble,
          adaptiveCard && !isUser && styles.adaptiveCardBubble
        ]}
        elevation={1}
      >
        <Card.Content style={styles.content}>
          {/* 通常のテキストメッセージ */}
          {text && (
            <Text
              variant="bodyMedium"
              style={[
                styles.messageText,
                { color: colors.textColor }
              ]}
            >
              {text}
            </Text>
          )}
          
          {/* Adaptive Card */}
          {adaptiveCard && !isUser && (
            <View style={styles.adaptiveCardContainer}>
              <AdaptiveCard
                cardJson={adaptiveCard}
                onSubmit={onAdaptiveCardSubmit}
                style={styles.adaptiveCard}
              />
            </View>
          )}
          
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
  adaptiveCardBubble: {
    maxWidth: '90%', // Adaptive Cardの場合は少し広め
  },
  adaptiveCardContainer: {
    marginVertical: 4,
  },
  adaptiveCard: {
    backgroundColor: 'transparent',
    elevation: 0,
  },
});

export default MessageBubble;