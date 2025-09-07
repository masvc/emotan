import requests
import serial
import os
import time
import threading
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# 設定
CHANNEL_ACCESS_TOKEN = os.getenv('CHANNEL_ACCESS_TOKEN')
ARDUINO_PORT = os.getenv('ARDUINO_PORT')
CLOUD_API_URL = os.getenv('CLOUD_API_URL', 'https://your-render-app.onrender.com')
API_SECRET_KEY = os.getenv('API_SECRET_KEY', 'your-secret-api-key')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# ローカルデータ保存
current_data = {
    'raw_value': 0,
    'percentage': 0,
    'status': 'unknown',
    'last_update': None,
    'message': '起動中...',
    'character_message': 'システム起動中だよ〜！',
    'character_face': 'normal'
}

def generate_character_message(percentage, status):
    """Gemini APIを使って植物キャラクターのセリフを生成"""
    if not GEMINI_API_KEY:
        return get_default_message(status, percentage)
    
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # 明るくて親しみやすい植物キャラクター用プロンプト
        prompt = f"""
あなたは明るくて親しみやすい植物キャラクターです。
現在の水分レベル: {percentage}%
状態: {status}

以下の条件でセリフを作ってください：
- 30-60文字程度の短いセリフ
- 明るくて親しみやすい話し方
- 「〜だよ」「〜ね」「〜よ」などの自然な語尾
- 感謝の気持ちを素直に表現
- 現在の水分状況を簡潔に含める
- 絵文字は使わない

例：
良好(80%): 「{percentage}%で元気だよ！いつもありがとう♪」
水不足(0%): 「のどが乾いたよ〜。お水ちょうだい！」

セリフのみを返してください:
"""
        
        response = model.generate_content(prompt)
        message = response.text.strip()
        
        # 長いメッセージの場合は適切にトリミング
        if len(message) > 80:
            message = message[:77] + "..."
            
        return message
        
    except Exception as e:
        print(f"Gemini API エラー: {e}")
        return get_default_message(status, percentage)

def get_default_message(status, percentage):
    """デフォルトメッセージ（API失敗時用）"""
    import random
    
    # 水分レベルに応じたパターン分け
    if percentage == 0:
        # ❶デフォルト：開始時 0%
        messages = [
            'よろしく！今日も一緒に頑張ろうね',
            'おはよう！今日もよろしくお願いします',
            'システム起動中だよ！準備OK'
        ]
    elif 1 <= percentage <= 90:
        # ❷ちょっとだけ喜ぶ：1%~90%
        messages = [
            f'{percentage}%だよ！まあまあかな。いつもありがとう',
            f'水分{percentage}%でそこそこ元気だよ！あなたのおかげだね',
            f'{percentage}%でぼちぼちだよ！見守ってくれてありがとう'
        ]
    elif 90 < percentage <= 100:
        # ❸喜ぶ：90~100%
        messages = [
            f'元気だよ！{percentage}%で調子いいね。いつもありがとう',
            f'{percentage}%で絶好調！あなたのおかげで幸せだよ',
            f'水分{percentage}%で最高だよ！ありがとう'
        ]
    else:
        # ❹怒る：開始時以外の0%
        messages = [
            'のどが乾いたよ！お水欲しいな',
            'カラカラだよ！助けて',
            'お水が足りないよ！早く'
        ]
    
    return random.choice(messages)

def send_line_message(message):
    """LINE Messaging API経由でメッセージ送信"""
    url = "https://api.line.me/v2/bot/message/broadcast"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"
    }
    
    data = {
        "messages": [
            {
                "type": "text",
                "text": message
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            print(f"LINE送信成功: {message}")
            return True
        else:
            print(f"LINE送信失敗: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"LINE送信エラー: {e}")
        return False

def get_water_status_message(raw_value, percentage):
    """水分レベルに応じたLINEメッセージを生成"""
    current_time = time.strftime("%H:%M")
    
    if percentage <= 30:
        return f"🔴 植物の水分不足 ({current_time})\n💧 水分レベル: {percentage}%\n⚠️ 水やりが必要です！"
    elif percentage <= 60:
        return f"🟡 植物の水分は適度 ({current_time})\n💧 水分レベル: {percentage}%\n✅ 良好な状態です"
    else:
        return f"🟢 植物の水分は十分 ({current_time})\n💧 水分レベル: {percentage}%\n🎉 完璧な状態です！"

def update_current_data(raw_value, percentage):
    """現在のデータを更新"""
    global current_data
    
    # 水分レベルに応じたパターン分け
    if percentage == 0:
        status = "unknown"
        face = "yousei1"  # ❶デフォルト：開始時 0%
    elif 1 <= percentage <= 90:
        status = "yellow"
        face = "yousei2"  # ❷ちょっとだけ喜ぶ：1%~90%
    elif 90 < percentage <= 100:
        status = "green"
        face = "yousei4"  # ❸喜ぶ：90~100%
    else:
        status = "red"
        face = "yousei5"  # ❹怒る：開始時以外の0%
    
    character_message = generate_character_message(percentage, status)
    
    current_data.update({
        'raw_value': raw_value,
        'percentage': percentage,
        'status': status,
        'last_update': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'message': get_water_status_message(raw_value, percentage),
        'character_message': character_message,
        'character_face': face
    })
    
    print(f"📊 データ更新: {percentage}% ({status}) | キャラクター: {character_message} | 画像: {face}")

def send_data_to_cloud(data):
    """クラウドAPIにデータを送信"""
    try:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {API_SECRET_KEY}'
        }
        
        response = requests.post(
            f"{CLOUD_API_URL}/api/update",
            json=data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print("☁️ クラウド送信成功")
            return True
        else:
            print(f"☁️ クラウド送信失敗: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"☁️ クラウド送信エラー: {e}")
        return False

def test_line_connection():
    """LINE接続テスト"""
    print("LINE Messaging API接続テスト中...")
    success = send_line_message("🌱 AquaSync水分監視システムが開始されました\n定期的に植物の状態をお知らせします")
    if success:
        print("✅ LINE接続成功")
    else:
        print("❌ LINE接続失敗")
    return success

def parse_arduino_data(line):
    """Arduinoからのデータを解析"""
    try:
        if "Raw:" in line and "%" in line:
            parts = line.split("->")
            if len(parts) >= 2:
                raw_part = parts[0].split("Raw:")[-1].strip()
                percent_part = parts[1].split("%")[0].strip()
                
                raw_value = int(raw_part)
                percentage = int(percent_part)
                
                return raw_value, percentage
    except Exception as e:
        print(f"データ解析エラー: {e}")
    
    return None, None

def send_status_report(raw_value, percentage, status_type):
    """状態に応じたLINE通知を送信"""
    message = get_water_status_message(raw_value, percentage)
    
    # データ更新
    update_current_data(raw_value, percentage)
    
    # クラウドに送信
    send_data_to_cloud(current_data)
    
    if status_type == "green":
        success = send_line_message(message)
    else:
        success = send_line_message(message)
    
    return success

def main():
    print(f"🌱 AquaSync ローカルセンサーシステム 🌱")
    print(f"Arduino監視開始: {ARDUINO_PORT}")
    print(f"Channel Access Token設定: {'OK' if CHANNEL_ACCESS_TOKEN else 'NG'}")
    print(f"Gemini API Key設定: {'OK' if GEMINI_API_KEY else 'NG'}")
    print(f"クラウドAPI URL: {CLOUD_API_URL}")
    
    if not CHANNEL_ACCESS_TOKEN:
        print("❌ CHANNEL_ACCESS_TOKENが設定されていません")
        return

    # 初期キャラクターメッセージ設定
    initial_message = generate_character_message(0, 'unknown')
    current_data['character_message'] = initial_message
    print(f"🎭 キャラクター初期化: {initial_message}")
    
    # LINE接続テスト
    if not test_line_connection():
        print("LINE接続に問題があります。続行しますが通知は送信されません。")
    
    # クラウド接続テスト
    print("☁️ クラウド接続テスト中...")
    if send_data_to_cloud(current_data):
        print("✅ クラウド接続成功")
    else:
        print("❌ クラウド接続失敗")
    
    print("✅ システム準備完了")
    print("📊 水分レベル変化と定期レポートでLINE通知を送信します")
    print("☁️ データをクラウドに送信してWebダッシュボードに反映します")
    
    # 状態追跡変数
    last_status = None
    last_report_time = time.time()
    last_cloud_update = time.time()
    report_interval = 600  # 10分間隔での定期レポート
    cloud_update_interval = 10  # 10秒間隔でクラウド更新
    
    try:
        arduino = serial.Serial(ARDUINO_PORT, 9600)
        time.sleep(2)
        print("Arduino接続成功！水分監視を開始します。")
        
        while True:
            try:
                line = arduino.readline().decode().strip()
                if line:
                    print(f"受信: {line}")
                    
                    # 水分データの解析
                    raw_value, percentage = parse_arduino_data(line)
                    if raw_value is not None and percentage is not None:
                        current_time = time.time()
                        
                        # 状態変化の検出
                        current_status = None
                        if percentage <= 30:
                            current_status = "red"
                        elif percentage <= 60:
                            current_status = "yellow"
                        else:
                            current_status = "green"
                        
                        # データを常時更新
                        update_current_data(raw_value, percentage)
                        
                        # 状態が変わった場合に通知
                        if current_status != last_status and last_status is not None:
                            print(f"🔔 状態変化検出: {last_status} → {current_status}")
                            success = send_status_report(raw_value, percentage, current_status)
                            if success:
                                print("✅ 状態変化通知送信完了")
                            else:
                                print("❌ 状態変化通知送信失敗")
                        
                        last_status = current_status
                        
                        # 定期的にクラウドに送信（15秒間隔）
                        if current_time - last_cloud_update >= cloud_update_interval:
                            send_data_to_cloud(current_data)
                            last_cloud_update = current_time
                        
                        # 定期レポート（5分間隔）
                        if current_time - last_report_time >= report_interval:
                            print("📊 定期レポート送信中...")
                            message = f"📊 定期レポート\n{get_water_status_message(raw_value, percentage)}\n\n次回レポート: 5分後"
                            success = send_line_message(message)
                            if success:
                                print("✅ 定期レポート送信完了")
                                last_report_time = current_time
                            else:
                                print("❌ 定期レポート送信失敗")
                    
            except KeyboardInterrupt:
                print("\n監視を終了します")
                break
            except UnicodeDecodeError as e:
                print(f"文字エンコードエラー: {e}")
                time.sleep(0.1)
            except Exception as e:
                print(f"読み取りエラー: {e}")
                time.sleep(1)
                
    except Exception as e:
        print(f"Arduino接続エラー: {e}")
        print("ポート名やArduino IDEのシリアルモニタが開いていないか確認してください。")

if __name__ == "__main__":
    main()