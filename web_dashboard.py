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

# HTML テンプレート（ビジュアルノベル風・音声機能付き）
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
            width: 200px;
            background: rgba(255, 255, 255, 0.95);
            border: 3px solid #8B4513;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
            backdrop-filter: blur(8px);
            z-index: 20;
            text-align: center;
        }
        .sidebar-title {
            font-size: 18px;
            font-weight: bold;
            color: #8B4513;
            margin-bottom: 15px;
            border-bottom: 2px solid #8B4513;
            padding-bottom: 8px;
        }
        .water-level {
            font-size: 32px;
            font-weight: bold;
            color: #8B4513;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
        }
        .water-level.happy {
            color: #007bff;
        }
        .water-level.angry {
            color: #dc3545;
        }
        .emotion-mark {
            font-size: 28px;
            animation: pulse 2s infinite;
            color: #8B4513;
        }
        .emotion-mark.happy {
            color: #007bff;
        }
        .emotion-mark.angry {
            color: #dc3545;
        }
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
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
            margin: 10px;
            border-radius: 12px;
            background: rgba(255, 255, 255, 0.1);
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
        
    </style>
    <script>
        let lastUpdateTime = new Date('{{ last_update or "1970-01-01" }}').getTime();
        let lastFaceType = null; // 前回の状態を記録（音声用）
        
        function refreshData() {
            fetch('/api/data')
                .then(response => response.json())
                .then(data => {
                    // 水分量の更新
                    document.getElementById('percentage').textContent = data.percentage + '%';
                    
                    // 感情マークの更新
                    updateEmotionMark(data.character_face);
                    
                    // 色の更新
                    updateColors(data.percentage, data.character_face);
                    
                    // 台詞ボックスの更新
                    document.getElementById('dialogue-text').textContent = data.character_message || 'お疲れ様！';
                    
                    // キャラクター画像のエフェクト更新（音声付き）
                    updateCharacterEffect(data.character_face || data.status);
                    
                    // ステータスに応じてクラスを更新
                    const sidebar = document.getElementById('sidebar');
                    sidebar.className = 'sidebar status-' + data.status;
                });
        }
        
        function playVoice(faceType) {
            // 状態に応じた音声ファイルを決定
            let voiceFile = getVoiceFile(faceType);
            
            if (voiceFile) {
                const audio = new Audio(`/voice/${voiceFile}`);
                audio.volume = 0.7; // 音量調整
                audio.play().catch(e => console.log('音声再生エラー:', e));
                console.log(`🎵 音声再生: ${voiceFile}`);
            }
        }
        
        function getVoiceFile(faceType) {
            const voiceFiles = {
                'yousei1': ['ohayo.wav', 'yorosiku.wav'],
                'yousei2': ['nice.wav'],
                'yousei4': ['arigatou.wav', 'yatta.wav'],
                'yousei5': ['kora.wav', 'omizu.wav']
            };
            
            const files = voiceFiles[faceType];
            if (files && files.length > 0) {
                // ランダムに選択
                return files[Math.floor(Math.random() * files.length)];
            }
            return null;
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
                    faceType = 'yousei4'; // 音声用に正規化
                    break;
                case 'red':
                case 'sad':
                    imageSrc = '/img/yousei5.png';
                    characterImg.classList.add('sad');
                    faceType = 'yousei5'; // 音声用に正規化
                    break;
                default:
                    imageSrc = '/img/yousei1.png';
                    faceType = 'yousei1'; // 音声用に正規化
                    break;
            }
            
            // 画像を更新
            characterImg.src = imageSrc;
            
            // 状態が変わった時だけ音声再生
            if (lastFaceType !== faceType) {
                console.log(`🔄 状態変化: ${lastFaceType} → ${faceType}`);
                playVoice(faceType);
                lastFaceType = faceType;
            }
        }
        
        function updateEmotionMark(faceType) {
            const emotionMark = document.getElementById('emotion-mark');
            
            switch(faceType) {
                case 'yousei1':
                    emotionMark.innerHTML = '<i class="fas fa-smile"></i>';
                    break;
                case 'yousei2':
                    emotionMark.innerHTML = '<i class="fas fa-meh"></i>';
                    break;
                case 'yousei4':
                    emotionMark.innerHTML = '<i class="fas fa-laugh"></i>';
                    break;
                case 'yousei5':
                    emotionMark.innerHTML = '<i class="fas fa-angry"></i>';
                    break;
                default:
                    emotionMark.innerHTML = '<i class="fas fa-smile"></i>';
                    break;
            }
        }
        
        function updateColors(percentage, faceType) {
            const waterLevel = document.getElementById('water-level');
            const emotionMark = document.getElementById('emotion-mark');
            
            // クラスをリセット
            waterLevel.classList.remove('happy', 'angry');
            emotionMark.classList.remove('happy', 'angry');
            
            // 90-100%または喜びの時は青
            if ((percentage >= 90 && percentage <= 100) || faceType === 'yousei4') {
                waterLevel.classList.add('happy');
                emotionMark.classList.add('happy');
            }
            // 開始時以外の0%または怒りの時は赤
            else if ((percentage === 0 && faceType === 'yousei5') || faceType === 'yousei5') {
                waterLevel.classList.add('angry');
                emotionMark.classList.add('angry');
            }
        }
        
        // 10秒ごとに自動更新
        setInterval(refreshData, 10000);
        
        // ページ読み込み時に1回実行
        window.onload = function() {
            refreshData();
        };
    </script>
</head>
<body>
    <!-- サイドバー（右上） -->
    <div id="sidebar" class="sidebar status-{{ status }}">
        <div class="sidebar-title">好感度</div>
        
        <div id="water-level" class="water-level">
            <span id="percentage">{{ percentage }}%</span>
            <div id="emotion-mark" class="emotion-mark">
                {% if character_face == 'yousei1' %}<i class="fas fa-smile"></i>
                {% elif character_face == 'yousei2' %}<i class="fas fa-meh"></i>
                {% elif character_face == 'yousei4' %}<i class="fas fa-laugh"></i>
                {% elif character_face == 'yousei5' %}<i class="fas fa-angry"></i>
                {% else %}<i class="fas fa-smile"></i>{% endif %}
            </div>
        </div>
    </div>
    
    <!-- キャラクター表示エリア -->
    <div class="character-area">
        <img id="character-image" src="/img/yousei1.png" alt="エモたん" class="character-image {{ character_face }}">
    </div>
    
    <!-- 台詞ボックス -->
    <div class="dialogue-container">
        <div class="dialogue-box">
            <div class="dialogue-name">エモたんからのメッセージ</div>
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

@app.route('/voice/<filename>')
def serve_voice(filename):
    """音声ファイルを配信"""
    voice_path = os.path.join(os.getcwd(), 'voice', filename)
    if os.path.exists(voice_path):
        return send_file(voice_path, mimetype='audio/wav')
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
    print("  - GET  /voice/<filename> - 音声ファイル配信")
    print("  - GET  /health - ヘルスチェック")
    
    # ポート設定（Render等のクラウド環境対応）
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    
    app.run(host=host, port=port, debug=False)