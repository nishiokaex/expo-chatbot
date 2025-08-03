import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Text, useTheme } from 'react-native-paper';

/**
 * Adaptive Cards TextBlock要素
 * テキストを表示するための基本要素
 * 
 * サポートするプロパティ:
 * - text: 表示するテキスト (必須)
 * - color: テキスト色 (Default, Dark, Light, Accent, Good, Warning, Attention)
 * - size: テキストサイズ (Small, Default, Medium, Large, ExtraLarge)
 * - weight: フォントウェイト (Lighter, Default, Bolder)
 * - wrap: テキストの折り返し (true/false)
 * - maxLines: 最大行数
 * - horizontalAlignment: 水平配置 (Left, Center, Right)
 * - isSubtle: 薄い表示 (true/false)
 * - spacing: 要素間のスペーシング
 */

const TextBlockElement = ({ element, theme }) => {
  const paperTheme = useTheme();

  // テキスト色の取得
  const getTextColor = (color) => {
    switch (color) {
      case 'Dark':
        return paperTheme.colors.onSurface;
      case 'Light':
        return paperTheme.colors.outline;
      case 'Accent':
        return paperTheme.colors.primary;
      case 'Good':
        return '#4CAF50'; // 成功色
      case 'Warning':
        return '#FF9800'; // 警告色
      case 'Attention':
        return paperTheme.colors.error;
      case 'Default':
      default:
        return paperTheme.colors.onSurface;
    }
  };

  // テキストサイズの取得
  const getTextVariant = (size) => {
    switch (size) {
      case 'Small':
        return 'bodySmall';
      case 'Medium':
        return 'bodyLarge';
      case 'Large':
        return 'headlineSmall';
      case 'ExtraLarge':
        return 'headlineMedium';
      case 'Default':
      default:
        return 'bodyMedium';
    }
  };

  // フォントウェイトの取得
  const getFontWeight = (weight) => {
    switch (weight) {
      case 'Lighter':
        return '300';
      case 'Bolder':
        return 'bold';
      case 'Default':
      default:
        return 'normal';
    }
  };

  // 水平配置のスタイル取得
  const getAlignmentStyle = (alignment) => {
    switch (alignment) {
      case 'Center':
        return 'center';
      case 'Right':
        return 'right';
      case 'Left':
      default:
        return 'left';
    }
  };

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

  const textColor = getTextColor(element.color);
  const textVariant = getTextVariant(element.size);
  const fontWeight = getFontWeight(element.weight);
  const textAlign = getAlignmentStyle(element.horizontalAlignment);
  const marginTop = getSpacingStyle(element.spacing);

  // isSubtleの場合は透明度を下げる
  const opacity = element.isSubtle ? 0.6 : 1.0;

  const textStyle = {
    color: textColor,
    fontWeight: fontWeight,
    textAlign: textAlign,
    opacity: opacity,
  };

  // 区切り線のスタイル
  const containerStyle = [
    styles.container,
    {
      marginTop: marginTop,
      borderTopWidth: element.separator ? 1 : 0,
      borderTopColor: paperTheme.colors.outline,
      paddingTop: element.separator ? 8 : 0,
    }
  ];

  return (
    <View style={containerStyle}>
      <Text
        variant={textVariant}
        style={textStyle}
        numberOfLines={element.maxLines}
        ellipsizeMode={element.wrap ? undefined : 'tail'}
      >
        {element.text}
      </Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginVertical: 2,
  },
});

export default TextBlockElement;