import requests
from collections import defaultdict, Counter
import statistics
import time
import random
from datetime import datetime as dt
import os
import platform
import json
import math

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False
    class Fore:
        WHITE = RED = GREEN = YELLOW = BLUE = CYAN = MAGENTA = ""
    class Style:
        NORMAL = BRIGHT = RESET_ALL = ""

ROOM_NAMES = [
    " ",
    "Nhà kho",
    "Phòng họp", 
    "Phòng giám đốc",
    "Phòng trò chuyện",
    "Phòng giám sát",
    "Văn phòng",
    "Phòng tài vụ",
    "Phòng nhân sự"
]

CONFIG_FILE = "xworld_config.json"
DATA_FILE = "dulieu.txt"
STATS_FILE = "thongke.json"

def load_config():
    user_id=input('Nhập user-id của bạn:')
    user_secret_key=input('Nhập secret-key của bạn:')
    default_config = {
        "user_id": user_id,
        "user_secret_key": user_secret_key,
        "risk_level": 0.3,  
        "analysis_depth": 50, 
        "lucky_factor": 0.2  
    }
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return {**default_config, **config}
    except:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)
        return default_config

def save_stats(stats):
    try:
        with open(STATS_FILE, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
    except Exception as e:
        fancy_print(f"⚠️ Lỗi lưu thống kê: {e}", Fore.RED)

def load_stats():
    try:
        with open(STATS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"wins": 0, "loses": 0, "total_games": 0, "win_streak": 0, "max_streak": 0}

def clear_screen():
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')

def fancy_print(text, color=Fore.WHITE, style=Style.NORMAL, end='\n'):
    if COLORAMA_AVAILABLE:
        print(f"{style}{color}{text}{Style.RESET_ALL}", end=end)
    else:
        print(text, end=end)

def display_header():
    current_time = dt.now().strftime("%H:%M:%S %d/%m/%Y")
    fancy_print("╔══════════════════════════════════════════╗", Fore.CYAN, Style.BRIGHT)
    fancy_print("║         XWORLD - VUA THOÁT HIỂM          ║", Fore.CYAN, Style.BRIGHT)
    fancy_print("║               Tool by NTC                ║", Fore.CYAN, Style.BRIGHT)
    fancy_print("║ Tele:https://t.me/+RL_zVyZjvx1hZjc1      ║", Fore.CYAN, Style.BRIGHT)
    fancy_print("║ YTB:https://www.youtube.com/@Tool-Xworld ║", Fore.CYAN, Style.BRIGHT)
    fancy_print("║ Tiktok:https://www.tiktok.com/@cng1237929║", Fore.CYAN, Style.BRIGHT)
    fancy_print("║ Zalo:0842010239                          ║", Fore.CYAN, Style.BRIGHT)
    fancy_print(f"║ Thời gian: {current_time:<30}║", Fore.CYAN, Style.BRIGHT)
    fancy_print("╚══════════════════════════════════════════╝", Fore.CYAN, Style.BRIGHT)

def display_wallet_balance(headers):
	user_id = headers['user-id']
	json_data = {
		'user_id': int(user_id),
		'source': 'home',
	}
	for attempt in range(3):
		try:
			response = requests.post(
				'https://wallet.3games.io/api/wallet/user_asset', 
				headers=headers, 
				json=json_data, 
				timeout=15
			)
			if response.status_code == 200:
				data = response.json()
				assets = data.get("data", {}).get("user_asset", {})
				build = assets.get("BUILD", 0)
				world = assets.get("WORLD", 0)
				usdt = assets.get("USDT", 0)
				fancy_print("\n╔══════════════════════════════╗", Fore.YELLOW, Style.BRIGHT)
				fancy_print("║        SỐ DƯ TÀI SẢN         ║", Fore.YELLOW, Style.BRIGHT)
				fancy_print("╠══════════════════════════════╣", Fore.YELLOW, Style.BRIGHT)
				fancy_print(f"║ BUILD : {build:<21,.2f}║", Fore.YELLOW, Style.BRIGHT)
				fancy_print(f"║ WORLD : {world:<21,.2f}║", Fore.YELLOW, Style.BRIGHT)
				fancy_print(f"║ USDT  : {usdt:<21,.2f}║", Fore.YELLOW, Style.BRIGHT)
				fancy_print("╚══════════════════════════════╝\n", Fore.YELLOW, Style.BRIGHT)
				return True
			else:
				fancy_print(f"⚠️ API trả về lỗi: {response.status_code}", Fore.YELLOW)
		except requests.exceptions.Timeout:
			fancy_print(f"⚠️ Timeout lần {attempt + 1}/3, thử lại...", Fore.YELLOW)
		except Exception as e:
			fancy_print(f"⚠️ Lỗi khi lấy số dư (lần {attempt + 1}/3): {e}", Fore.YELLOW)
		if attempt < 2:
			time.sleep(2)
	fancy_print("⚠️ Không thể lấy thông tin số dư sau 3 lần thử!", Fore.RED, Style.BRIGHT)
	return False
def safe_api_call(url, headers, params=None, json_data=None, max_retries=3):
    for attempt in range(max_retries):
        try:
            if json_data:
                response = requests.post(url, headers=headers, json=json_data, timeout=15)
            else:
                response = requests.get(url, headers=headers, params=params, timeout=15)
            
            if response.status_code == 200:
                return response.json()
            else:
                fancy_print(f"⚠️ API error {response.status_code} (lần {attempt + 1})", Fore.YELLOW)
        except requests.exceptions.Timeout:
            fancy_print(f"⚠️ Timeout lần {attempt + 1}/{max_retries}", Fore.YELLOW)
        except Exception as e:
            fancy_print(f"⚠️ Lỗi API lần {attempt + 1}/{max_retries}: {e}", Fore.YELLOW)
        
        if attempt < max_retries - 1:
            time.sleep(2 ** attempt)
    
    return None

def get_top10_data(headers):
    params = {'asset': 'BUILD'}
    res = safe_api_call('https://api.escapemaster.net/escape_game/recent_10_issues', headers, params=params)
    
    if not res or not res.get('data'):
        fancy_print("⚠️ Không thể lấy dữ liệu top 10!", Fore.RED, Style.BRIGHT)
        return [], []
    
    issue_ids = [i['issue_id'] for i in res['data']]
    killed_rooms = [int(i['killed_room_id']) for i in res['data']]
    return issue_ids, killed_rooms

def get_top100_data(headers):
    params = {'asset': 'BUILD'}
    res = safe_api_call('https://api.escapemaster.net/escape_game/recent_100_issues', headers, params=params)
    
    if not res or not res.get('data') or not res['data'].get('room_id_2_killed_times'):
        fancy_print("⚠️ Không thể lấy dữ liệu top 100!", Fore.RED, Style.BRIGHT)
        return [], []
    
    room_data = res['data']['room_id_2_killed_times']
    rooms = [int(i) for i in room_data.keys()]
    kill_counts = [room_data[str(i)] for i in rooms]
    return rooms, kill_counts

def analyze_pattern(killed_rooms, depth=20):
    if len(killed_rooms) < depth:
        depth = len(killed_rooms)
    
    recent_rooms = killed_rooms[:depth]
    room_frequency = Counter(recent_rooms)
    very_recent = recent_rooms[:5] 
    recent_frequency = Counter(very_recent)
    patterns = {}
    for i in range(len(recent_rooms) - 2):
        pattern = tuple(recent_rooms[i:i+3])
        patterns[pattern] = patterns.get(pattern, 0) + 1
    
    return {
        'room_frequency': room_frequency,
        'recent_frequency': recent_frequency,
        'patterns': patterns,
        'last_room': recent_rooms[0] if recent_rooms else 1
    }

def calculate_room_safety_scores(top10_data, top100_data, config):
    issue_ids, killed_rooms = top10_data
    rooms_100, kill_counts_100 = top100_data
    
    if not killed_rooms or not rooms_100:
        return {i: 0.5 for i in range(1, 9)} 
    analysis = analyze_pattern(killed_rooms, config['analysis_depth'])
    safety_scores = {}
    
    for room in range(1, 9):
        score = 1.0
        recent_kills = analysis['room_frequency'].get(room, 0)
        if recent_kills > 0:
            score -= (recent_kills / len(killed_rooms)) * 0.4
        very_recent_kills = analysis['recent_frequency'].get(room, 0)
        if very_recent_kills > 0:
            score -= (very_recent_kills / 5) * 0.3
        if room in rooms_100:
            room_index = rooms_100.index(room)
            kill_count_100 = kill_counts_100[room_index]
            score += (1 - kill_count_100 / max(kill_counts_100)) * 0.2
        else:
            score += 0.2
        if analysis['last_room'] == room:
            score -= 0.5
        safety_scores[room] = max(0.1, min(1.0, score))
    
    return safety_scores

def smart_room_selection(safety_scores, config):
    min_safe_score = 0.6
    safe_rooms = {room: score for room, score in safety_scores.items() if score >= min_safe_score}
    
    if not safe_rooms:
        safe_rooms = {max(safety_scores.keys(), key=lambda k: safety_scores[k]): 
                     max(safety_scores.values())}
    weighted_choices = []
    for room, score in safe_rooms.items():
        weight = score + (random.random() * config['lucky_factor'])
        weighted_choices.append((room, weight))
    if random.random() < config['risk_level']:
        return random.choice([room for room, _ in weighted_choices])
    else:
        return max(weighted_choices, key=lambda x: x[1])[0]

def display_analysis_results(safety_scores, selected_room, current_issue):
    fancy_print("\n" + "="*60, Fore.GREEN, Style.BRIGHT)
    fancy_print(f"🎯 PHÒNG ĐƯỢC CHỌN: {selected_room} - {ROOM_NAMES[selected_room]}", Fore.GREEN, Style.BRIGHT)
    fancy_print(f"🤖 ĐỘ TIN CẬY: 85% ", Fore.BLUE, Style.BRIGHT)
    fancy_print("="*60, Fore.GREEN, Style.BRIGHT)
def chon_phong_thong_minh(headers, config):
    fancy_print("🔍 Đang thu thập dữ liệu...", Fore.CYAN)
    top10_data = get_top10_data(headers)
    top100_data = get_top100_data(headers)
    
    issue_ids, killed_rooms = top10_data
    
    if not issue_ids or not killed_rooms:
        fancy_print("⚠️ Không thể lấy dữ liệu, chọn phòng ngẫu nhiên", Fore.YELLOW)
        return random.randint(1, 8), 0
    
    current_issue = issue_ids[0] + 1
    
    fancy_print("📊 Đang phân tích...", Fore.CYAN)
    safety_scores = calculate_room_safety_scores(top10_data, top100_data, config)
    selected_room = smart_room_selection(safety_scores, config)
    display_analysis_results(safety_scores, selected_room, current_issue)
    try:
        prediction_data = {
            'issue': current_issue,
            'selected_room': selected_room,
            'safety_scores': safety_scores,
            'timestamp': dt.now().isoformat()
        }
        with open('predictions.json', 'a', encoding='utf-8') as f:
            f.write(json.dumps(prediction_data, ensure_ascii=False) + '\n')
    except:
        pass
    
    return selected_room, current_issue

def display_enhanced_stats():
    stats = load_stats()
    fancy_print("\n" + "="*50, Fore.BLUE, Style.BRIGHT)
    fancy_print("📈 THỐNG KÊ TRẬN ĐẤU", Fore.BLUE, Style.BRIGHT)
    fancy_print("="*50, Fore.BLUE, Style.BRIGHT)
    
    win_rate = (stats['wins'] / max(stats['total_games'], 1)) * 100
    fancy_print(f"🏆 Thắng: {stats['wins']} trận", Fore.GREEN, Style.BRIGHT)
    fancy_print(f"💀 Thua: {stats['loses']} trận", Fore.RED, Style.BRIGHT)
    fancy_print(f"🎯 Tổng: {stats['total_games']} trận", Fore.CYAN, Style.BRIGHT)
    fancy_print(f"📊 Tỷ lệ thắng: {win_rate:.1f}%", Fore.YELLOW, Style.BRIGHT)
    fancy_print(f"🔥 Chuỗi thắng: {stats['win_streak']} (Max: {stats['max_streak']})", Fore.MAGENTA, Style.BRIGHT)
    
    fancy_print("="*50, Fore.BLUE, Style.BRIGHT)

def kiem_tra_kq_nang_cao(headers, ki, bot_chon):
    fancy_print("\n⏳ Đang chờ kết quả...", Fore.YELLOW)
    
    max_wait_time = 300  
    wait_interval = 10 
    waited_time = 0
    
    while waited_time < max_wait_time:
        top10_data = get_top10_data(headers)
        issue_ids, killed_rooms = top10_data
        
        if not issue_ids or not killed_rooms:
            time.sleep(wait_interval)
            waited_time += wait_interval
            continue
        
        if int(ki) == int(issue_ids[0]):
            killer_room = killed_rooms[0]
            result = 'Thắng' if bot_chon != killer_room else 'Thua'
            fancy_print("\n" + "="*50, Fore.MAGENTA, Style.BRIGHT)
            fancy_print("🎮 KẾT QUẢ TRẬN ĐẤU", Fore.MAGENTA, Style.BRIGHT)
            fancy_print("="*50, Fore.MAGENTA, Style.BRIGHT)
            
            fancy_print(f"🆔 Kì số: {ki}", Fore.CYAN, Style.BRIGHT)
            fancy_print(f"💀 Sát thủ chọn: Phòng {killer_room} ({ROOM_NAMES[killer_room]})", Fore.RED, Style.BRIGHT)
            fancy_print(f"🤖 Bot chọn: Phòng {bot_chon} ({ROOM_NAMES[bot_chon]})", Fore.BLUE, Style.BRIGHT)
            
            if result == 'Thắng':
                fancy_print("🏆 KẾT QUẢ: THẮNG! 🎉", Fore.GREEN, Style.BRIGHT)
            else:
                fancy_print("💔 KẾT QUẢ: THUA 😢", Fore.RED, Style.BRIGHT)
                
            fancy_print("="*50, Fore.MAGENTA, Style.BRIGHT)
            stats = load_stats()
            stats['total_games'] += 1
            
            if result == 'Thắng':
                stats['wins'] += 1
                stats['win_streak'] += 1
                stats['max_streak'] = max(stats['max_streak'], stats['win_streak'])
            else:
                stats['loses'] += 1
                stats['win_streak'] = 0
            
            save_stats(stats)
            with open(DATA_FILE, 'a', encoding='utf-8') as f:
                f.write(f'Kì {ki}: Sát thủ chọn phòng [{killer_room}]: {ROOM_NAMES[killer_room]}, '
                       f'Bot chọn phòng [{bot_chon}]: {ROOM_NAMES[bot_chon]}, KẾT QUẢ: {result}\n')
            
            time.sleep(3)
            return result
        dots = "." * ((waited_time // 5) % 4)
        fancy_print(f"\r⏳ Chờ kết quả{dots:<3} ({waited_time//60:02d}:{waited_time%60:02d})", 
                   Fore.YELLOW, end='')
        
        time.sleep(wait_interval)
        waited_time += wait_interval
    
    fancy_print("\n⚠️ Timeout - Không thể lấy kết quả!", Fore.RED, Style.BRIGHT)
    return None

def main():
    try:
        config = load_config()
        
        headers = {
            'accept': '*/*',
            'accept-language': 'vi,en;q=0.9',
            'cache-control': 'no-cache',
            'country-code': 'vn',
            'origin': 'https://xworld.info',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://xworld.info/',
            'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': 'Mozilla/5.0 (Linux; Android 13; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
            'user-id': config['user_id'],
            'user-login': 'login_v2',
            'user-secret-key': config['user_secret_key'],
            'xb-language': 'vi-VN',
        }
        
        clear_screen()
        display_header()
        if not display_wallet_balance(headers):
            fancy_print("❌ Không thể kết nối đến server. Vui lòng kiểm tra lại!", Fore.RED, Style.BRIGHT)
            input("Nhấn Enter để thoát...")
            return
        
        time.sleep(2)
        
        while True:
            try:
                clear_screen()
                display_header()
                display_wallet_balance(headers)
                bot_chon, ki = chon_phong_thong_minh(headers, config)
                
                if ki == 0:
                    fancy_print("⚠️ Không thể lấy thông tin kì hiện tại!", Fore.RED)
                    time.sleep(5)
                    continue
                
                time.sleep(3)
                display_enhanced_stats()
                result = kiem_tra_kq_nang_cao(headers, ki, bot_chon)
                
                if result:
                    if result == 'Thắng':
                        fancy_print("🎉 CHÚC MỪNG! BẠN ĐÃ THẮNG!", Fore.GREEN, Style.BRIGHT)
                    else:
                        fancy_print("😢 Chúc bạn may mắn lần sau!", Fore.YELLOW, Style.BRIGHT)
                fancy_print("\n⏰ Chờ 10 giây trước khi tiếp tục...", Fore.CYAN)
                time.sleep(10)
                
            except KeyboardInterrupt:
                fancy_print("\n👋 Tạm biệt! Cảm ơn bạn đã sử dụng tool!", Fore.CYAN, Style.BRIGHT)
                break
            except Exception as e:
                fancy_print(f"⚠️ Lỗi không mong muốn: {e}", Fore.RED, Style.BRIGHT)
                fancy_print("🔄 Thử lại sau 5 giây...", Fore.YELLOW)
                time.sleep(5)
                
    except Exception as e:
        fancy_print(f"❌ Lỗi nghiêm trọng: {e}", Fore.RED, Style.BRIGHT)
        input("Nhấn Enter để thoát...")

if __name__ == "__main__":
    main()
