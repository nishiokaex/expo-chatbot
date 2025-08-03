import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Card, Text, useTheme } from 'react-native-paper';

// Elements
import TextBlockElement from './elements/TextBlock';
import ContainerElement from './elements/Container';
import ColumnSetElement from './elements/ColumnSet';

// Inputs
import TextInputElement from './inputs/TextInput';
import ToggleInputElement from './inputs/ToggleInput';

// Actions
import SubmitAction from './actions/SubmitAction';

// Utils
import { validateCard } from './utils/validation';
import { parseAdaptiveCard } from './utils/parser';

/**
 * Microsoft Bot Framework Adaptive Cards Renderer for React Native Paper
 * 
 * サポートするAdaptive Cardsのサブセット仕様:
 * 
 * ## Elements (要素)
 * - TextBlock: テキスト表示（text, size, weight, color, wrap）
 * - Container: 他の要素をグループ化（items, style, spacing）
 * - ColumnSet: 列レイアウト（columns）
 * - Column: 列の定義（width, items）
 * 
 * ## Inputs (入力)
 * - Input.Text: テキスト入力（id, placeholder, value, maxLength）
 * - Input.Toggle: トグルスイッチ（id, title, value）
 * 
 * ## Actions (アクション)
 * - Action.Submit: データ送信（title, data）
 * 
 * ## Layout & Spacing
 * - spacing: None, Small, Default, Medium, Large, ExtraLarge, Padding
 * - verticalContentAlignment: Top, Center, Bottom
 * 
 * ## Styling
 * - colors: Default, Dark, Light, Accent, Good, Warning, Attention
 * - sizes: Small, Default, Medium, Large, ExtraLarge
 * - weights: Lighter, Default, Bolder
 * 
 * ## Schema Version
 * - "1.3": サポートするAdaptive Cardsスキーマバージョン
 */

const AdaptiveCard = ({ cardJson, onSubmit, style }) => {
  const theme = useTheme();

  // JSONが文字列の場合はパース
  const cardData = React.useMemo(() => {
    try {
      const data = typeof cardJson === 'string' ? JSON.parse(cardJson) : cardJson;
      return parseAdaptiveCard(data);
    } catch (error) {
      console.error('Adaptive Card JSON parse error:', error);
      return null;
    }
  }, [cardJson]);

  // カードの検証
  const isValid = React.useMemo(() => {
    if (!cardData) return false;
    return validateCard(cardData);
  }, [cardData]);

  // 入力値の状態管理
  const [inputValues, setInputValues] = React.useState({});

  // 入力値の更新
  const updateInputValue = React.useCallback((inputId, value) => {
    setInputValues(prev => ({
      ...prev,
      [inputId]: value
    }));
  }, []);

  // 要素をレンダリング
  const renderElement = React.useCallback((element, index) => {
    const commonProps = {
      key: index,
      theme,
      inputValues,
      updateInputValue,
    };

    switch (element.type) {
      case 'TextBlock':
        return <TextBlockElement {...commonProps} element={element} />;
      
      case 'Container':
        return (
          <ContainerElement 
            {...commonProps} 
            element={element}
            renderElement={renderElement}
          />
        );
      
      case 'ColumnSet':
        return (
          <ColumnSetElement 
            {...commonProps} 
            element={element}
            renderElement={renderElement}
          />
        );
      
      case 'Input.Text':
        return <TextInputElement {...commonProps} element={element} />;
      
      case 'Input.Toggle':
        return <ToggleInputElement {...commonProps} element={element} />;
      
      default:
        console.warn(`Unsupported element type: ${element.type}`);
        return null;
    }
  }, [theme, inputValues, updateInputValue]);

  // アクションをレンダリング
  const renderActions = React.useCallback(() => {
    if (!cardData.actions || cardData.actions.length === 0) {
      return null;
    }

    return (
      <View style={styles.actionsContainer}>
        {cardData.actions.map((action, index) => {
          switch (action.type) {
            case 'Action.Submit':
              return (
                <SubmitAction
                  key={index}
                  action={action}
                  theme={theme}
                  inputValues={inputValues}
                  onSubmit={onSubmit}
                />
              );
            
            default:
              console.warn(`Unsupported action type: ${action.type}`);
              return null;
          }
        })}
      </View>
    );
  }, [cardData, theme, inputValues, onSubmit]);

  // エラー時の表示
  if (!isValid || !cardData) {
    return (
      <Card style={[styles.errorCard, style]}>
        <Card.Content>
          <Text variant="bodyMedium" style={{ color: theme.colors.error }}>
            Adaptive Cardの読み込みに失敗しました
          </Text>
        </Card.Content>
      </Card>
    );
  }

  return (
    <Card style={[styles.card, style]} elevation={1}>
      <Card.Content style={styles.content}>
        {/* カード本体の要素 */}
        {cardData.body && cardData.body.map((element, index) => 
          renderElement(element, index)
        )}
        
        {/* アクション */}
        {renderActions()}
      </Card.Content>
    </Card>
  );
};

const styles = StyleSheet.create({
  card: {
    marginVertical: 4,
    borderRadius: 8,
  },
  errorCard: {
    marginVertical: 4,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#F44336',
  },
  content: {
    padding: 12,
  },
  actionsContainer: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    marginTop: 16,
    gap: 8,
  },
});

export default AdaptiveCard;