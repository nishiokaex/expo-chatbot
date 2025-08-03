import React from 'react';
import { View, StyleSheet } from 'react-native';
import { useTheme } from 'react-native-paper';

/**
 * Adaptive Cards Column要素
 * ColumnSet内の個別の列を定義
 * 
 * サポートするプロパティ:
 * - items: 列内の要素配列
 * - width: 列の幅 (Auto, Stretch, ピクセル値、重み)
 * - verticalContentAlignment: 垂直配置 (Top, Center, Bottom)
 * - spacing: 要素間のスペーシング
 * - separator: 区切り線の表示
 */

const ColumnElement = ({ element, theme, renderElement }) => {
  const paperTheme = useTheme();

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

  const marginTop = getSpacingStyle(element.spacing);
  const justifyContent = getVerticalAlignment(element.verticalContentAlignment);

  // コンテナのスタイル
  const containerStyle = [
    styles.container,
    {
      marginTop: marginTop,
      justifyContent: justifyContent,
      borderLeftWidth: element.separator ? 1 : 0,
      borderLeftColor: paperTheme.colors.outline,
      paddingLeft: element.separator ? 8 : 0,
    }
  ];

  // アイテム間のスペーシング計算
  const getItemSpacing = (index, itemsLength) => {
    if (index === 0) return 0;
    return 6; // 列内アイテム間のスペーシング（少し狭め）
  };

  return (
    <View style={containerStyle}>
      {element.items && element.items.map((item, index) => (
        <View 
          key={index} 
          style={{ marginTop: getItemSpacing(index, element.items.length) }}
        >
          {renderElement(item, index)}
        </View>
      ))}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingVertical: 4,
  },
});

export default ColumnElement;