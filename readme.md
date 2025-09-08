# AquaSync

Arduino 水分センサーと妖精キャラクター「エモたん」を使った植物監視システム

## 概要

植物の水分状態を監視し、可愛い妖精キャラクターが状況を教えてくれる Web アプリです。

## 主な機能

- Arduino 水分センサーによるリアルタイム監視
- 妖精キャラクター「エモたん」の 5 種類の表情
- 音声機能（ON/OFF 切り替え可能）
- LINE 通知
- AI 生成メッセージ（Gemini API）
- Web ダッシュボード（Render 上で稼働）

## 技術構成

- **Backend**: Python Flask + Gunicorn
- **Frontend**: HTML/CSS/JavaScript
- **Cloud**: Render
- **IoT**: Arduino + Python
- **AI**: Google Gemini API
- **通知**: LINE Messaging API

## ファイル構成

```
emotan/
├── web_dashboard.py      # Webアプリケーション
├── local_sensor.py       # センサー制御 + LINE通知
├── AquaSync.ino          # Arduinoコード
├── requirements.txt      # Python依存関係
├── img/                  # 妖精キャラクター画像
├── voice/                # 音声ファイル
└── venv/                 # Python仮想環境
```

## デプロイ

Web アプリケーションはクラウドプラットフォームでデプロイ可能です。

## セットアップ

### ローカル環境

```bash
# 依存関係インストール
pip install -r requirements.txt

# 環境変数設定（.envファイル）
API_SECRET_KEY=your-secret-key
CLOUD_API_URL=your-cloud-url
CHANNEL_ACCESS_TOKEN=your-line-token
GEMINI_API_KEY=your-gemini-key
ARDUINO_PORT=your-arduino-port

# 実行
python web_dashboard.py
```

### Arduino

1. Arduino IDE で`AquaSync.ino`を開く
2. 必要なライブラリをインストール（Servo、TM1637Display）
3. Arduino にアップロード

### センサー監視

```bash
# センサー監視開始
python local_sensor.py
```

## API

### 主要エンドポイント

- `GET /` - ダッシュボード
- `GET /api/data` - センサーデータ取得
- `POST /api/update` - データ更新（Bearer 認証必要）

### データ形式

```json
{
  "raw_value": 450,
  "percentage": 75,
  "status": "yellow",
  "character_message": "75%でそこそこ元気だよ〜！",
  "character_face": "yousei2"
}
```

## 今後の予定

- データベース追加
- 履歴データの保存・グラフ表示
- モバイルアプリ対応
- 複数センサー対応

---

**Project Status**: Ready for Development
