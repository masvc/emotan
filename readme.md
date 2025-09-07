# AquaSync プロジェクト引き継ぎ資料

## 📋 プロジェクト概要

**AquaSync**は、IoT センサーを使用した水分監視システムです。センサーデータをリアルタイムでクラウドに送信し、妖精キャラクター「えもたん」が可愛く状況を教えてくれる Web ダッシュボードを提供します。

### 🎯 主な機能

- リアルタイム水分レベル監視
- 妖精キャラクターによる状況表示
- クラウドダッシュボード（Render）
- RESTful API
- ローカルセンサー制御

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
- **Frontend**: HTML/CSS/JavaScript (妖精キャラクター)
- **Cloud**: Render (Web サービス)
- **IoT**: Python (シリアル通信)
- **API**: RESTful JSON API

## 📁 ファイル構成

```
emotan/
├── 📄 web_dashboard.py          # メインのWebアプリケーション
├── 📄 local_sensor.py           # ローカルセンサー制御
├── 📄 local_sensor_test.py      # センサーテスト用
├── 📄 requirements.txt          # Python依存関係
├── 📄 Procfile                  # Render用起動設定
├── 📄 .env                      # 環境変数 (ローカル用)
├── 📄 .gitignore                # Git除外設定
└── 🖼️ img/                      # 画像リソース
    ├── back.jpg                 # 背景画像
    ├── yousei1.png              # 妖精(通常)
    ├── yousei2.png              # 妖精(警戒)
    └── yousei4.png              # 妖精(元気)
```

## 🚀 デプロイ済み環境

### 🌐 本番環境 (Render)

- **URL**: https://emotan.onrender.com
- **ステータス**: 稼働中 ✅
- **サーバー**: Gunicorn + Flask
- **自動デプロイ**: GitHub 連携

### 📊 主要エンドポイント

- `GET /` - ダッシュボード
- `GET /api/data` - センサーデータ取得
- `POST /api/update` - データ更新 (要認証)
- `GET /health` - ヘルスチェック

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

# 環境変数設定
cp .env.example .env  # .envファイルを編集

# ローカル実行
python web_dashboard.py
```

### 2. センサー接続 (ローカル側)

```bash
# センサーテスト
python local_sensor_test.py

# センサー監視開始
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
  "moisture": 75,
  "status": "yellow",
  "last_update": "2025-09-07T04:51:03",
  "message": "75%でそこそこ元気だよ〜！",
  "character": "yousei2.png"
}
```

### POST /api/update

センサーデータを更新 (要 API Key)

**リクエスト例:**

```json
{
  "moisture": 75,
  "status": "yellow",
  "message": "水分75%でそこそこ元気だよ〜！"
}
```

**ヘッダー:**

```
X-API-Key: your-api-secret-key
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

**症状**: 403 Forbidden
**解決**: API Key を確認

```python
headers = {'X-API-Key': 'your-secret-key'}
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
- [ ] 履歴データの保存
- [ ] リアルタイム通知 (WebSocket)
- [ ] モバイルアプリ対応
- [ ] Docker 化

### 🎨 UI/UX 改善

- [ ] レスポンシブデザイン
- [ ] ダークモード
- [ ] グラフ表示機能
- [ ] アラート設定
- [ ] 複数センサー対応

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

| 日付       | バージョン | 変更内容                          |
| ---------- | ---------- | --------------------------------- |
| 2025-09-07 | v1.0       | 初回リリース、Render デプロイ完了 |
| 2025-09-07 | v1.1       | Gunicorn 本番サーバー導入         |

---

**Last Updated**: 2025-09-07  
**Document Version**: 1.0  
**Project Status**: Production Ready ✅
