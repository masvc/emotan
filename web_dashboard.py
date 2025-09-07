import os
from flask import Flask, render_template_string, jsonify, request, abort, send_file
from datetime import datetime

# Flaskアプリ設定
app = Flask(__name__)

# 環境変数から設定を取得
API_SECRET_KEY = os.getenv('API_SECRET_KEY', 'aquasync-secret-key-2024')

# グローバル変数でデータを保存（メモリ内ストレージ）
current_data = {
    'raw_value': 0,
    'percentage': 0,
    'status': 'unknown',
    'last_update': None,
    'message': 'データ待機中...',
    'character_message': 'データを受信中だよ〜！',
    'character_face': 'normal'
}

# HTML テンプレート（ビジュアルノベル風・大幅サイズアップ版）
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AquaSync 水分監視システム</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Hiragino Kaku Gothic Pro', 'ヒラギノ角ゴ Pro W3', Meiryo, 'メイリオ', Osaka, 'MS PGothic', sans-serif;
            background: url('/img/back.jpg') center center / cover no-repeat fixed;
            color: #333;
            line-height: 1.6;
            height: 100vh;
            overflow: hidden;
            position: relative;
        }
        
        /* サイドバー（右上） */
        .sidebar {
            position: fixed;
            top: 20px;
            right: 20px;
            width: 300px;
            background: rgba(255, 255, 255, 0.95);
            border: 3px solid #8B4513;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
            backdrop-filter: blur(8px);
            z-index: 20;
        }
        .sidebar-title {
            font-size: 24px;
            font-weight: bold;
            color: #8B4513;
            margin-bottom: 20px;
            text-align: center;
            border-bottom: 2px solid #8B4513;
            padding-bottom: 12px;
        }
        .status-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 18px;
            font-size: 20px;
        }
        .status-label {
            color: #555;
            display: flex;
            align-items: center;
            gap: 12px;
            font-weight: bold;
        }
        .status-label i {
            font-size: 24px;
            width: 30px;
            text-align: center;
        }
        .status-value {
            font-weight: bold;
            font-size: 22px;
        }
        .status-green .status-value { color: #28a745; }
        .status-yellow .status-value { color: #ffc107; }
        .status-red .status-value { color: #dc3545; }
        .status-unknown .status-value { color: #6c757d; }
        .progress-mini {
            width: 100%;
            height: 10px;
            background: #e9ecef;
            border-radius: 5px;
            overflow: hidden;
            margin-top: 8px;
        }
        .progress-mini-fill {
            height: 100%;
            transition: width 0.5s ease;
        }
        .connection-status-mini {
            font-size: 16px;
            text-align: center;
            margin-top: 15px;
            padding: 8px;
            border-radius: 8px;
            font-weight: bold;
        }
        .connection-status-mini.connected {
            background: #d4edda;
            color: #155724;
        }
        .connection-status-mini.disconnected {
            background: #f8d7da;
            color: #721c24;
        }
        
        /* キャラクター表示エリア */
        .character-area {
            position: fixed;
            bottom: 300px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 10;
        }
        .character-image {
            width: 800px;
            height: auto;
            filter: drop-shadow(0 0 30px rgba(0, 0, 0, 0.6));
            transition: all 0.3s ease;
        }
        .character-image.happy {
            filter: drop-shadow(0 0 30px rgba(255, 215, 0, 0.8));
        }
        .character-image.sad {
            filter: drop-shadow(0 0 30px rgba(255, 0, 0, 0.6));
        }
        
        /* 台詞ボックス */
        .dialogue-container {
            position: fixed;
            bottom: 30px;
            left: 30px;
            right: 30px;
            height: 250px;
            background: linear-gradient(to bottom, rgba(139, 69, 19, 0.95), rgba(101, 67, 33, 0.95));
            border-top: 4px solid #8B4513;
            border-radius: 20px;
            padding: 30px 60px;
            box-shadow: 0 -8px 25px rgba(0, 0, 0, 0.6);
            font-weight: bold;
        }
        .dialogue-box {
            width: 100%;
            height: 100%;
            background: rgba(255, 255, 255, 0.98);
            border: 3px solid #8B4513;
            border-radius: 18px;
            padding: 30px;
            position: relative;
            box-shadow: inset 0 0 15px rgba(139, 69, 19, 0.3);
        }
        .dialogue-text {
            font-size: 24px;
            line-height: 1.7;
            color: #333;
            overflow-y: auto;
            height: 100%;
            font-weight: bold;
        }
        .dialogue-name {
            position: absolute;
            top: -22px;
            left: 40px;
            background: #8B4513;
            color: white;
            padding: 10px 30px;
            border-radius: 22px;
            font-size: 18px;
            font-weight: bold;
        }
        
        /* 更新ボタン */
        .update-button {
            position: fixed;
            bottom: 300px;
            right: 50px;
            background: rgba(139, 69, 19, 0.9);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 30px;
            cursor: pointer;
            font-size: 18px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
            font-weight: bold;
        }
        .update-button:hover {
            background: rgba(139, 69, 19, 1);
            transform: scale(1.05);
        }
    </style>
    <script>
        let lastUpdateTime = new Date('{{ last_update or "1970-01-01" }}').getTime();
        
        function refreshData() {
            fetch('/api/data')
                .then(response => response.json())
                .then(data => {
                    // サイドバーの更新
                    document.getElementById('percentage').textContent = data.percentage + '%';
                    document.getElementById('raw-value').textContent = data.raw_value;
                    document.getElementById('status-text').textContent = getStatusText(data.status);
                    document.getElementById('last-update').textContent = data.last_update || 'データなし';
                    
                    // 台詞ボックスの更新
                    document.getElementById('dialogue-text').textContent = data.character_message || 'お疲れ様！';
                    
                    // キャラクター画像のエフェクト更新
                    updateCharacterEffect(data.character_face || data.status);
                    
                    // 接続状態の更新
                    updateConnectionStatusMini(data.last_update);
                    
                    // ステータスに応じてクラスを更新
                    const sidebar = document.getElementById('sidebar');
                    sidebar.className = 'sidebar status-' + data.status;
                    
                    // プログレスバーを更新
                    const progressFill = document.getElementById('progress-mini-fill');
                    progressFill.style.width = data.percentage + '%';
                    progressFill.className = 'progress-mini-fill status-' + data.status;
                });
        }
        
        function updateCharacterEffect(faceType) {
            const characterImg = document.getElementById('character-image');
            
            // クラスをリセット
            characterImg.className = 'character-image';
            
            // 画像ファイル名に基づいて画像を切り替え
            let imageSrc = '/img/yousei1.png'; // デフォルト
            
            switch(faceType) {
                case 'yousei1':
                    imageSrc = '/img/yousei1.png';
                    break;
                case 'yousei2':
                    imageSrc = '/img/yousei2.png';
                    break;
                case 'yousei4':
                    imageSrc = '/img/yousei4.png';
                    characterImg.classList.add('happy');
                    break;
                case 'yousei5':
                    imageSrc = '/img/yousei5.png';
                    characterImg.classList.add('sad');
                    break;
                case 'green':
                case 'happy':
                    imageSrc = '/img/yousei4.png';
                    characterImg.classList.add('happy');
                    break;
                case 'red':
                case 'sad':
                    imageSrc = '/img/yousei5.png';
                    characterImg.classList.add('sad');
                    break;
                default:
                    imageSrc = '/img/yousei1.png';
                    break;
            }
            
            // 画像を更新
            characterImg.src = imageSrc;
        }
        
        function updateConnectionStatusMini(lastUpdate) {
            const connectionStatus = document.getElementById('connection-status-mini');
            
            if (!lastUpdate) {
                connectionStatus.className = 'connection-status-mini disconnected';
                connectionStatus.textContent = '⚠️ データ待機中';
                return;
            }
            
            const updateTime = new Date(lastUpdate).getTime();
            const now = new Date().getTime();
            const timeDiff = (now - updateTime) / 1000; // 秒単位
            
            if (timeDiff > 60) { // 1分以上更新がない
                connectionStatus.className = 'connection-status-mini disconnected';
                connectionStatus.textContent = `⚠️ 接続切れ (${Math.floor(timeDiff/60)}分前)`;
            } else {
                connectionStatus.className = 'connection-status-mini connected';
                connectionStatus.textContent = '✅ 接続中';
            }
        }
        
        function getStatusText(status) {
            switch(status) {
                case 'green': return '良好';
                case 'yellow': return '適度';
                case 'red': return '不足';
                default: return '不明';
            }
        }
        
        // 15秒ごとに自動更新
        setInterval(refreshData, 15000);
        
        // ページ読み込み時に1回実行
        window.onload = function() {
            refreshData();
            updateConnectionStatusMini('{{ last_update }}');
        };
    </script>
</head>
<body>
    <!-- サイドバー（右上） -->
    <div id="sidebar" class="sidebar status-{{ status }}">
        <div class="sidebar-title">水分データ</div>
        
        <div class="status-item">
            <span class="status-label">
                <i class="fas fa-tint"></i>
                水分レベル
            </span>
            <span id="percentage" class="status-value">{{ percentage }}%</span>
        </div>
        
        <div class="progress-mini">
            <div id="progress-mini-fill" class="progress-mini-fill status-{{ status }}" 
                 style="width: {{ percentage }}%"></div>
        </div>
        
        <div class="status-item">
            <span class="status-label">
                <i class="fas fa-chart-line"></i>
                センサー値
            </span>
            <span id="raw-value" class="status-value">{{ raw_value }}</span>
        </div>
        
        <div class="status-item">
            <span class="status-label">
                <i class="fas fa-heart"></i>
                ステータス
            </span>
            <span id="status-text" class="status-value">
                {% if status == 'green' %}良好
                {% elif status == 'yellow' %}適度
                {% elif status == 'red' %}不足
                {% else %}不明{% endif %}
            </span>
        </div>
        
        <div class="status-item">
            <span class="status-label">
                <i class="fas fa-clock"></i>
                最終更新
            </span>
            <span id="last-update" class="status-value" style="font-size: 16px;">{{ last_update or 'データなし' }}</span>
        </div>
        
        <div id="connection-status-mini" class="connection-status-mini connected">
            ✅ 接続中
        </div>
    </div>
    
    <!-- キャラクター表示エリア -->
    <div class="character-area">
        <img id="character-image" src="/img/yousei1.png" alt="植物妖精" class="character-image {{ character_face }}">
    </div>
    
    <!-- 更新ボタン -->
    <button class="update-button" onclick="refreshData()">
        <i class="fas fa-sync-alt"></i> 更新
    </button>
    
    <!-- 台詞ボックス -->
    <div class="dialogue-container">
        <div class="dialogue-box">
            <div class="dialogue-name">植物妖精からのメッセージ</div>
            <div id="dialogue-text" class="dialogue-text">
                {{ character_message or 'データを受信中だよ〜！' }}
            </div>
        </div>
    </div>
</body>
</html>
"""

def authenticate_request():
    """API リクエストの認証"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return False
    
    token = auth_header.split('Bearer ')[-1]
    return token == API_SECRET_KEY

@app.route('/')
def dashboard():
    """水分レベルダッシュボードを表示"""
    return render_template_string(HTML_TEMPLATE, **current_data)

@app.route('/api/data')
def get_data():
    """現在の水分データをJSON形式で返す"""
    return jsonify(current_data)

@app.route('/api/update', methods=['POST'])
def update_data():
    """ローカルセンサーからのデータを受信"""
    # 認証チェック
    if not authenticate_request():
        abort(401)
    
    try:
        # JSONデータを受信
        new_data = request.json
        if not new_data:
            return jsonify({'error': 'No data provided'}), 400
        
        # グローバルデータを更新
        global current_data
        current_data.update(new_data)
        
        # 更新時刻を記録
        current_data['last_update'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"📊 データ受信: {current_data['percentage']}% ({current_data['status']}) | {current_data['character_message']}")
        
        return jsonify({'status': 'success', 'message': 'Data updated successfully'})
        
    except Exception as e:
        print(f"データ更新エラー: {e}")
        return jsonify({'error': 'Failed to update data'}), 500

@app.route('/img/<filename>')
def serve_image(filename):
    """ローカル画像ファイルを配信"""
    image_path = os.path.join(os.getcwd(), 'img', filename)
    if os.path.exists(image_path):
        return send_file(image_path)
    else:
        abort(404)

@app.route('/health')
def health_check():
    """ヘルスチェック用エンドポイント"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'last_sensor_update': current_data.get('last_update'),
        'current_status': current_data.get('status', 'unknown')
    })

if __name__ == '__main__':
    print("🌐 AquaSync Cloud Dashboard 起動中...")
    print(f"🔐 API Secret Key: {'設定済み' if API_SECRET_KEY != 'aquasync-secret-key-2024' else '未設定'}")
    print("📊 ダッシュボード: /")
    print("🔌 API エンドポイント:")
    print("  - GET  /api/data - データ取得")
    print("  - POST /api/update - データ更新（要認証）")
    print("  - GET  /health - ヘルスチェック")
    
    # ポート設定（Render等のクラウド環境対応）
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    
    app.run(host=host, port=port, debug=False)