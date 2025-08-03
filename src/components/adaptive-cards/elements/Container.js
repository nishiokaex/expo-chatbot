import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Surface, useTheme } from 'react-native-paper';

/**
 * Adaptive Cards Container要素
 * 他の要素をグループ化するためのコンテナ
 * 
 * サポートするプロパティ:
 * - items: 子要素の配列
 * - style: コンテナのスタイル (Default, Emphasis, Good, Attention, Warning, Accent)
 * - verticalContentAlignment: 垂直配置 (Top, Center, Bottom)
 * - spacing: 要素間のスペーシング
 * - separator: 区切り線の表示
 * - bleed: 親要素のパディングを無視
 */

const ContainerElement = ({ element, theme, renderElement }) => {
  const paperTheme = useTheme();

  // コンテナスタイルの背景色取得
  const getBackgroundColor = (style) => {
    switch (style) {
      case 'Emphasis':
        return paperTheme.colors.surfaceVariant;
      case 'Good':
        return '#E8F5E8'; // 薄い緑
      case 'Attention':
        return paperTheme.colors.errorContainer;
      case 'Warning':
        return '#FFF3E0'; // 薄いオレンジ
      case 'Accent':
        return paperTheme.colors.primaryContainer;
      case 'Default':
      default:
        return 'transparent';
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

  // 垂直配置のスタイル取得
  const getVerticalAlignment = (alignment) => {
    switch (alignment) {
      case 'Center':
        return 'center';
      case 'Bottom':
        return 'flex-end';
      case 'Top':
      default:
        return 'flex-start';
    }
  };

  const backgroundColor = getBackgroundColor(element.style);
  const marginTop = getSpacingStyle(element.spacing);
  const justifyContent = getVerticalAlignment(element.verticalContentAlignment);

  // コンテナのスタイル
  const containerStyle = [
    styles.container,
    {
      backgroundColor: backgroundColor,
      marginTop: marginTop,
      borderTopWidth: element.separator ? 1 : 0,
      borderTopColor: paperTheme.colors.outline,
      paddingTop: element.separator ? 8 : 0,
      justifyContent: justifyContent,
    }
  ];

  // bleedプロパティによるパディング調整
  const contentStyle = [
    styles.content,
    {
      marginHorizontal: element.bleed ? -12 : 0,
    }
  ];

  // アイテム間のスペーシング計算
  const getItemSpacing = (index, itemsLength) => {
    if (index === 0) return 0;
    return 8; // アイテム間のデフォルトスペーシング
  };

  // 背景色が透明でない場合はSurfaceを使用
  const ContainerComponent = backgroundColor === 'transparent' ? View : Surface;
  const containerProps = backgroundColor === 'transparent' 
    ? { style: containerStyle }
    : { style: containerStyle, elevation: 0 };

  return (
    <ContainerComponent {...containerProps}>
      <View style={contentStyle}>
        {element.items && element.items.map((item, index) => (
          <View 
            key={index} 
            style={{ marginTop: getItemSpacing(index, element.items.length) }}
          >
            {renderElement(item, index)}
          </View>
        ))}
      </View>
    </ContainerComponent>
  );
};

const styles = StyleSheet.create({
  container: {
    borderRadius: 8,
    paddingVertical: 8,
    paddingHorizontal: 12,
  },
  content: {
    flex: 1,
  },
});

export default ContainerElement;