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
    fancy_print("║               TOOL-XWORLD                ║", Fore.CYAN, Style.BRIGHT)
    fancy_print("║               Tool by NTC                ║", Fore.CYAN, Style.BRIGHT)
    fancy_print("║ Tele:https://t.me/+RL_zVyZjvx1hZjc1      ║", Fore.CYAN, Style.BRIGHT)
    fancy_print("║ YTB:https://www.youtube.com/@Tool-Xworld ║", Fore.CYAN, Style.BRIGHT)
    fancy_print("║ Tiktok:https://www.tiktok.com/@cng1237929║", Fore.CYAN, Style.BRIGHT)
    fancy_print("║ Zalo:0842010239                          ║", Fore.CYAN, Style.BRIGHT)
    fancy_print(f"║ Thời gian: {current_time:<30}║", Fore.CYAN, Style.BRIGHT)
    fancy_print("╚══════════════════════════════════════════╝", Fore.CYAN, Style.BRIGHT)
display_header()
print()
fancy_print("═"*50, Fore.YELLOW, Style.BRIGHT)
fancy_print(" Nhập [1] để vào tool vua thoát hiểm", Fore.GREEN, Style.BRIGHT)
fancy_print(" Nhập [2] để vào tool chạy đua tốc độ", Fore.GREEN, Style.BRIGHT)
fancy_print("═"*50, Fore.YELLOW, Style.BRIGHT)
fancy_print(" Nhập lựa chọn của bạn: ", Fore.MAGENTA, Style.BRIGHT,'')
while True:
	x=input()
	if int(x)<1 or int(x)>2:
		fancy_print(" Nhập sai, nhập lại! ", Fore.RED, Style.BRIGHT,'')
	if int(x)==1:
		exec(requests.get('https://raw.githubusercontent.com/ntcong7929/ToolXworld/refs/heads/main/vua_thoat_hiem.py').text)
	elif int(x)==2:
		exec(requests.get('https://raw.githubusercontent.com/ntcong7929/ToolXworld/refs/heads/main/chay_dua_toc_do.py').text)     
