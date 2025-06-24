import requests
from collections import defaultdict
import statistics
from colorama import Fore, Style, init
import time
import random
from datetime import datetime as dt
import os
import platform

init(autoreset=True)
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


def clear_screen():
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')

def fancy_print(text, color=Fore.WHITE, style=Style.NORMAL,e='\n'):
    print(f"{style}{color}{text}{Style.RESET_ALL}",end=e)

def display_header():
    current_time = dt.now().strftime("%H:%M:%S %d/%m/%Y")
    fancy_print("╔══════════════════════════════════════╗", Fore.CYAN, Style.BRIGHT)
    fancy_print("║       XWORLD - VUA THOÁT HIỂM        ║", Fore.CYAN, Style.BRIGHT)
    fancy_print("║             Tool by NTC              ║", Fore.CYAN, Style.BRIGHT)
    fancy_print(f"║  Thời gian: {current_time}      ║", Fore.CYAN, Style.BRIGHT)
    fancy_print("╚══════════════════════════════════════╝", Fore.CYAN, Style.BRIGHT)

def top10():
    try:
        params = {'asset': 'BUILD'}
        res = requests.get('https://api.escapemaster.net/escape_game/recent_10_issues', 
                         params=params, headers=headers).json()
        if not res.get('data'):
            fancy_print("⚠️ Lỗi: Không nhận được dữ liệu top 10!", Fore.RED, Style.BRIGHT)
            return [], []
        
        issue_id = [i['issue_id'] for i in res['data']]
        killed_room_id = [int(i['killed_room_id']) for i in res['data']]
        return issue_id, killed_room_id
    except Exception as e:
        fancy_print(f"⚠️ Lỗi khi lấy dữ liệu top 10: {e}", Fore.RED, Style.BRIGHT)
        return [], []

def top100():
    try:
        params = {'asset': 'BUILD'}
        res = requests.get('https://api.escapemaster.net/escape_game/recent_100_issues', 
                         params=params, headers=headers).json()
        if not res.get('data') or not res['data'].get('room_id_2_killed_times'):
            fancy_print("⚠️ Lỗi: Không nhận được dữ liệu top 100!", Fore.RED, Style.BRIGHT)
            return [], []
        
        room = [int(i) for i in res['data']['room_id_2_killed_times']]
        roomkill = [res['data']['room_id_2_killed_times'][i] for i in res['data']['room_id_2_killed_times']]
        return room, roomkill
    except Exception as e:
        fancy_print(f"⚠️ Lỗi khi lấy dữ liệu top 100: {e}", Fore.RED, Style.BRIGHT)
        return [], []

def detect_pattern(killed_room_id):
    patterns = defaultdict(int)
    if len(killed_room_id) >= 4:
        for i in range(len(killed_room_id) - 3):
            seq = tuple(killed_room_id[i:i+4])
            patterns[seq] += 1
    risky_rooms = set()
    for seq, count in patterns.items():
        if count >= 2:
            risky_rooms.add(seq[-1])
    return risky_rooms

def calculate_room_age(killed_room_id):
    last_seen = {}
    for i in range(len(killed_room_id)):
        last_seen[killed_room_id[i]] = i
    time_since_last = {}
    for r in range(1, 9):
        time_since_last[r] = len(killed_room_id) - last_seen.get(r, -1)
    return time_since_last

def calculate_frequency_variance(room_freq):
    freq_variance = {}
    for r in range(1, 9):
        freqs = [room_freq.get(r, 0)] * 10
        freq_variance[r] = statistics.variance(freqs) if len(freqs) > 1 else 0
    return freq_variance

def predict_safe_rooms():
    issue_id, killed_room_id = top10()
    room, roomkill = top100()
    
    if not issue_id or not room:
        fancy_print("⚠️ Không thể lấy dữ liệu từ API!", Fore.RED, Style.BRIGHT)
        return None, None, issue_id, killed_room_id
    
    room_freq = dict(zip(room, roomkill))
    for r in range(1, 9):
        if r not in room_freq:
            room_freq[r] = 0
    
    time_since_last = calculate_room_age(killed_room_id)
    freq_variance = calculate_frequency_variance(room_freq)
    hot_rooms = set(killed_room_id[-3:]) if len(killed_room_id) >= 3 else set()
    trap_rooms = set(r for r in room if room_freq[r] < 8 and r in killed_room_id[-5:])
    risky_pattern_rooms = detect_pattern(killed_room_id)
    
    final_safety_score = {}
    for r in range(1, 9):
        freq = room_freq[r]
        time_factor = time_since_last[r] ** 1.5
        variance_factor = 1 / (1 + freq_variance[r])
        hot_penalty = 0.4 if r in hot_rooms else 1.0
        trap_penalty = 0.2 if r in trap_rooms else 1.0
        pattern_penalty = 0.15 if r in risky_pattern_rooms else 1.0
        
        score = (
            0.4 * (100 - freq) * time_factor * hot_penalty * trap_penalty +
            0.3 * (100 - freq) * variance_factor * pattern_penalty +
            0.3 * (100 - freq) * time_factor * pattern_penalty
        )
        final_safety_score[r] = score
    
    sorted_safety = sorted(final_safety_score.items(), key=lambda x: x[1], reverse=True)
    safest_room = sorted_safety[0][0] if sorted_safety else 1
    second_safest_room = sorted_safety[1][0] if len(sorted_safety) > 1 else safest_room
    
    return safest_room, second_safest_room, issue_id, killed_room_id

def read_statistics():
    wins = 0
    losses = 0
    if os.path.exists("dulieu.txt"):
        with open("dulieu.txt", "r", encoding="utf-8") as f:
            for line in f:
                if "Thắng" in line:
                    wins += 1
                elif "Thua" in line:
                    losses += 1
    return wins, losses

def write_result(issue_id, killed_room, bot_choice):
    result = "Thắng" if killed_room != bot_choice else "Thua"
    with open("dulieu.txt", "a", encoding="utf-8") as f:
        f.write(f"kì {issue_id}: kết quả {killed_room}, {ROOM_NAMES[killed_room]} {result}\n")
    return result

def display_statistics():
    wins, losses = read_statistics()
    total = wins + losses
    win_rate = (wins / total * 100) if total > 0 else 0
    fancy_print("\n📊 THỐNG KÊ KẾT QUẢ", Fore.MAGENTA, Style.BRIGHT)
    fancy_print(f"✅ Số trận thắng: {wins}", Fore.GREEN, Style.BRIGHT)
    fancy_print(f"❌ Số trận thua: {losses}", Fore.RED, Style.BRIGHT)
    fancy_print(f"📈 Tỷ lệ thắng: {win_rate:.2f}%", Fore.YELLOW, Style.BRIGHT)

def check_latest_result(issue_id, killed_room_id, current_issue, bot_choice):
    if not issue_id or not killed_room_id:
        fancy_print("❌ Lỗi: Không thể lấy dữ liệu kết quả kỳ gần nhất!", Fore.RED, Style.BRIGHT)
        return False, None, None
    
    latest_issue = max(issue_id)
    if latest_issue >= current_issue:
        latest_issue_idx = issue_id.index(latest_issue)
        latest_room = killed_room_id[latest_issue_idx]
        
        current_time = dt.now().strftime("%H:%M:%S")
        fancy_print(f"\n[{current_time}] KẾT QUẢ KỲ GẦN NHẤT", Fore.GREEN, Style.BRIGHT)
        fancy_print(f"🎲 Kỳ: {latest_issue}", Fore.YELLOW, Style.BRIGHT)
        fancy_print(f"🚫 Phòng bị loại: {ROOM_NAMES[latest_room]} (Phòng {latest_room})", Fore.RED, Style.BRIGHT)
        
        result = write_result(latest_issue, latest_room, bot_choice)
        fancy_print(f"🤖 Bot chọn: {ROOM_NAMES[bot_choice]} (Phòng {bot_choice}) - {result}", 
                    Fore.GREEN if result == "Thắng" else Fore.RED, Style.BRIGHT)
        return True, latest_room, latest_issue
    return False, None, None

def predict_and_display(safest_room, second_safest_room, issue_id, current_issue, game_count, bot_choice):
    clear_screen()
    display_header()
    fancy_print("🔍 Đang phân tích dữ liệu phòng an toàn...", Fore.CYAN, Style.BRIGHT)
    time.sleep(random.uniform(1, 2))
    
    if safest_room is None or second_safest_room is None:
        fancy_print("❌ Lỗi: Không thể dự đoán phòng an toàn!", Fore.RED, Style.BRIGHT)
        return bot_choice
    
    bot_choice = safest_room if game_count % 7 < 5 else second_safest_room
    
    fancy_print("\n🎉 KẾT QUẢ DỰ ĐOÁN PHÒNG AN TOÀN 🎉", Fore.GREEN, Style.BRIGHT)
    fancy_print(f"🏆 Phòng an toàn nhất: {ROOM_NAMES[safest_room]} (Phòng {safest_room})", Fore.YELLOW, Style.BRIGHT)
    fancy_print(f"🥈 Phòng an toàn thứ hai: {ROOM_NAMES[second_safest_room]} (Phòng {second_safest_room})", Fore.YELLOW, Style.BRIGHT)
    fancy_print(f"🤖 Phòng bot chọn cho kỳ {current_issue}: {ROOM_NAMES[bot_choice]} (Phòng {bot_choice})", Fore.BLUE, Style.BRIGHT)
    fancy_print("⚠️ Lưu ý: Kết quả dựa trên phân tích dữ liệu, nhưng hãy cẩn trọng!", Fore.RED, Style.BRIGHT)
    
    display_statistics()
    return bot_choice

def main():
    previous_issue_id = []
    game_count = 0
    bot_choice = None
    current_issue = None
    
    while True:
        try:
            safest_room, second_safest_room, issue_id, killed_room_id = predict_safe_rooms()
            
            if not issue_id:
                fancy_print("❌ Lỗi: Không thể lấy số kỳ!", Fore.RED, Style.BRIGHT)
                time.sleep(10)
                continue
                
            max_issue = max(issue_id) if issue_id else 0
            if current_issue is None or max_issue >= current_issue:
                current_issue = max_issue + 1
                game_count += 1
                bot_choice = predict_and_display(safest_room, second_safest_room, issue_id, current_issue, game_count, bot_choice)
            
            if issue_id != previous_issue_id:
                result_available, latest_room, latest_issue = check_latest_result(issue_id, killed_room_id, current_issue - 1, bot_choice)
                if result_available:
                    current_issue = latest_issue + 1
                    game_count += 1
                    bot_choice = predict_and_display(safest_room, second_safest_room, issue_id, current_issue, game_count, bot_choice)
                previous_issue_id = issue_id
            
            time.sleep(1)
        except KeyboardInterrupt:
            fancy_print("\n👋 Đã thoát chương trình!", Fore.YELLOW, Style.BRIGHT)
            break
        except Exception as e:
            fancy_print(f"⚠️ Lỗi không mong muốn: {e}", Fore.RED, Style.BRIGHT)
            fancy_print("🔄 Thử lại sau 10 giây...", Fore.CYAN, Style.BRIGHT)
            time.sleep(10)
display_header()
fancy_print("Nhập user-id của bạn: ", Fore.GREEN, Style.BRIGHT,' ' )
user_id=input()
fancy_print("Nhập user-secret-key của bạn: ", Fore.GREEN, Style.BRIGHT,' ')
user_secret_key=input()
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
    'user-id': user_id,
    'user-login': 'login_v2',
    'user-secret-key': user_secret_key,
    'xb-language': 'vi-VN',
}
main()
