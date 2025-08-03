/**
 * Adaptive Cards機能のテストスイート
 * React Native Paper統合テスト
 */

import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import { PaperProvider } from 'react-native-paper';

// Adaptive Cards関連コンポーネント
import AdaptiveCard from '../src/components/adaptive-cards/AdaptiveCard';
import TextBlockElement from '../src/components/adaptive-cards/elements/TextBlock';
import ContainerElement from '../src/components/adaptive-cards/elements/Container';
import ColumnSetElement from '../src/components/adaptive-cards/elements/ColumnSet';
import ColumnElement from '../src/components/adaptive-cards/elements/Column';
import TextInputElement from '../src/components/adaptive-cards/inputs/TextInput';
import ToggleInputElement from '../src/components/adaptive-cards/inputs/ToggleInput';
import SubmitAction from '../src/components/adaptive-cards/actions/SubmitAction';

// ユーティリティ
import { validateCard, validateElement } from '../src/components/adaptive-cards/utils/validation';
import { parseAdaptiveCard, parseElement } from '../src/components/adaptive-cards/utils/parser';

// テスト用のラッパーコンポーネント
const TestWrapper = ({ children }) => (
  <PaperProvider>
    {children}
  </PaperProvider>
);

describe('Adaptive Cards - バリデーション機能', () => {
  test('有効なAdaptive Cardを検証', () => {
    const validCard = {
      type: 'AdaptiveCard',
      $schema: 'http://adaptivecards.io/schemas/adaptive-card.json',
      version: '1.3',
      body: [
        {
          type: 'TextBlock',
          text: 'Hello World'
        }
      ]
    };

    expect(validateCard(validCard)).toBe(true);
  });

  test('無効なAdaptive Cardを検証', () => {
    const invalidCard = {
      type: 'InvalidCard',
      body: []
    };

    expect(validateCard(invalidCard)).toBe(false);
  });

  test('サポートされていないバージョンを検証', () => {
    const unsupportedVersionCard = {
      type: 'AdaptiveCard',
      $schema: 'http://adaptivecards.io/schemas/adaptive-card.json',
      version: '2.0',
      body: []
    };

    expect(validateCard(unsupportedVersionCard)).toBe(false);
  });

  test('TextBlock要素の検証', () => {
    const validTextBlock = {
      type: 'TextBlock',
      text: 'Valid text'
    };

    const invalidTextBlock = {
      type: 'TextBlock'
    };

    expect(validateElement(validTextBlock)).toBe(true);
    expect(validateElement(invalidTextBlock)).toBe(false);
  });
});

describe('Adaptive Cards - パース機能', () => {
  test('基本的なAdaptive Cardをパース', () => {
    const cardData = {
      type: 'AdaptiveCard',
      version: '1.3',
      body: [
        {
          type: 'TextBlock',
          text: 'Hello World',
          size: 'Large'
        }
      ]
    };

    const parsed = parseAdaptiveCard(cardData);
    
    expect(parsed.type).toBe('AdaptiveCard');
    expect(parsed.version).toBe('1.3');
    expect(parsed.body).toHaveLength(1);
    expect(parsed.body[0].text).toBe('Hello World');
    expect(parsed.body[0].size).toBe('Large');
  });

  test('要素のデフォルト値を適用', () => {
    const element = {
      type: 'TextBlock',
      text: 'Test'
    };

    const parsed = parseElement(element);
    
    expect(parsed.size).toBe('Default');
    expect(parsed.weight).toBe('Default');
    expect(parsed.color).toBe('Default');
    expect(parsed.wrap).toBe(false);
  });
});

describe('Adaptive Cards - TextBlock要素', () => {
  test('基本的なTextBlockをレンダリング', () => {
    const element = {
      type: 'TextBlock',
      text: 'テストテキスト',
      size: 'Medium',
      weight: 'Bolder',
      color: 'Accent'
    };

    const { getByText } = render(
      <TestWrapper>
        <TextBlockElement element={element} />
      </TestWrapper>
    );

    expect(getByText('テストテキスト')).toBeTruthy();
  });

  test('isSubtleプロパティでスタイルが変更される', () => {
    const element = {
      type: 'TextBlock',
      text: 'Subtle text',
      isSubtle: true
    };

    const { getByText } = render(
      <TestWrapper>
        <TextBlockElement element={element} />
      </TestWrapper>
    );

    const textElement = getByText('Subtle text');
    expect(textElement.props.style.opacity).toBe(0.6);
  });
});

describe('Adaptive Cards - Container要素', () => {
  const mockRenderElement = jest.fn((element, index) => null);

  beforeEach(() => {
    mockRenderElement.mockClear();
  });

  test('Container要素をレンダリング', () => {
    const element = {
      type: 'Container',
      style: 'Emphasis',
      items: [
        { type: 'TextBlock', text: 'Item 1' },
        { type: 'TextBlock', text: 'Item 2' }
      ]
    };

    render(
      <TestWrapper>
        <ContainerElement 
          element={element} 
          renderElement={mockRenderElement}
        />
      </TestWrapper>
    );

    expect(mockRenderElement).toHaveBeenCalledTimes(2);
  });
});

describe('Adaptive Cards - 入力要素', () => {
  const mockUpdateInputValue = jest.fn();

  beforeEach(() => {
    mockUpdateInputValue.mockClear();
  });

  test('TextInput要素をレンダリングして入力', () => {
    const element = {
      type: 'Input.Text',
      id: 'testInput',
      placeholder: 'テスト入力',
      value: ''
    };

    const { getByDisplayValue } = render(
      <TestWrapper>
        <TextInputElement 
          element={element}
          inputValues={{}}
          updateInputValue={mockUpdateInputValue}
        />
      </TestWrapper>
    );

    const input = getByDisplayValue('');
    fireEvent.changeText(input, 'テスト値');

    expect(mockUpdateInputValue).toHaveBeenCalledWith('testInput', 'テスト値');
  });

  test('Toggle入力要素をレンダリングして切り替え', () => {
    const element = {
      type: 'Input.Toggle',
      id: 'testToggle',
      title: 'テストトグル',
      value: 'false',
      valueOn: 'true',
      valueOff: 'false'
    };

    const { getByText } = render(
      <TestWrapper>
        <ToggleInputElement 
          element={element}
          inputValues={{}}
          updateInputValue={mockUpdateInputValue}
        />
      </TestWrapper>
    );

    expect(getByText('テストトグル')).toBeTruthy();
  });
});

describe('Adaptive Cards - ColumnSet/Column', () => {
  const mockRenderElement = jest.fn((element, index) => null);

  beforeEach(() => {
    mockRenderElement.mockClear();
  });

  test('ColumnSetをレンダリング', () => {
    const element = {
      type: 'ColumnSet',
      columns: [
        {
          type: 'Column',
          width: 'Auto',
          items: [{ type: 'TextBlock', text: 'Column 1' }]
        },
        {
          type: 'Column', 
          width: 'Stretch',
          items: [{ type: 'TextBlock', text: 'Column 2' }]
        }
      ]
    };

    render(
      <TestWrapper>
        <ColumnSetElement 
          element={element}
          renderElement={mockRenderElement}
        />
      </TestWrapper>
    );

    // 2つのColumnが正しくレンダリングされることを確認
    expect(mockRenderElement).toHaveBeenCalled();
  });
});

describe('Adaptive Cards - Action.Submit', () => {
  test('Submit アクションをレンダリング', () => {
    const action = {
      type: 'Action.Submit',
      title: '送信',
      data: { key: 'value' }
    };

    const mockOnSubmit = jest.fn();

    const { getByText } = render(
      <TestWrapper>
        <SubmitAction 
          action={action}
          inputValues={{ input1: 'test' }}
          onSubmit={mockOnSubmit}
        />
      </TestWrapper>
    );

    const button = getByText('送信');
    fireEvent.press(button);

    expect(mockOnSubmit).toHaveBeenCalledWith({
      action: action,
      data: { input1: 'test', key: 'value' },
      actionType: 'Action.Submit',
      actionId: action.id
    });
  });
});

describe('Adaptive Cards - 統合テスト', () => {
  test('完全なAdaptive Cardをレンダリング', () => {
    const cardJson = {
      type: 'AdaptiveCard',
      $schema: 'http://adaptivecards.io/schemas/adaptive-card.json',
      version: '1.3',
      body: [
        {
          type: 'TextBlock',
          text: 'フィードバックフォーム',
          size: 'Large',
          weight: 'Bolder'
        },
        {
          type: 'Container',
          items: [
            {
              type: 'Input.Text',
              id: 'name',
              placeholder: '名前を入力してください'
            },
            {
              type: 'Input.Toggle',
              id: 'subscribe',
              title: 'ニュースレターを購読する'
            }
          ]
        }
      ],
      actions: [
        {
          type: 'Action.Submit',
          title: '送信'
        }
      ]
    };

    const mockOnSubmit = jest.fn();

    const { getByText, getByDisplayValue } = render(
      <TestWrapper>
        <AdaptiveCard 
          cardJson={cardJson}
          onSubmit={mockOnSubmit}
        />
      </TestWrapper>
    );

    // タイトルが表示されることを確認
    expect(getByText('フィードバックフォーム')).toBeTruthy();
    
    // 入力フィールドが表示されることを確認
    expect(getByDisplayValue('')).toBeTruthy();
    
    // トグルが表示されることを確認
    expect(getByText('ニュースレターを購読する')).toBeTruthy();
    
    // 送信ボタンが表示されることを確認
    expect(getByText('送信')).toBeTruthy();
  });

  test('無効なJSONでエラー表示', () => {
    const invalidJson = null;

    const { getByText } = render(
      <TestWrapper>
        <AdaptiveCard cardJson={invalidJson} />
      </TestWrapper>
    );

    expect(getByText('Adaptive Cardの読み込みに失敗しました')).toBeTruthy();
  });

  test('JSONストリングからのパース', () => {
    const cardJsonString = JSON.stringify({
      type: 'AdaptiveCard',
      version: '1.3',
      body: [
        {
          type: 'TextBlock',
          text: 'JSON文字列からのテスト'
        }
      ]
    });

    const { getByText } = render(
      <TestWrapper>
        <AdaptiveCard cardJson={cardJsonString} />
      </TestWrapper>
    );

    expect(getByText('JSON文字列からのテスト')).toBeTruthy();
  });
});