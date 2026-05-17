import requests
import cv2
import logging
from app.core.config import settings # <-- IMPORT SETTINGS KAMU

logger = logging.getLogger(__name__)

# --- SEKARANG DIAMBIL DARI CENTRAL CONFIG ---
TELEGRAM_TOKEN = settings.TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID = settings.TELEGRAM_CHAT_ID

def send_telegram_alert(pesan_teks: str, frame_gambar=None):
    """
    Kirim pesan ke Telegram dengan deteksi log langsung di terminal.
    """
    print("\n==== 🛡️ JALUR TELEGRAM DIAKSES ====")
    print(f"-> Token Terbaca  : {TELEGRAM_TOKEN}")
    print(f"-> Chat ID Terbaca: {TELEGRAM_CHAT_ID}")
    
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("KESALAHAN: Token atau Chat ID kosong di .env! Gagal kirim.")
        print("=========================================\n")
        return

    try:
        if frame_gambar is not None:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
            _, buffer = cv2.imencode('.jpg', frame_gambar)
            file_bytes = buffer.tobytes()
            
            payload = {"chat_id": TELEGRAM_CHAT_ID, "caption": pesan_teks}
            files = {"photo": ("alert.jpg", file_bytes, "image/jpeg")}
            
            print("-> Mencoba menembak API Telegram (Photo)...")
            response = requests.post(url, data=payload, files=files)
            print(f"-> Respon Telegram: Status Code {response.status_code}")
            print(f"-> Detail Respon: {response.text}")
            
        else:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            payload = {"chat_id": TELEGRAM_CHAT_ID, "text": pesan_teks}
            
            print("-> Mencoba menembak API Telegram (Text Only)...")
            response = requests.post(url, json=payload)
            print(f"-> Respon Telegram: Status Code {response.status_code}")
            print(f"-> Detail Respon: {response.text}")
            
        print("=========================================\n")
            
    except Exception as e:
        print(f"ERROR JARINGAN TELEGRAM: {e}")
        print("=========================================\n")