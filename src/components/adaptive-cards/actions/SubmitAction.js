import React from 'react';
import { StyleSheet } from 'react-native';
import { Button } from 'react-native-paper';

/**
 * Adaptive Cards Action.Submit要素
 * フォームデータを送信するためのアクションボタン
 * 
 * サポートするプロパティ:
 * - title: ボタンのテキスト (必須)
 * - data: 送信時に含める追加データ
 * - id: アクションの識別子
 */

const SubmitAction = ({ action, theme, inputValues, onSubmit }) => {
  // 送信ボタンクリック時のハンドラ
  const handleSubmit = () => {
    // 入力値と追加データを結合
    const submitData = {
      ...inputValues,
      ...action.data,
    };

    // onSubmitコールバックを呼び出し
    if (onSubmit && typeof onSubmit === 'function') {
      onSubmit({
        action: action,
        data: submitData,
        actionType: 'Action.Submit',
        actionId: action.id,
      });
    } else {
      console.log('Action.Submit triggered:', {
        actionId: action.id,
        data: submitData,
      });
    }
  };

  return (
    <Button
      mode="contained"
      onPress={handleSubmit}
      style={styles.button}
      compact={false}
    >
      {action.title}
    </Button>
  );
};

const styles = StyleSheet.create({
  button: {
    borderRadius: 8,
  },
});

export default SubmitAction;