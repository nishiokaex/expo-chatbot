/**
 * Adaptive Cards JSON スキーマ検証ユーティリティ
 */

/**
 * Adaptive Cardの基本検証
 * @param {Object} cardData - Adaptive Cardデータ
 * @returns {boolean} 検証結果
 */
export const validateCard = (cardData) => {
  if (!cardData || typeof cardData !== 'object') {
    return false;
  }

  // 必須フィールドの確認
  if (cardData.type !== 'AdaptiveCard') {
    console.warn('Invalid card type. Expected "AdaptiveCard"');
    return false;
  }

  // スキーマバージョンの確認
  if (!cardData.$schema || !cardData.version) {
    console.warn('Missing schema or version');
    return false;
  }

  // サポートバージョンの確認
  const supportedVersions = ['1.0', '1.1', '1.2', '1.3'];
  if (!supportedVersions.includes(cardData.version)) {
    console.warn(`Unsupported version: ${cardData.version}`);
    return false;
  }

  // bodyの存在確認
  if (!cardData.body || !Array.isArray(cardData.body)) {
    console.warn('Card body must be an array');
    return false;
  }

  return true;
};

/**
 * 要素の検証
 * @param {Object} element - 要素データ
 * @returns {boolean} 検証結果
 */
export const validateElement = (element) => {
  if (!element || typeof element !== 'object') {
    return false;
  }

  if (!element.type) {
    console.warn('Element missing type');
    return false;
  }

  // サポートする要素タイプ
  const supportedTypes = [
    'TextBlock',
    'Container',
    'ColumnSet',
    'Column',
    'Input.Text',
    'Input.Toggle'
  ];

  if (!supportedTypes.includes(element.type)) {
    console.warn(`Unsupported element type: ${element.type}`);
    return false;
  }

  return validateElementSpecific(element);
};

/**
 * 要素タイプ別の詳細検証
 * @param {Object} element - 要素データ
 * @returns {boolean} 検証結果
 */
const validateElementSpecific = (element) => {
  switch (element.type) {
    case 'TextBlock':
      return validateTextBlock(element);
    
    case 'Container':
      return validateContainer(element);
    
    case 'ColumnSet':
      return validateColumnSet(element);
    
    case 'Column':
      return validateColumn(element);
    
    case 'Input.Text':
      return validateInputText(element);
    
    case 'Input.Toggle':
      return validateInputToggle(element);
    
    default:
      return true;
  }
};

/**
 * TextBlock要素の検証
 */
const validateTextBlock = (element) => {
  if (!element.text || typeof element.text !== 'string') {
    console.warn('TextBlock missing text property');
    return false;
  }
  return true;
};

/**
 * Container要素の検証
 */
const validateContainer = (element) => {
  if (element.items && !Array.isArray(element.items)) {
    console.warn('Container items must be an array');
    return false;
  }
  return true;
};

/**
 * ColumnSet要素の検証
 */
const validateColumnSet = (element) => {
  if (!element.columns || !Array.isArray(element.columns)) {
    console.warn('ColumnSet missing columns array');
    return false;
  }
  
  if (element.columns.length === 0) {
    console.warn('ColumnSet must have at least one column');
    return false;
  }
  
  return true;
};

/**
 * Column要素の検証
 */
const validateColumn = (element) => {
  if (element.items && !Array.isArray(element.items)) {
    console.warn('Column items must be an array');
    return false;
  }
  return true;
};

/**
 * Input.Text要素の検証
 */
const validateInputText = (element) => {
  if (!element.id || typeof element.id !== 'string') {
    console.warn('Input.Text missing id property');
    return false;
  }
  return true;
};

/**
 * Input.Toggle要素の検証
 */
const validateInputToggle = (element) => {
  if (!element.id || typeof element.id !== 'string') {
    console.warn('Input.Toggle missing id property');
    return false;
  }
  
  if (!element.title || typeof element.title !== 'string') {
    console.warn('Input.Toggle missing title property');
    return false;
  }
  
  return true;
};

/**
 * アクションの検証
 * @param {Object} action - アクションデータ
 * @returns {boolean} 検証結果
 */
export const validateAction = (action) => {
  if (!action || typeof action !== 'object') {
    return false;
  }

  if (!action.type) {
    console.warn('Action missing type');
    return false;
  }

  const supportedActionTypes = ['Action.Submit'];
  
  if (!supportedActionTypes.includes(action.type)) {
    console.warn(`Unsupported action type: ${action.type}`);
    return false;
  }

  // Action.Submit固有の検証
  if (action.type === 'Action.Submit') {
    if (!action.title || typeof action.title !== 'string') {
      console.warn('Action.Submit missing title property');
      return false;
    }
  }

  return true;
};