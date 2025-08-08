import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ScrollView, KeyboardAvoidingView, Platform, Alert } from 'react-native';
import { 
  TextInput, 
  Button, 
  Card, 
  Title, 
  Paragraph, 
  Surface,
  Snackbar,
  ActivityIndicator,
  useTheme,
  Divider,
  List,
  IconButton
} from 'react-native-paper';
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context';
import AsyncStorage from '@react-native-async-storage/async-storage';
import axios from 'axios';

/**
 * URL設定画面コンポーネント
 * チャットボット用のURL設定とベクトルストア管理
 */
export default function UrlSettingsScreen() {
  const theme = useTheme();
  const [url, setUrl] = useState('');
  const [savedUrl, setSavedUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [vectorStoreStatus, setVectorStoreStatus] = useState({
    initialized: false,
    current_url: null,
    status: 'not_initialized'
  });
  const [snackbar, setSnackbar] = useState({
    visible: false,
    message: '',
    type: 'info' // 'success', 'error', 'info'
  });

  // AsyncStorageのキー
  const URL_STORAGE_KEY = 'chatbot_url';

  useEffect(() => {
    loadSavedUrl();
    checkVectorStoreStatus();
  }, []);

  /**
   * 保存されたURLを読み込み
   */
  const loadSavedUrl = async () => {
    try {
      const storedUrl = await AsyncStorage.getItem(URL_STORAGE_KEY);
      if (storedUrl) {
        setSavedUrl(storedUrl);
        setUrl(storedUrl);
      }
    } catch (error) {
      console.error('URL読み込みエラー:', error);
    }
  };

  /**
   * URLをAsyncStorageに保存
   */
  const saveUrl = async (urlToSave) => {
    try {
      await AsyncStorage.setItem(URL_STORAGE_KEY, urlToSave);
      setSavedUrl(urlToSave);
    } catch (error) {
      console.error('URL保存エラー:', error);
      throw error;
    }
  };

  /**
   * ベクトルストアの状態をチェック
   */
  const checkVectorStoreStatus = async () => {
    try {
      const apiBaseUrl = process.env.API_SERVER_HOST || '';
      const response = await axios.get(`${apiBaseUrl}/api/vectorstore-status`);
      setVectorStoreStatus(response.data);
    } catch (error) {
      console.error('ベクトルストア状態取得エラー:', error);
      setVectorStoreStatus({
        initialized: false,
        current_url: null,
        status: 'error'
      });
    }
  };

  /**
   * URLバリデーション
   */
  const validateUrl = (inputUrl) => {
    const urlPattern = /^(https?:\/\/)[\w\-]+(\.[\w\-]+)+([\w\-\.,@?^=%&:/~\+#]*[\w\-\@?^=%&/~\+#])?$/;
    return urlPattern.test(inputUrl);
  };

  /**
   * スナックバー表示ヘルパー
   */
  const showSnackbar = (message, type = 'info') => {
    setSnackbar({
      visible: true,
      message,
      type
    });
  };

  /**
   * URL設定とベクトルストア構築
   */
  const handleSetUrl = async () => {
    if (!url.trim()) {
      showSnackbar('URLを入力してください。', 'error');
      return;
    }

    if (!validateUrl(url.trim())) {
      showSnackbar('有効なURLを入力してください。', 'error');
      return;
    }

    setIsLoading(true);
    
    try {
      const apiBaseUrl = process.env.API_SERVER_HOST || '';
      
      // バックエンドにURL設定リクエスト
      const response = await axios.post(`${apiBaseUrl}/api/set-url`, {
        url: url.trim()
      });

      if (response.data.success) {
        // AsyncStorageに保存
        await saveUrl(url.trim());
        
        // ベクトルストア状態を更新
        await checkVectorStoreStatus();
        
        showSnackbar('URLの設定とドキュメントの読み込みが完了しました。', 'success');
      } else {
        showSnackbar(response.data.message || 'URL設定に失敗しました。', 'error');
      }
    } catch (error) {
      console.error('URL設定エラー:', error);
      showSnackbar('URL設定中にエラーが発生しました。', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * ベクトルストアクリア
   */
  const handleClearVectorStore = async () => {
    Alert.alert(
      '確認',
      'ベクトルストアをクリアしますか？この操作は元に戻せません。',
      [
        {
          text: 'キャンセル',
          style: 'cancel'
        },
        {
          text: 'クリア',
          style: 'destructive',
          onPress: async () => {
            setIsLoading(true);
            
            try {
              const apiBaseUrl = process.env.API_SERVER_HOST || '';
              const response = await axios.post(`${apiBaseUrl}/api/clear-vectorstore`);

              if (response.data.success) {
                await checkVectorStoreStatus();
                showSnackbar('ベクトルストアをクリアしました。', 'success');
              } else {
                showSnackbar(response.data.message || 'クリアに失敗しました。', 'error');
              }
            } catch (error) {
              console.error('ベクトルストアクリアエラー:', error);
              showSnackbar('クリア中にエラーが発生しました。', 'error');
            } finally {
              setIsLoading(false);
            }
          }
        }
      ]
    );
  };

  /**
   * 保存されたURLをクリア
   */
  const handleClearSavedUrl = async () => {
    Alert.alert(
      '確認',
      '保存されたURLを削除しますか？',
      [
        {
          text: 'キャンセル',
          style: 'cancel'
        },
        {
          text: '削除',
          style: 'destructive',
          onPress: async () => {
            try {
              await AsyncStorage.removeItem(URL_STORAGE_KEY);
              setSavedUrl('');
              setUrl('');
              showSnackbar('保存されたURLを削除しました。', 'success');
            } catch (error) {
              console.error('URL削除エラー:', error);
              showSnackbar('URL削除中にエラーが発生しました。', 'error');
            }
          }
        }
      ]
    );
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'ready':
        return theme.colors.primary;
      case 'error':
        return theme.colors.error;
      default:
        return theme.colors.outline;
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'ready':
        return '準備完了';
      case 'error':
        return 'エラー';
      default:
        return '未初期化';
    }
  };

  return (
    <SafeAreaProvider>
      <SafeAreaView style={[styles.container, { backgroundColor: theme.colors.background }]}>
        <KeyboardAvoidingView 
          style={styles.keyboardAvoid}
          behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        >
          <ScrollView 
            style={styles.scrollView}
            contentContainerStyle={styles.scrollContent}
            showsVerticalScrollIndicator={false}
          >
            {/* URL設定カード */}
            <Card style={styles.card}>
              <Card.Content>
                <Title style={styles.cardTitle}>URL設定</Title>
                <Paragraph style={styles.cardDescription}>
                  チャットボットが参照するWebページのURLを設定してください。
                </Paragraph>
                
                <TextInput
                  mode="outlined"
                  label="WebページURL"
                  placeholder="https://example.com"
                  value={url}
                  onChangeText={setUrl}
                  style={styles.textInput}
                  disabled={isLoading}
                  keyboardType="url"
                  autoCapitalize="none"
                  autoCorrect={false}
                />

                <View style={styles.buttonContainer}>
                  <Button
                    mode="contained"
                    onPress={handleSetUrl}
                    loading={isLoading}
                    disabled={isLoading || !url.trim()}
                    style={styles.primaryButton}
                  >
                    URLを設定
                  </Button>
                </View>
              </Card.Content>
            </Card>

            {/* 現在の状態カード */}
            <Card style={styles.card}>
              <Card.Content>
                <Title style={styles.cardTitle}>ベクトルストア状態</Title>
                
                <List.Item
                  title="ステータス"
                  description={getStatusText(vectorStoreStatus.status)}
                  left={() => (
                    <View style={[
                      styles.statusIndicator,
                      { backgroundColor: getStatusColor(vectorStoreStatus.status) }
                    ]} />
                  )}
                />

                {vectorStoreStatus.current_url && (
                  <List.Item
                    title="現在のURL"
                    description={vectorStoreStatus.current_url}
                    left={() => <List.Icon icon="link" />}
                  />
                )}

                <Divider style={styles.divider} />

                <View style={styles.buttonRow}>
                  <Button
                    mode="outlined"
                    onPress={checkVectorStoreStatus}
                    disabled={isLoading}
                    style={styles.secondaryButton}
                    icon="refresh"
                  >
                    状態更新
                  </Button>

                  <Button
                    mode="outlined"
                    onPress={handleClearVectorStore}
                    disabled={isLoading || !vectorStoreStatus.initialized}
                    style={[styles.secondaryButton, { borderColor: theme.colors.error }]}
                    textColor={theme.colors.error}
                    icon="delete"
                  >
                    クリア
                  </Button>
                </View>
              </Card.Content>
            </Card>

            {/* 保存されたURL */}
            {savedUrl && (
              <Card style={styles.card}>
                <Card.Content>
                  <Title style={styles.cardTitle}>保存されたURL</Title>
                  <List.Item
                    title={savedUrl}
                    right={() => (
                      <IconButton
                        icon="delete"
                        iconColor={theme.colors.error}
                        onPress={handleClearSavedUrl}
                        disabled={isLoading}
                      />
                    )}
                  />
                </Card.Content>
              </Card>
            )}

            {/* 使用方法 */}
            <Card style={styles.card}>
              <Card.Content>
                <Title style={styles.cardTitle}>使用方法</Title>
                <Paragraph style={styles.helpText}>
                  1. WebページのURLを入力して「URLを設定」をタップ
                </Paragraph>
                <Paragraph style={styles.helpText}>
                  2. ドキュメントの読み込みが完了すると、チャットでその内容について質問できます
                </Paragraph>
                <Paragraph style={styles.helpText}>
                  3. 新しいURLに変更する場合は、再度URL設定を行ってください
                </Paragraph>
              </Card.Content>
            </Card>
          </ScrollView>

          {/* スナックバー */}
          <Snackbar
            visible={snackbar.visible}
            onDismiss={() => setSnackbar({ ...snackbar, visible: false })}
            duration={4000}
            style={[
              styles.snackbar,
              {
                backgroundColor: 
                  snackbar.type === 'success' ? theme.colors.primary :
                  snackbar.type === 'error' ? theme.colors.error :
                  theme.colors.surface
              }
            ]}
            action={{
              label: '閉じる',
              onPress: () => setSnackbar({ ...snackbar, visible: false }),
            }}
          >
            {snackbar.message}
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
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    padding: 16,
    paddingBottom: 32,
  },
  card: {
    marginBottom: 16,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  cardDescription: {
    marginBottom: 16,
    color: '#666',
  },
  textInput: {
    marginBottom: 16,
  },
  buttonContainer: {
    marginTop: 8,
  },
  primaryButton: {
    marginVertical: 4,
  },
  secondaryButton: {
    flex: 1,
    marginHorizontal: 4,
  },
  buttonRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 8,
  },
  statusIndicator: {
    width: 12,
    height: 12,
    borderRadius: 6,
    alignSelf: 'center',
    marginLeft: 12,
  },
  divider: {
    marginVertical: 16,
  },
  helpText: {
    marginBottom: 8,
    fontSize: 14,
    lineHeight: 20,
  },
  snackbar: {
    marginBottom: 16,
  },
});