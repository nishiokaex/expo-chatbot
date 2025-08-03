/**
 * Adaptive Cards使用例
 * 様々なカードレイアウトのサンプル
 */

// 基本的なテキスト表示カード
export const basicTextCard = {
  type: 'AdaptiveCard',
  $schema: 'http://adaptivecards.io/schemas/adaptive-card.json',
  version: '1.3',
  body: [
    {
      type: 'TextBlock',
      text: 'こんにちは！',
      size: 'Large',
      weight: 'Bolder',
      color: 'Accent'
    },
    {
      type: 'TextBlock',
      text: 'これは基本的なAdaptive Cardの例です。',
      wrap: true
    }
  ]
};

// フォーム入力カード
export const formCard = {
  type: 'AdaptiveCard',
  $schema: 'http://adaptivecards.io/schemas/adaptive-card.json',
  version: '1.3',
  body: [
    {
      type: 'TextBlock',
      text: 'ユーザー情報入力',
      size: 'Medium',
      weight: 'Bolder'
    },
    {
      type: 'Container',
      style: 'Emphasis',
      items: [
        {
          type: 'Input.Text',
          id: 'name',
          placeholder: '名前を入力してください',
          maxLength: 50
        },
        {
          type: 'Input.Text',
          id: 'email',
          placeholder: 'メールアドレス',
          style: 'Email'
        },
        {
          type: 'Input.Toggle',
          id: 'newsletter',
          title: 'ニュースレターの購読',
          value: 'false'
        }
      ]
    }
  ],
  actions: [
    {
      type: 'Action.Submit',
      title: '送信',
      data: {
        formType: 'userInfo'
      }
    }
  ]
};

// 列レイアウトカード
export const columnLayoutCard = {
  type: 'AdaptiveCard',
  $schema: 'http://adaptivecards.io/schemas/adaptive-card.json',
  version: '1.3',
  body: [
    {
      type: 'TextBlock',
      text: '商品比較',
      size: 'Large',
      weight: 'Bolder',
      horizontalAlignment: 'Center'
    },
    {
      type: 'ColumnSet',
      columns: [
        {
          type: 'Column',
          width: 'Auto',
          items: [
            {
              type: 'TextBlock',
              text: '商品A',
              weight: 'Bolder'
            },
            {
              type: 'TextBlock',
              text: '価格: ¥1,000',
              color: 'Good'
            },
            {
              type: 'TextBlock',
              text: '在庫: あり',
              isSubtle: true
            }
          ]
        },
        {
          type: 'Column',
          width: 'Auto',
          items: [
            {
              type: 'TextBlock',
              text: '商品B',
              weight: 'Bolder'
            },
            {
              type: 'TextBlock',
              text: '価格: ¥1,500',
              color: 'Warning'
            },
            {
              type: 'TextBlock',
              text: '在庫: 少量',
              isSubtle: true
            }
          ]
        }
      ]
    }
  ],
  actions: [
    {
      type: 'Action.Submit',
      title: '商品Aを選択',
      data: { productId: 'A' }
    },
    {
      type: 'Action.Submit',
      title: '商品Bを選択',
      data: { productId: 'B' }
    }
  ]
};

// アンケートカード
export const surveyCard = {
  type: 'AdaptiveCard',
  $schema: 'http://adaptivecards.io/schemas/adaptive-card.json',
  version: '1.3',
  body: [
    {
      type: 'TextBlock',
      text: 'サービス満足度調査',
      size: 'Medium',
      weight: 'Bolder'
    },
    {
      type: 'TextBlock',
      text: 'ご利用いただきありがとうございます。簡単なアンケートにお答えください。',
      wrap: true,
      spacing: 'Medium'
    },
    {
      type: 'Container',
      items: [
        {
          type: 'Input.Text',
          id: 'feedback',
          placeholder: 'ご意見・ご感想をお聞かせください',
          isMultiline: true,
          maxLength: 500
        },
        {
          type: 'Input.Toggle',
          id: 'recommend',
          title: '他の人にもこのサービスを推薦しますか？',
          value: 'false'
        },
        {
          type: 'Input.Toggle',
          id: 'updates',
          title: 'サービス更新情報を受け取る',
          value: 'true'
        }
      ]
    }
  ],
  actions: [
    {
      type: 'Action.Submit',
      title: 'アンケートを送信',
      data: {
        surveyType: 'satisfaction'
      }
    }
  ]
};

// エラー表示カード
export const errorCard = {
  type: 'AdaptiveCard',
  $schema: 'http://adaptivecards.io/schemas/adaptive-card.json',
  version: '1.3',
  body: [
    {
      type: 'Container',
      style: 'Attention',
      items: [
        {
          type: 'TextBlock',
          text: 'エラーが発生しました',
          size: 'Medium',
          weight: 'Bolder',
          color: 'Attention'
        },
        {
          type: 'TextBlock',
          text: 'リクエストの処理中に問題が発生しました。もう一度お試しください。',
          wrap: true
        }
      ]
    }
  ],
  actions: [
    {
      type: 'Action.Submit',
      title: '再試行',
      data: {
        action: 'retry'
      }
    }
  ]
};

// 成功メッセージカード
export const successCard = {
  type: 'AdaptiveCard',
  $schema: 'http://adaptivecards.io/schemas/adaptive-card.json',
  version: '1.3',
  body: [
    {
      type: 'Container',
      style: 'Good',
      items: [
        {
          type: 'TextBlock',
          text: '✅ 処理が完了しました',
          size: 'Medium',
          weight: 'Bolder',
          color: 'Good'
        },
        {
          type: 'TextBlock',
          text: 'ご依頼いただいた内容を正常に処理いたしました。',
          wrap: true
        }
      ]
    }
  ]
};