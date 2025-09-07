import os
from flask import Flask, render_template_string, jsonify, request, abort
from datetime import datetime

# Flaskアプリ設定
app = Flask(__name__)

# 環境変数から設定を取得
API_SECRET_KEY = os.getenv('API_SECRET_KEY', 'your-secret-api-key')

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

# HTML テンプレート（元のコードと同じ）
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
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background-color: #f8f9fa;
            color: #333;
            line-height: 1.6;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }
        .header {
            background: #2c3e50;
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            font-size: 28px;
            font-weight: 600;
            margin-bottom: 8px;
        }
        .header .subtitle {
            font-size: 16px;
            opacity: 0.9;
            font-weight: 400;
        }
        .content {
            padding: 30px;
        }
        .main-content {
            margin-bottom: 30px;
        }
        .status-overview {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }
        .character-section {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 6px;
            padding: 20px;
            text-align: center;
        }
        .character-title {
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 15px;
            color: #2c3e50;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .character-face {
            width: 70px;
            height: 70px;
            border-radius: 50%;
            margin: 0 auto 15px auto;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            transition: all 0.3s ease;
        }
        .character-face-happy {
            background: linear-gradient(135deg, #ffb3d6 0%, #ffc9e0 100%);
            border: 3px solid #ff69b4;
            box-shadow: 0 0 15px rgba(255, 105, 180, 0.3);
        }
        .character-face-normal {
            background: linear-gradient(135deg, #e8d5ff 0%, #f0e6ff 100%);
            border: 3px solid #9575cd;
            box-shadow: 0 0 10px rgba(149, 117, 205, 0.2);
        }
        .character-face-sad {
            background: linear-gradient(135deg, #ffcccb 0%, #ffe4e1 100%);
            border: 3px solid #ff6b6b;
            box-shadow: 0 0 10px rgba(255, 107, 107, 0.2);
        }
        .face-eyes {
            position: absolute;
            top: 20px;
            width: 100%;
            display: flex;
            justify-content: space-around;
            padding: 0 15px;
        }
        .eye {
            width: 10px;
            height: 12px;
            background: #333;
            border-radius: 50% 50% 50% 50% / 60% 60% 40% 40%;
            position: relative;
        }
        .eye::after {
            content: '';
            position: absolute;
            top: -3px;
            left: -2px;
            width: 14px;
            height: 6px;
            border: 2px solid #333;
            border-bottom: none;
            border-radius: 50% 50% 0 0;
        }
        .eye::before {
            content: '';
            position: absolute;
            top: 2px;
            left: 2px;
            width: 3px;
            height: 3px;
            background: white;
            border-radius: 50%;
        }
        .face-cheeks {
            position: absolute;
            top: 30px;
            width: 100%;
            display: flex;
            justify-content: space-between;
            padding: 0 8px;
        }
        .cheek {
            width: 12px;
            height: 8px;
            background: rgba(255, 182, 193, 0.6);
            border-radius: 50%;
        }
        .face-mouth {
            position: absolute;
            bottom: 15px;
            left: 50%;
            transform: translateX(-50%);
        }
        .mouth-happy {
            width: 25px;
            height: 12px;
            border: 2px solid #333;
            border-top: none;
            border-radius: 0 0 25px 25px;
        }
        .mouth-normal {
            width: 16px;
            height: 2px;
            background: #333;
            border-radius: 2px;
        }
        .mouth-sad {
            width: 25px;
            height: 12px;
            border: 2px solid #333;
            border-bottom: none;
            border-radius: 25px 25px 0 0;
            transform: translateX(-50%) rotate(180deg);
        }
        .face-bow {
            position: absolute;
            top: -8px;
            left: 50%;
            transform: translateX(-50%);
            width: 16px;
            height: 8px;
        }
        .face-bow::before {
            content: '';
            position: absolute;
            left: 0;
            width: 6px;
            height: 8px;
            background: #ff69b4;
            border-radius: 50% 0 50% 50%;
            transform: rotate(-20deg);
        }
        .face-bow::after {
            content: '';
            position: absolute;
            right: 0;
            width: 6px;
            height: 8px;
            background: #ff69b4;
            border-radius: 0 50% 50% 50%;
            transform: rotate(20deg);
        }
        .face-bow-center {
            position: absolute;
            left: 50%;
            top: 50%;
            transform: translate(-50%, -50%);
            width: 4px;
            height: 6px;
            background: #e91e63;
            border-radius: 2px;
        }
        .character-message {
            background: linear-gradient(135deg, #fff0f5 0%, #ffeef8 100%);
            border: 1px solid #ffb3d6;
            border-radius: 15px;
            padding: 8px 12px;
            font-size: 12px;
            color: #8e24aa;
            font-weight: 500;
            position: relative;
            margin-top: 10px;
        }
        .character-message::before {
            content: '';
            position: absolute;
            top: -6px;
            left: 50%;
            transform: translateX(-50%);
            width: 0;
            height: 0;
            border-left: 6px solid transparent;
            border-right: 6px solid transparent;
            border-bottom: 6px solid #ffb3d6;
        }
        .character-message::after {
            content: '';
            position: absolute;
            top: -5px;
            left: 50%;
            transform: translateX(-50%);
            width: 0;
            height: 0;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-bottom: 5px solid #fff0f5;
        }
        .metric-card {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 6px;
            padding: 20px;
            text-align: center;
        }
        .metric-icon {
            font-size: 24px;
            margin-bottom: 10px;
        }
        .metric-value {
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 5px;
        }
        .metric-label {
            font-size: 14px;
            color: #6c757d;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .main-status {
            background: white;
            border: 1px solid #e9ecef;
            border-radius: 6px;
            padding: 30px;
            text-align: center;
            margin-bottom: 30px;
        }
        .status-icon {
            font-size: 48px;
            margin-bottom: 20px;
        }
        .percentage {
            font-size: 56px;
            font-weight: 700;
            margin-bottom: 10px;
        }
        .status-message {
            font-size: 18px;
            margin-bottom: 25px;
            padding: 0 20px;
        }
        .progress-container {
            width: 100%;
            background: #e9ecef;
            border-radius: 4px;
            height: 12px;
            overflow: hidden;
            margin-bottom: 20px;
        }
        .progress-fill {
            height: 100%;
            transition: width 0.5s ease;
            border-radius: 4px;
        }
        .status-green .metric-icon { color: #28a745; }
        .status-green .status-icon { color: #28a745; }
        .status-green .percentage { color: #28a745; }
        .status-green .progress-fill { background: #28a745; }
        
        .status-yellow .metric-icon { color: #ffc107; }
        .status-yellow .status-icon { color: #ffc107; }
        .status-yellow .percentage { color: #ffc107; }
        .status-yellow .progress-fill { background: #ffc107; }
        
        .status-red .metric-icon { color: #dc3545; }
        .status-red .status-icon { color: #dc3545; }
        .status-red .percentage { color: #dc3545; }
        .status-red .progress-fill { background: #dc3545; }
        
        .status-unknown .metric-icon { color: #6c757d; }
        .status-unknown .status-icon { color: #6c757d; }
        .status-unknown .percentage { color: #6c757d; }
        .status-unknown .progress-fill { background: #6c757d; }
        
        .actions {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin-bottom: 30px;
        }
        .btn {
            background: #007bff;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: background-color 0.2s;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }
        .btn:hover {
            background: #0056b3;
        }
        .btn-secondary {
            background: #6c757d;
        }
        .btn-secondary:hover {
            background: #545b62;
        }
        .footer-info {
            background: #f8f9fa;
            padding: 20px;
            border-top: 1px solid #e9ecef;
            text-align: center;
            font-size: 14px;
            color: #6c757d;
        }
        .footer-info i {
            margin-right: 5px;
        }
        .connection-status {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            border-radius: 6px;
            padding: 15px;
            margin-bottom: 30px;
            text-align: center;
        }
        .connection-status.disconnected {
            background: #f8d7da;
            border: 1px solid #f5c6cb;
        }
        @media (max-width: 768px) {
            .main-content {
                grid-template-columns: 1fr;
            }
            .status-overview {
                grid-template-columns: 1fr;
            }
            .actions {
                flex-direction: column;
                align-items: center;
            }
        }
    </style>
    <script>
        let lastUpdateTime = new Date('{{ last_update or "1970-01-01" }}').getTime();
        
        function refreshData() {
            fetch('/api/data')
                .then(response => response.json())
                .then(data => {
                    // 基本データの更新
                    document.getElementById('percentage').textContent = data.percentage;
                    document.getElementById('percentage-main').textContent = data.percentage + '%';
                    document.getElementById('raw-value').textContent = data.raw_value;
                    document.getElementById('status-text').textContent = getStatusText(data.status);
                    document.getElementById('last-update').textContent = data.last_update || 'データなし';
                    
                    // キャラクターの更新
                    document.getElementById('character-message').textContent = data.character_message || 'お疲れ様！';
                    updateCharacterFace(data.character_face || data.status);
                    
                    // 接続状態の更新
                    updateConnectionStatus(data.last_update);
                    
                    // ステータスに応じてクラスを更新
                    const mainStatus = document.getElementById('main-status');
                    const metricCards = document.querySelectorAll('.metric-card');
                    
                    // 古いステータスクラスを削除
                    mainStatus.className = 'main-status status-' + data.status;
                    metricCards.forEach(card => {
                        card.className = 'metric-card status-' + data.status;
                    });
                    
                    // プログレスバーを更新
                    const progressFill = document.getElementById('progress-fill');
                    progressFill.style.width = data.percentage + '%';
                    progressFill.className = 'progress-fill status-' + data.status;
                    
                    // ステータスアイコンを更新
                    const statusIcon = document.getElementById('status-icon');
                    statusIcon.className = getStatusIcon(data.status);
                });
        }
        
        function updateConnectionStatus(lastUpdate) {
            const connectionStatus = document.getElementById('connection-status');
            const connectionText = document.getElementById('connection-text');
            
            if (!lastUpdate) {
                connectionStatus.className = 'connection-status disconnected';
                connectionText.textContent = '⚠️ ローカルセンサーからのデータ待機中...';
                return;
            }
            
            const updateTime = new Date(lastUpdate).getTime();
            const now = new Date().getTime();
            const timeDiff = (now - updateTime) / 1000; // 秒単位
            
            if (timeDiff > 60) { // 1分以上更新がない
                connectionStatus.className = 'connection-status disconnected';
                connectionText.textContent = `⚠️ センサー接続が切れています（${Math.floor(timeDiff/60)}分前）`;
            } else {
                connectionStatus.className = 'connection-status';
                connectionText.textContent = '✅ ローカルセンサーと正常に接続中';
            }
        }
        
        function updateCharacterFace(faceType) {
            const face = document.getElementById('character-face');
            const mouth = document.getElementById('face-mouth');
            
            // クラスをリセット
            face.className = 'character-face';
            mouth.className = 'face-mouth';
            
            switch(faceType) {
                case 'green':
                case 'happy':
                    face.classList.add('character-face-happy');
                    mouth.classList.add('mouth-happy');
                    break;
                case 'red':
                case 'sad':
                    face.classList.add('character-face-sad');
                    mouth.classList.add('mouth-sad');
                    break;
                default:
                    face.classList.add('character-face-normal');
                    mouth.classList.add('mouth-normal');
                    break;
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
        
        function getStatusIcon(status) {
            switch(status) {
                case 'green': return 'fas fa-check-circle status-icon';
                case 'yellow': return 'fas fa-exclamation-triangle status-icon';
                case 'red': return 'fas fa-times-circle status-icon';
                default: return 'fas fa-question-circle status-icon';
            }
        }
        
        // 15秒ごとに自動更新
        setInterval(refreshData, 15000);
        
        // ページ読み込み時に1回実行
        window.onload = function() {
            refreshData();
            updateConnectionStatus('{{ last_update }}');
        };
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><i class="fas fa-seedling"></i> AquaSync 水分監視システム</h1>
            <div class="subtitle">植物の水分レベルをリアルタイムで監視</div>
        </div>
        
        <div class="content">
            <div id="connection-status" class="connection-status">
                <span id="connection-text">✅ ローカルセンサーと正常に接続中</span>
            </div>
            
            <div class="status-overview">
                <div class="metric-card status-{{ status }}">
                    <div class="metric-icon">
                        <i class="fas fa-tint"></i>
                    </div>
                    <div class="metric-value" id="percentage">{{ percentage }}</div>
                    <div class="metric-label">水分レベル (%)</div>
                </div>
                
                <div class="metric-card status-{{ status }}">
                    <div class="metric-icon">
                        <i class="fas fa-chart-line"></i>
                    </div>
                    <div class="metric-value" id="raw-value">{{ raw_value }}</div>
                    <div class="metric-label">センサー値</div>
                </div>
                
                <div class="metric-card status-{{ status }}">
                    <div class="metric-icon">
                        <i class="fas fa-info-circle"></i>
                    </div>
                    <div class="metric-value" id="status-text">
                        {% if status == 'green' %}良好
                        {% elif status == 'yellow' %}適度
                        {% elif status == 'red' %}不足
                        {% else %}不明{% endif %}
                    </div>
                    <div class="metric-label">ステータス</div>
                </div>
                
                <div class="character-section">
                    <div class="character-title">植物の気持ち</div>
                    <div id="character-face" class="character-face character-face-{{ character_face }}">
                        <div class="face-bow">
                            <div class="face-bow-center"></div>
                        </div>
                        <div class="face-eyes">
                            <div class="eye"></div>
                            <div class="eye"></div>
                        </div>
                        <div class="face-cheeks">
                            <div class="cheek"></div>
                            <div class="cheek"></div>
                        </div>
                        <div id="face-mouth" class="face-mouth 
                            {% if character_face == 'happy' or status == 'green' %}mouth-happy
                            {% elif character_face == 'sad' or status == 'red' %}mouth-sad
                            {% else %}mouth-normal{% endif %}">
                        </div>
                    </div>
                    <div class="character-message" id="character-message">
                        {{ character_message }}
                    </div>
                </div>
            </div>
            
            <div id="main-status" class="main-status status-{{ status }}">
                <div id="status-icon" class="
                    {% if status == 'green' %}fas fa-check-circle
                    {% elif status == 'yellow' %}fas fa-exclamation-triangle
                    {% elif status == 'red' %}fas fa-times-circle
                    {% else %}fas fa-question-circle{% endif %} status-icon">
                </div>
                
                <div class="percentage" id="percentage-main">{{ percentage }}%</div>
                
                <div class="progress-container">
                    <div id="progress-fill" class="progress-fill status-{{ status }}" 
                         style="width: {{ percentage }}%"></div>
                </div>
                
                <div class="status-message">
                    {% if status == 'green' %}
                        水分レベルは十分です。植物は健康な状態を保っています。
                    {% elif status == 'yellow' %}
                        水分レベルは適度です。継続的な監視をお勧めします。
                    {% elif status == 'red' %}
                        水分が不足しています。早急に水やりが必要です。
                    {% else %}
                        ローカルセンサーからのデータを待機中です。
                    {% endif %}
                </div>
            </div>
            
            <div class="actions">
                <button class="btn" onclick="refreshData()">
                    <i class="fas fa-sync-alt"></i> データを更新
                </button>
                <button class="btn btn-secondary" onclick="window.location.reload()">
                    <i class="fas fa-redo"></i> ページを再読み込み
                </button>
            </div>
        </div>
        
        <div class="footer-info">
            <i class="fas fa-clock"></i> 最終更新: <span id="last-update">{{ last_update or 'データなし' }}</span>
            <br>
            <i class="fas fa-cloud"></i> Cloud Dashboard Version - Powered by Render
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

@app.route('/health')
def health_check():
    """ヘルスチェック用エンドポイント"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'last_sensor_update': current_data.get('last_update'),
        'current_status': current_data.get('status', 'unknown')
    })

@app.route('/image/<filename>')
def serve_image(filename):
    """ローカル画像ファイルを配信"""
    image_path = os.path.join(os.getcwd(), filename)
    if os.path.exists(image_path):
        return send_file(image_path)
    else:
        abort(404)

if __name__ == '__main__':
    print("🌐 AquaSync Cloud Dashboard 起動中...")
    print(f"🔐 API Secret Key: {'設定済み' if API_SECRET_KEY != 'your-secret-api-key' else '未設定'}")
    print("📊 ダッシュボード: /")
    print("🔌 API エンドポイント:")
    print("  - GET  /api/data - データ取得")
    print("  - POST /api/update - データ更新（要認証）")
    print("  - GET  /health - ヘルスチェック")
    
    # ポート設定（Render等のクラウド環境対応）
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    
    app.run(host=host, port=port, debug=False)