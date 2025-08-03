import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Switch, Text, useTheme } from 'react-native-paper';

/**
 * Adaptive Cards Input.Toggle要素
 * トグルスイッチ（オン/オフ）入力
 * 
 * サポートするプロパティ:
 * - id: 入力フィールドの識別子 (必須)
 * - title: ラベルテキスト (必須)
 * - value: 初期値 (デフォルト: "false")
 * - valueOn: オン時の値 (デフォルト: "true")
 * - valueOff: オフ時の値 (デフォルト: "false")
 * - spacing: 要素間のスペーシング
 * - separator: 区切り線の表示
 */

const ToggleInputElement = ({ element, theme, inputValues, updateInputValue }) => {
  const paperTheme = useTheme();
  
  // 現在の値を取得（inputValuesから、なければデフォルト値）
  const currentValue = inputValues[element.id] || element.value || element.valueOff;
  
  // 現在の値がオン状態かどうかを判定
  const isOn = currentValue === element.valueOn;

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

  const marginTop = getSpacingStyle(element.spacing);

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

  // スイッチ状態変更時のハンドラ
  const handleToggle = () => {
    const newValue = isOn ? element.valueOff : element.valueOn;
    updateInputValue(element.id, newValue);
  };

  return (
    <View style={containerStyle}>
      <View style={styles.toggleContainer}>
        <Text 
          variant="bodyMedium" 
          style={[styles.label, { color: paperTheme.colors.onSurface }]}
        >
          {element.title}
        </Text>
        <Switch
          value={isOn}
          onValueChange={handleToggle}
          style={styles.switch}
        />
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginVertical: 2,
  },
  toggleContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 8,
    paddingHorizontal: 4,
  },
  label: {
    flex: 1,
    marginRight: 16,
  },
  switch: {
    flexShrink: 0,
  },
});

export default ToggleInputElement;