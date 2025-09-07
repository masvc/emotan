import requests
import os
import time
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# 設定
CLOUD_API_URL = os.getenv('CLOUD_API_URL', 'https://emotan.onrender.com')
API_SECRET_KEY = os.getenv('API_SECRET_KEY', 'aquasync-secret-key-2024')

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
            print("✅ クラウド送信成功")
            return True
        else:
            print(f"❌ クラウド送信失敗: {response.status_code}")
            print(f"   レスポンス: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ クラウド送信エラー: {e}")
        return False

def test_health_check():
    """ヘルスチェックエンドポイントをテスト"""
    try:
        response = requests.get(f"{CLOUD_API_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ ヘルスチェック成功")
            data = response.json()
            print(f"   ステータス: {data.get('status')}")
            print(f"   最終センサー更新: {data.get('last_sensor_update', 'なし')}")
            return True
        else:
            print(f"❌ ヘルスチェック失敗: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ ヘルスチェックエラー: {e}")
        return False

def get_current_data():
    """現在のダッシュボードデータを取得"""
    try:
        response = requests.get(f"{CLOUD_API_URL}/api/data", timeout=10)
        if response.status_code == 200:
            print("✅ データ取得成功")
            data = response.json()
            print(f"   水分レベル: {data.get('percentage', 0)}%")
            print(f"   ステータス: {data.get('status', 'unknown')}")
            print(f"   キャラクターメッセージ: {data.get('character_message', 'なし')}")
            print(f"   最終更新: {data.get('last_update', 'なし')}")
            return data
        else:
            print(f"❌ データ取得失敗: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ データ取得エラー: {e}")
        return None

def run_test_scenario():
    """様々な水分レベルでテストシナリオを実行"""
    test_scenarios = [
        {
            'name': '水不足状態',
            'data': {
                'raw_value': 25,
                'percentage': 25,
                'status': 'red',
                'last_update': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'message': '🔴 植物の水分不足テスト',
                'character_message': 'のど乾いちゃった〜',
                'character_face': 'sad'
            }
        },
        {
            'name': '適度な水分状態',
            'data': {
                'raw_value': 45,
                'percentage': 45,
                'status': 'yellow',
                'last_update': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'message': '🟡 植物の水分は適度テスト',
                'character_message': 'まあまあって感じかな',
                'character_face': 'normal'
            }
        },
        {
            'name': '十分な水分状態',
            'data': {
                'raw_value': 80,
                'percentage': 80,
                'status': 'green',
                'last_update': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'message': '🟢 植物の水分は十分テスト',
                'character_message': 'めっちゃ元気だよ〜！',
                'character_face': 'happy'
            }
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n--- テストシナリオ {i}: {scenario['name']} ---")
        
        # データ送信
        success = send_data_to_cloud(scenario['data'])
        
        if success:
            print(f"✅ {scenario['name']}のデータ送信完了")
            print(f"📊 ダッシュボード確認: {CLOUD_API_URL}")
            
            # 少し待機してからデータ確認
            time.sleep(2)
            print("\n現在のダッシュボードデータ:")
            get_current_data()
        else:
            print(f"❌ {scenario['name']}のデータ送信失敗")
        
        if i < len(test_scenarios):
            print("\n次のテストまで5秒待機...")
            time.sleep(5)

def main():
    print("🧪 AquaSync クラウド接続テスト 🧪")
    print(f"🌐 クラウドURL: {CLOUD_API_URL}")
    print(f"🔐 API Key: {'設定済み' if API_SECRET_KEY != 'aquasync-secret-key-2024' else 'デフォルト'}")
    print("=" * 50)
    
    # 1. ヘルスチェック
    print("\n1. ヘルスチェックテスト")
    if not test_health_check():
        print("❌ ヘルスチェックに失敗しました。サーバーが起動していない可能性があります。")
        return
    
    # 2. 現在のデータ取得
    print("\n2. 現在のデータ取得テスト")
    if not get_current_data():
        print("❌ データ取得に失敗しました。")
        return
    
    # 3. テストデータ送信
    print("\n3. テストデータ送信")
    user_input = input("テストシナリオを実行しますか？ (y/n): ")
    
    if user_input.lower() in ['y', 'yes', 'はい']:
        run_test_scenario()
        
        print("\n🎉 テスト完了！")
        print(f"📊 ダッシュボードを確認してください: {CLOUD_API_URL}")
        print("💡 友人にURLを共有できます！")
    else:
        print("テストをスキップしました。")
    
    print("\n--- テスト結果まとめ ---")
    print("✅ 成功したテスト:")
    print("   - ヘルスチェック")
    print("   - データ取得")
    if user_input.lower() in ['y', 'yes', 'はい']:
        print("   - テストデータ送信")
    
    print("\n🔗 次のステップ:")
    print("1. Arduinoを接続してlocal_sensor.pyを実行")
    print("2. 友人にダッシュボードURLを共有")
    print(f"3. URL: {CLOUD_API_URL}")

if __name__ == "__main__":
    main()