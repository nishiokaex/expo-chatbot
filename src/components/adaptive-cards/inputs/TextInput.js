import React from 'react';
import { View, StyleSheet } from 'react-native';
import { TextInput, useTheme } from 'react-native-paper';

/**
 * Adaptive Cards Input.Text要素
 * テキスト入力フィールド
 * 
 * サポートするプロパティ:
 * - id: 入力フィールドの識別子 (必須)
 * - placeholder: プレースホルダーテキスト
 * - value: 初期値
 * - maxLength: 最大文字数
 * - isMultiline: 複数行入力 (true/false)
 * - style: 入力スタイル (Text, Tel, Url, Email)
 * - spacing: 要素間のスペーシング
 * - separator: 区切り線の表示
 */

const TextInputElement = ({ element, theme, inputValues, updateInputValue }) => {
  const paperTheme = useTheme();
  
  // 現在の値を取得（inputValuesから、なければデフォルト値）
  const currentValue = inputValues[element.id] || element.value || '';

  // スペーシングの取得
  const getSpacingStyle = (spacing) => {
    switch (spacing) {
      case 'None':
        return 0;
      case 'Small':
        return 4;
      case 'Medium':
        return 12;
      case 'Large':
        return 16;
      case 'ExtraLarge':
        return 24;
      case 'Padding':
        return 16;
      case 'Default':
      default:
        return 8;
    }
  };

  // 入力スタイルに基づくキーボードタイプの取得
  const getKeyboardType = (style) => {
    switch (style) {
      case 'Tel':
        return 'phone-pad';
      case 'Url':
        return 'url';
      case 'Email':
        return 'email-address';
      case 'Text':
      default:
        return 'default';
    }
  };

  // 入力スタイルに基づく自動補完タイプの取得
  const getAutoCompleteType = (style) => {
    switch (style) {
      case 'Tel':
        return 'tel';
      case 'Url':
        return 'url';
      case 'Email':
        return 'email';
      case 'Text':
      default:
        return 'off';
    }
  };

  const marginTop = getSpacingStyle(element.spacing);
  const keyboardType = getKeyboardType(element.style);
  const autoCompleteType = getAutoCompleteType(element.style);

  // コンテナのスタイル
  const containerStyle = [
    styles.container,
    {
      marginTop: marginTop,
      borderTopWidth: element.separator ? 1 : 0,
      borderTopColor: paperTheme.colors.outline,
      paddingTop: element.separator ? 8 : 0,
    }
  ];

  // 値変更時のハンドラ
  const handleValueChange = (newValue) => {
    updateInputValue(element.id, newValue);
  };

  return (
    <View style={containerStyle}>
      <TextInput
        mode="outlined"
        label={element.placeholder}
        placeholder={element.placeholder}
        value={currentValue}
        onChangeText={handleValueChange}
        multiline={element.isMultiline}
        numberOfLines={element.isMultiline ? 3 : 1}
        maxLength={element.maxLength}
        keyboardType={keyboardType}
        autoCompleteType={autoCompleteType}
        style={styles.textInput}
        contentStyle={element.isMultiline ? styles.multilineContent : undefined}
        dense={!element.isMultiline}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginVertical: 2,
  },
  textInput: {
    backgroundColor: 'transparent',
  },
  multilineContent: {
    minHeight: 80,
    textAlignVertical: 'top',
  },
});

export default TextInputElement;