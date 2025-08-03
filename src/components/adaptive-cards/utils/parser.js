/**
 * Adaptive Cards JSON パースユーティリティ
 */

/**
 * Adaptive CardのJSONデータを解析・正規化
 * @param {Object} rawCardData - 生のJSONデータ
 * @returns {Object} 正規化されたカードデータ
 */
export const parseAdaptiveCard = (rawCardData) => {
  if (!rawCardData) {
    throw new Error('Card data is required');
  }

  // 基本構造の正規化
  const cardData = {
    type: rawCardData.type,
    $schema: rawCardData.$schema,
    version: rawCardData.version || '1.3',
    body: rawCardData.body || [],
    actions: rawCardData.actions || [],
    ...extractCardProperties(rawCardData)
  };

  // 要素の解析
  cardData.body = cardData.body.map(element => parseElement(element));
  
  // アクションの解析
  cardData.actions = cardData.actions.map(action => parseAction(action));

  return cardData;
};

/**
 * カードレベルのプロパティ抽出
 */
const extractCardProperties = (cardData) => {
  const properties = {};
  
  // 背景画像
  if (cardData.backgroundImage) {
    properties.backgroundImage = cardData.backgroundImage;
  }
  
  // 最小高さ
  if (cardData.minHeight) {
    properties.minHeight = cardData.minHeight;
  }
  
  // 垂直コンテンツ配置
  if (cardData.verticalContentAlignment) {
    properties.verticalContentAlignment = cardData.verticalContentAlignment;
  }

  return properties;
};

/**
 * 要素の解析・正規化
 * @param {Object} element - 要素データ
 * @returns {Object} 正規化された要素データ
 */
export const parseElement = (element) => {
  if (!element || !element.type) {
    throw new Error('Element type is required');
  }

  const baseElement = {
    type: element.type,
    id: element.id,
    spacing: parseSpacing(element.spacing),
    separator: element.separator || false,
    height: element.height || 'auto',
    ...extractCommonProperties(element)
  };

  // 要素タイプ別の解析
  switch (element.type) {
    case 'TextBlock':
      return parseTextBlock(element, baseElement);
    
    case 'Container':
      return parseContainer(element, baseElement);
    
    case 'ColumnSet':
      return parseColumnSet(element, baseElement);
    
    case 'Column':
      return parseColumn(element, baseElement);
    
    case 'Input.Text':
      return parseInputText(element, baseElement);
    
    case 'Input.Toggle':
      return parseInputToggle(element, baseElement);
    
    default:
      return baseElement;
  }
};

/**
 * 共通プロパティの抽出
 */
const extractCommonProperties = (element) => {
  const properties = {};
  
  // 表示/非表示
  if (element.isVisible !== undefined) {
    properties.isVisible = element.isVisible;
  }
  
  // 必須項目
  if (element.requires !== undefined) {
    properties.requires = element.requires;
  }

  return properties;
};

/**
 * TextBlock要素の解析
 */
const parseTextBlock = (element, baseElement) => {
  return {
    ...baseElement,
    text: element.text || '',
    color: parseColor(element.color),
    fontType: element.fontType || 'Default',
    horizontalAlignment: element.horizontalAlignment || 'Left',
    isSubtle: element.isSubtle || false,
    maxLines: element.maxLines,
    size: parseSize(element.size),
    weight: parseWeight(element.weight),
    wrap: element.wrap || false
  };
};

/**
 * Container要素の解析
 */
const parseContainer = (element, baseElement) => {
  return {
    ...baseElement,
    items: element.items ? element.items.map(item => parseElement(item)) : [],
    style: element.style || 'Default',
    verticalContentAlignment: element.verticalContentAlignment || 'Top',
    bleed: element.bleed || false
  };
};

/**
 * ColumnSet要素の解析
 */
const parseColumnSet = (element, baseElement) => {
  return {
    ...baseElement,
    columns: element.columns ? element.columns.map(column => parseElement(column)) : []
  };
};

/**
 * Column要素の解析
 */
const parseColumn = (element, baseElement) => {
  return {
    ...baseElement,
    items: element.items ? element.items.map(item => parseElement(item)) : [],
    width: element.width || 'Auto',
    verticalContentAlignment: element.verticalContentAlignment || 'Top'
  };
};

/**
 * Input.Text要素の解析
 */
const parseInputText = (element, baseElement) => {
  return {
    ...baseElement,
    placeholder: element.placeholder || '',
    value: element.value || '',
    maxLength: element.maxLength,
    isMultiline: element.isMultiline || false,
    style: element.style || 'Text'
  };
};

/**
 * Input.Toggle要素の解析
 */
const parseInputToggle = (element, baseElement) => {
  return {
    ...baseElement,
    title: element.title || '',
    value: element.value || 'false',
    valueOn: element.valueOn || 'true',
    valueOff: element.valueOff || 'false'
  };
};

/**
 * アクションの解析
 * @param {Object} action - アクションデータ
 * @returns {Object} 正規化されたアクションデータ
 */
export const parseAction = (action) => {
  const baseAction = {
    type: action.type,
    title: action.title || '',
    id: action.id
  };

  switch (action.type) {
    case 'Action.Submit':
      return {
        ...baseAction,
        data: action.data || {}
      };
    
    default:
      return baseAction;
  }
};

/**
 * スペーシング値の正規化
 */
const parseSpacing = (spacing) => {
  if (!spacing) return 'Default';
  
  const validSpacings = ['None', 'Small', 'Default', 'Medium', 'Large', 'ExtraLarge', 'Padding'];
  return validSpacings.includes(spacing) ? spacing : 'Default';
};

/**
 * 色の正規化
 */
const parseColor = (color) => {
  if (!color) return 'Default';
  
  const validColors = ['Default', 'Dark', 'Light', 'Accent', 'Good', 'Warning', 'Attention'];
  return validColors.includes(color) ? color : 'Default';
};

/**
 * サイズの正規化
 */
const parseSize = (size) => {
  if (!size) return 'Default';
  
  const validSizes = ['Small', 'Default', 'Medium', 'Large', 'ExtraLarge'];
  return validSizes.includes(size) ? size : 'Default';
};

/**
 * フォントウェイトの正規化
 */
const parseWeight = (weight) => {
  if (!weight) return 'Default';
  
  const validWeights = ['Lighter', 'Default', 'Bolder'];
  return validWeights.includes(weight) ? weight : 'Default';
};