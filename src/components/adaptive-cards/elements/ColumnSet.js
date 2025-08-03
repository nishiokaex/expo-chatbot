import React from 'react';
import { View, StyleSheet } from 'react-native';
import { useTheme } from 'react-native-paper';
import ColumnElement from './Column';

/**
 * Adaptive Cards ColumnSet要素
 * 列レイアウトを定義するためのコンテナ
 * 
 * サポートするプロパティ:
 * - columns: Column要素の配列 (必須)
 * - spacing: 要素間のスペーシング
 * - separator: 区切り線の表示
 */

const ColumnSetElement = ({ element, theme, renderElement }) => {
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

  // 列の幅を計算
  const calculateColumnWidths = (columns) => {
    const totalColumns = columns.length;
    const autoColumns = columns.filter(col => col.width === 'Auto' || !col.width);
    const stretchColumns = columns.filter(col => col.width === 'Stretch');
    const fixedColumns = columns.filter(col => 
      col.width && col.width !== 'Auto' && col.width !== 'Stretch'
    );

    // 固定幅の合計を計算
    let fixedWidth = 0;
    fixedColumns.forEach(col => {
      if (typeof col.width === 'string' && col.width.endsWith('px')) {
        fixedWidth += parseInt(col.width.replace('px', ''));
      } else if (typeof col.width === 'number') {
        fixedWidth += col.width;
      }
    });

    // 残りの幅を計算（Auto + Stretchで分割）
    const remainingColumns = autoColumns.length + stretchColumns.length;
    
    return columns.map(col => {
      if (col.width === 'Stretch' || !col.width) {
        return { flex: 1 };
      } else if (col.width === 'Auto') {
        return { flexShrink: 1, flexGrow: 0 };
      } else if (typeof col.width === 'string' && col.width.endsWith('px')) {
        return { width: parseInt(col.width.replace('px', '')) };
      } else if (typeof col.width === 'number') {
        return { width: col.width };
      } else {
        return { flex: 1 };
      }
    });
  };

  const marginTop = getSpacingStyle(element.spacing);
  const columnWidths = calculateColumnWidths(element.columns || []);

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

  return (
    <View style={containerStyle}>
      <View style={styles.row}>
        {element.columns && element.columns.map((column, index) => (
          <View 
            key={index} 
            style={[
              styles.column,
              columnWidths[index],
              index > 0 && styles.columnSpacing
            ]}
          >
            <ColumnElement
              element={column}
              theme={paperTheme}
              renderElement={renderElement}
            />
          </View>
        ))}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginVertical: 2,
  },
  row: {
    flexDirection: 'row',
    alignItems: 'stretch',
  },
  column: {
    minHeight: 0, // Flexboxの高さ問題を回避
  },
  columnSpacing: {
    marginLeft: 8, // 列間のスペーシング
  },
});

export default ColumnSetElement;