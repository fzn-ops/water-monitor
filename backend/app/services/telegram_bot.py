import requests
import cv2
import logging

logger = logging.getLogger(__name__)

# Masukkan Token dan Chat ID dari Langkah 1 & 2
TELEGRAM_TOKEN = "8941800842:AAESbrrkPw34lhwxnS44WN1LZAwCGrBPUPw"
TELEGRAM_CHAT_ID = "5260425458"

def send_telegram_alert(pesan_teks: str, frame_gambar=None):
    """
    Kirim pesan ke Telegram. Jika disertakan frame_gambar dari OpenCV,
    bot akan mengirimkan foto kejadian berserta teksnya!
    """
    try:
        if frame_gambar is not None:
            # Jika ada gambar (AI mendeteksi bahaya), kirim foto + caption
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
            
            # Ubah gambar OpenCV (numpy) menjadi file JPG
            _, buffer = cv2.imencode('.jpg', frame_gambar)
            file_bytes = buffer.tobytes()
            
            payload = {"chat_id": TELEGRAM_CHAT_ID, "caption": pesan_teks}
            files = {"photo": ("alert.jpg", file_bytes, "image/jpeg")}
            
            requests.post(url, data=payload, files=files)
            logger.info("Foto peringatan terkirim ke Telegram!")
            
        else:
            # Jika hanya teks biasa
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            payload = {"chat_id": TELEGRAM_CHAT_ID, "text": pesan_teks}
            
            requests.post(url, json=payload)
            logger.info("Pesan teks terkirim ke Telegram!")
            
    except Exception as e:
        logger.error(f"Gagal mengirim ke Telegram: {e}")