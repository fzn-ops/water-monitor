import os
import requests
import cv2
import logging
from dotenv import load_dotenv # <-- Tambahkan ini

logger = logging.getLogger(__name__)

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_alert(pesan_teks: str, frame_gambar=None):
    """
    Kirim pesan ke Telegram. Jika disertakan frame_gambar dari OpenCV,
    bot akan mengirimkan foto kejadian berserta teksnya!
    """
    # Pastikan token dan chat id ada sebelum mengirim
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        logger.error("Gagal mengirim! TELEGRAM_TOKEN atau TELEGRAM_CHAT_ID belum disetting di .env")
        return

    try:
        if frame_gambar is not None:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
            
            _, buffer = cv2.imencode('.jpg', frame_gambar)
            file_bytes = buffer.tobytes()
            
            payload = {"chat_id": TELEGRAM_CHAT_ID, "caption": pesan_teks}
            files = {"photo": ("alert.jpg", file_bytes, "image/jpeg")}
            
            requests.post(url, data=payload, files=files)
            logger.info("Foto peringatan terkirim ke Telegram!")
            
        else:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            payload = {"chat_id": TELEGRAM_CHAT_ID, "text": pesan_teks}
            
            requests.post(url, json=payload)
            logger.info("Pesan teks terkirim ke Telegram!")
            
    except Exception as e:
        logger.error(f"Gagal mengirim ke Telegram: {e}")