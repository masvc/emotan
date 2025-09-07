# AquaSync プロジェクト引き継ぎ資料

## 📋 プロジェクト概要

**AquaSync**は、IoT センサーを使用した水分監視システムです。Arduino センサーから水分データを取得し、リアルタイムでクラウドに送信。妖精キャラクター「えもたん」が可愛く状況を教えてくれる Web ダッシュボードを提供します。

### 🎯 主な機能

- **リアルタイム水分レベル監視** - Arduino センサーによる水分測定
- **妖精キャラクター「えもたん」** - 5 種類の表情で状況を表現
- **音声機能** - 状態変化時の音声再生（ON/OFF 切り替え可能）
- **LINE 通知** - 水分状態の変化を LINE で通知
- **AI 生成メッセージ** - Gemini API による自然なキャラクターセリフ
- **クラウドダッシュボード** - Render 上で稼働する Web アプリ
- **RESTful API** - データ取得・更新用 API
- **ローカルセンサー制御** - Arduino とのシリアル通信

## 🏗️ システム構成

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   ローカル側    │────│   クラウド側    │────│   ユーザー      │
│ (センサー+制御) │    │ (Webダッシュ    │    │ (ブラウザ)      │
│                 │    │  ボード)        │    │                 │
│ local_sensor.py │────│web_dashboard.py │────│ https://emotan. │
│ Arduino/センサー│    │ (Render)        │    │ onrender.com    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 🔧 技術スタック

- **Backend**: Python Flask + Gunicorn
- **Frontend**: HTML/CSS/JavaScript (妖精キャラクター + 音声機能)
- **Cloud**: Render (Web サービス)
- **IoT**: Arduino + Python (シリアル通信)
- **API**: RESTful JSON API + Bearer 認証
- **AI**: Google Gemini API (キャラクターセリフ生成)
- **通知**: LINE Messaging API
- **音声**: WAV 形式音声ファイル配信

## 📁 ファイル構成

```
emotan/
├── 📄 web_dashboard.py          # メインのWebアプリケーション
├── 📄 local_sensor.py           # ローカルセンサー制御 + LINE通知
├── 📄 local_sensor_test.py      # クラウド接続テスト用
├── 📄 AquaSync.ino              # Arduino水分センサーコード
├── 📄 requirements.txt          # Python依存関係
├── 📄 readme.md                 # プロジェクト資料
├── 🖼️ img/                      # 画像リソース
│   ├── back.jpg                 # 背景画像
│   ├── yousei1.png              # 妖精(通常)
│   ├── yousei2.png              # 妖精(警戒)
│   ├── yousei3.png              # 妖精(追加)
│   ├── yousei4.png              # 妖精(元気)
│   └── yousei5.png              # 妖精(怒り)
├── 🔊 voice/                    # 音声リソース
│   ├── arigatou.wav             # ありがとう音声
│   ├── kora.wav                 # こら音声
│   ├── nice.wav                 # ナイス音声
│   ├── ohayo.wav                # おはよう音声
│   ├── omizu.wav                # お水音声
│   ├── yatta.wav                # やった音声
│   └── yorosiku.wav             # よろしく音声
└── 📁 venv/                     # Python仮想環境
```

## 🚀 デプロイ済み環境

### 🌐 本番環境 (Render)

- **URL**: https://emotan.onrender.com
- **ステータス**: 稼働中 ✅
- **サーバー**: Gunicorn + Flask
- **自動デプロイ**: GitHub 連携

### 📊 主要エンドポイント

- `GET /` - ダッシュボード（妖精キャラクター表示）
- `GET /api/data` - センサーデータ取得
- `POST /api/update` - データ更新 (Bearer 認証必須)
- `GET /health` - ヘルスチェック
- `GET /img/<filename>` - 画像ファイル配信
- `GET /voice/<filename>` - 音声ファイル配信

## ⚙️ セットアップ手順

### 1. ローカル開発環境

```bash
# リポジトリクローン
git clone <repository-url>
cd emotan

# 仮想環境作成
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係インストール
pip install -r requirements.txt

# 環境変数設定（.envファイルを作成）
# 以下の環境変数を設定してください：
# API_SECRET_KEY=your-secret-key
# CLOUD_API_URL=https://emotan.onrender.com
# CHANNEL_ACCESS_TOKEN=your-line-token
# GEMINI_API_KEY=your-gemini-key
# ARDUINO_PORT=/dev/tty.usbserial-xxxxx

# ローカル実行
python web_dashboard.py
```

### 2. Arduino セットアップ

```bash
# Arduino IDEでAquaSync.inoを開く
# 必要なライブラリをインストール：
# - Servo
# - TM1637Display

# Arduinoにコードをアップロード
# シリアルモニタで動作確認
```

### 3. センサー接続 (ローカル側)

```bash
# クラウド接続テスト
python local_sensor_test.py

# センサー監視開始（LINE通知付き）
python local_sensor.py
```

## 🌐 Render デプロイ手順

### 初回デプロイ

1. Render アカウント作成
2. GitHub 連携
3. Web Service 作成
4. 以下の設定:

```
Build Command: pip install -r requirements.txt
Start Command: gunicorn --bind 0.0.0.0:$PORT web_dashboard:app
```

### Environment Variables

```
API_SECRET_KEY=your-secret-key
RENDER_EXTERNAL_URL=https://emotan.onrender.com
```

### 更新デプロイ

```bash
git add .
git commit -m "Update message"
git push origin main  # 自動デプロイされます
```

## 📡 API 仕様

### GET /api/data

センサーデータを取得

**レスポンス例:**

```json
{
  "raw_value": 450,
  "percentage": 75,
  "status": "yellow",
  "last_update": "2025-01-15T12:30:45",
  "message": "🟡 植物の水分は適度 (12:30)\n💧 水分レベル: 75%\n✅ 良好な状態です",
  "character_message": "75%でそこそこ元気だよ〜！あなたのおかげだね♪",
  "character_face": "yousei2"
}
```

### POST /api/update

センサーデータを更新 (要 API Key)

**リクエスト例:**

```json
{
  "raw_value": 450,
  "percentage": 75,
  "status": "yellow",
  "message": "🟡 植物の水分は適度 (12:30)\n💧 水分レベル: 75%\n✅ 良好な状態です",
  "character_message": "75%でそこそこ元気だよ〜！あなたのおかげだね♪",
  "character_face": "yousei2"
}
```

**ヘッダー:**

```
Authorization: Bearer your-api-secret-key
Content-Type: application/json
```

## 🔍 監視とトラブルシューティング

### ログ確認

```bash
# Renderログ
https://dashboard.render.com → Logs タブ

# ローカルログ
tail -f console.log
```

### よくある問題

#### 1. デプロイタイムアウト

**症状**: Render deploy 時にタイムアウト
**解決**: Start Command を確認

```bash
# ❌ 間違い
python web_dashboard.py

# ✅ 正解
gunicorn --bind 0.0.0.0:$PORT web_dashboard:app
```

#### 2. API 認証エラー

**症状**: 401 Unauthorized
**解決**: Bearer 認証を確認

```python
headers = {'Authorization': 'Bearer your-secret-key'}
```

#### 3. センサー接続エラー

**症状**: シリアル通信失敗
**解決**: ポート確認

```python
# デバイス確認
ls /dev/tty*  # Mac/Linux
# デバイスマネージャー確認 (Windows)
```

### パフォーマンス監視

- **応答時間**: < 2 秒
- **稼働率**: 99%+
- **メモリ使用量**: < 512MB

## 📈 今後の改善案

### 🔧 技術的改善

- [ ] データベース追加 (PostgreSQL)
- [ ] 履歴データの保存・グラフ表示
- [ ] リアルタイム通知 (WebSocket)
- [ ] モバイルアプリ対応
- [ ] Docker 化
- [ ] 複数センサー対応
- [ ] 自動水やりシステム連携

### 🎨 UI/UX 改善

- [ ] レスポンシブデザイン
- [ ] ダークモード
- [ ] グラフ表示機能
- [ ] アラート設定
- [ ] キャラクターアニメーション
- [ ] 音声設定の永続化

### 🔒 セキュリティ強化

- [ ] HTTPS 強制
- [ ] Rate limiting
- [ ] ユーザー認証
- [ ] API 版管理

## 📞 サポート情報

### 🔗 重要なリンク

- **本番サイト**: https://emotan.onrender.com
- **Render Dashboard**: https://dashboard.render.com
- **GitHub**: <repository-url>

### 📱 緊急連絡先

- **開発者**: [連絡先情報]
- **Render サポート**: https://render.com/docs

### 📚 参考資料

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Gunicorn Documentation](https://gunicorn.org/)
- [Render Documentation](https://render.com/docs)

---

## 📝 更新履歴

| 日付       | バージョン | 変更内容                             |
| ---------- | ---------- | ------------------------------------ |
| 2025-01-15 | v1.0       | 初回リリース、Render デプロイ完了    |
| 2025-01-15 | v1.1       | Gunicorn 本番サーバー導入            |
| 2025-01-15 | v1.2       | 音声機能、LINE 通知、Gemini API 追加 |
| 2025-01-15 | v1.3       | Arduino 統合、5 種類キャラクター対応 |

---

**Last Updated**: 2025-01-15  
**Document Version**: 1.3  
**Project Status**: Production Ready ✅
