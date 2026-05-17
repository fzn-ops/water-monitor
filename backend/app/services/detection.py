import cv2
import numpy as np
from ultralytics import YOLO
from pathlib import Path
import logging
import torch
import time
from app.services.telegram_bot import send_telegram_alert
from app.core.config import settings

logger = logging.getLogger(__name__)

# Path ke model .pt — taruh file model kamu di folder yolo_model/
MODEL_PATH = Path(__file__).parent.parent.parent / "yolo_model" / "best.pt"


class WaterLevelDetector:
    """
    Deteksi level air menggunakan YOLOv8 + OpenCV.

    Alur:
      1. Baca frame dari kamera
      2. Jalankan YOLOv8 → deteksi bounding box meteran & permukaan air
      3. Hitung jarak pixel antara permukaan air dan dasar meteran
      4. Konversi pixel → cm menggunakan skala kalibrasi
    """

    def __init__(self, model_path: str = str(MODEL_PATH), tinggi_fisik_meter_cm: float = 200.0):
        """
        Args:
            model_path   : Path ke file .pt hasil training
            pixel_to_cm  : Faktor konversi pixel ke cm (kalibrasi manual)
                           Contoh: 0.5 berarti 1 pixel = 0.5 cm
                           Sesuaikan dengan jarak kamera ke meteran
        """
        self.tinggi_fisik_meter_cm = tinggi_fisik_meter_cm
        
        self.model = None
        self._load_model(model_path)

        self.last_alert_time = 0
        self.batas_bahaya_cm = settings.THRESHOLD_BAHAYA

    def _load_model(self, model_path: str):
        """Load model YOLOv8 dari file .pt"""
        if not Path(model_path).exists():
            raise FileNotFoundError(
                f"Model tidak ditemukan: {model_path}\n"
                f"Taruh file .pt kamu di folder yolo_model/ dengan nama 'best.pt'"
            )
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f">>> DEVICE: {'GPU (CUDA)' if torch.cuda.is_available() else 'CPU'}")
        print(f">>> CUDA available: {torch.cuda.is_available()}")

        logger.info(f"Loading model dari: {model_path}")
        self.model = YOLO(model_path)
        self.model.to(device)
        logger.info("Model berhasil dimuat.")

    def detect_frame(self, frame: np.ndarray, location_name: str = "Lokasi Simulasi",trigger_alarm: bool = True) -> dict:
        # Inference YOLO, tidak perlu plot otomatis lagi
        results = self.model(frame, verbose=False)[0]

        meter_box = None
        water_box = None
        best_meter_conf = 0.0
        best_water_conf = 0.0
        MIN_CONF = 0.5

        for box in results.boxes:
            cls_id = int(box.cls[0])
            cls_name = self.model.names[cls_id].lower()
            coords = box.xyxy[0].tolist()  # [x1, y1, x2, y2]
            conf = float(box.conf[0])

            # 1. Langsung abaikan yang di bawah threshold (terminal jadi bersih)
            if conf < MIN_CONF:
                continue

            # 2. Cari kotak dengan confidence tertinggi untuk masing-masing class
            if (cls_name == "meter" or cls_name == "staff_gauge") and conf > best_meter_conf:
                meter_box = coords
                best_meter_conf = conf
            elif (cls_name == "water_surface" or cls_name == "water_level") and conf > best_water_conf:
                water_box = coords
                best_water_conf = conf

        # --- LOG TERMINAL: Hanya print pemenang tertingginya saja ---
        if meter_box:
            logger.debug(f">>> TERPILIH: staff_gauge (conf: {best_meter_conf:.2f})")
        if water_box:
            logger.debug(f">>> TERPILIH: water_level (conf: {best_water_conf:.2f})")

        # --- GAMBAR KOTAK MANUAl (Hanya 1 Kotak Terbaik) ---
        annotated = frame.copy() # Salin gambar asli agar tidak rusak

        if meter_box:
            # OpenCV butuh angka bulat (integer) untuk menggambar koordinat
            x1, y1, x2, y2 = map(int, meter_box)
            # Gambar kotak warna Hijau (0, 255, 0) ketebalan 2
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
            # Tulis label di atas kotaknya
            cv2.putText(annotated, f"Staff Gauge {best_meter_conf:.2f}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        if water_box:
            x1, y1, x2, y2 = map(int, water_box)
            # Gambar kotak warna Biru (255, 0, 0) ketebalan 2
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.putText(annotated, f"Water Level {best_water_conf:.2f}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

        # Hitung jarak air pakai
        pixel_distance, water_level_cm = self._calculate_water_level(meter_box, water_box)

        if trigger_alarm and water_level_cm > self.batas_bahaya_cm:
            waktu_sekarang = time.time()    
            # Cek apakah sudah lewat 5 menit (300 detik) sejak alarm terakhir
            if waktu_sekarang - self.last_alert_time > 300:
                pesan_bahaya = (
                    f"🚨 PERINGATAN BAHAYA BANJIR! 🚨\n\n"
                    f"📍 Lokasi: {location_name}\n"
                    f"🌊 Tinggi Air Terdeteksi: {water_level_cm:.2f} cm\n"
                    f"⚠️ Status: Melewati batas aman ({self.batas_bahaya_cm} cm)\n\n"
                    f"Mohon segera lakukan pengecekan lokasi!"
                )
                
                # Kirim pesan + gambar hasil deteksi AI (annotated)
                send_telegram_alert(pesan_bahaya, frame_gambar=annotated)
                
                # Perbarui waktu memori agar tidak spam
                self.last_alert_time = waktu_sekarang

        return {
            "water_level_cm": water_level_cm,
            "pixel_distance": pixel_distance,
            "meter_box": meter_box,
            "water_box": water_box,
            "annotated_frame": annotated,
        }

    def _calculate_water_level(
        self,
        meter_box: list | None,
        water_box: list | None,
    ) -> tuple[float, float]:
        """
        Hitung tinggi air menggunakan METODE JANGKAR ATAS + SKALA LEBAR DINAMIS.
        Tahan terhadap kamera goyang dan efek Zoom!
        """
        if meter_box is None or water_box is None:
            return 0.0, 0.0

        # =======================================================
        # 1. HITUNG SKALA DINAMIS MENGGUNAKAN LEBAR METERAN
        # =======================================================
        # GANTI ANGKA INI dengan ukuran lebar fisik papan penggarismu di dunia nyata
        # (Misalnya: papan meteran lebarnya 15 cm)
        LEBAR_FISIK_METER_CM = 30.0 
        
        # Lebar pixel = titik x kanan dikurangi titik x kiri (x2 - x1)
        lebar_pixel_meter = meter_box[2] - meter_box[0]

        # Cegah error "dibagi 0" jika AI sesaat nge-bug / kotak terlalu kecil
        if lebar_pixel_meter <= 0:
            return 0.0, 0.0

        # Rasio pixel/cm sekarang murni dinamis menyesuaikan Zoom kamera!
        PIXEL_PER_CM = lebar_pixel_meter / LEBAR_FISIK_METER_CM


        # =======================================================
        # 2. METODE JANGKAR ATAS (MENGUKUR JARAK TURUN)
        # =======================================================
        # y1 meteran (Ujung paling atas papan meteran)
        meter_top_y = meter_box[1] 
        
        # y1 air (Garis atas permukaan air)
        water_y = water_box[1]     

        # Jarak dari ujung atas meteran turun ke permukaan air
        pixel_distance_from_top = water_y - meter_top_y
        
        if pixel_distance_from_top < 0:
            pixel_distance_from_top = 0.0


        # =======================================================
        # 3. KONVERSI & KALKULASI TINGGI AIR AKHIR
        # =======================================================
        cm_dari_atas = pixel_distance_from_top / PIXEL_PER_CM
        
        # Tinggi air = Tinggi papan total - Jarak dari atas
        water_level_cm = round(self.tinggi_fisik_meter_cm - cm_dari_atas, 2)

        # Pastikan tidak ada angka minus jika air surut jauh di luar kamera
        if water_level_cm < 0:
            water_level_cm = 0.0 

        # --- LOG TERMINAL (Tersembunyi, hanya muncul kalau mode debug aktif) ---
        logger.debug(f">>> [DINAMIS] Lebar Pixel Meteran  : {lebar_pixel_meter:.1f} px")
        logger.debug(f">>> [DINAMIS] Skala Saat Ini       : {PIXEL_PER_CM:.2f} px/cm")
        logger.debug(f">>> [DINAMIS] Jarak Turun          : {cm_dari_atas:.2f} cm")
        logger.debug(f">>> TINGGI AIR SEBENARNYA          : {water_level_cm:.2f} cm")
        return pixel_distance_from_top, water_level_cm
    
class CameraStream:
    """
    Kelola stream kamera menggunakan OpenCV.
    Mendukung webcam lokal (index int) dan IP camera (URL string).
    """

    def __init__(self, source: int | str = 0):
        """
        Args:
            source: 0 untuk webcam pertama,
                    1 untuk webcam kedua,
                    "rtsp://..." atau "http://..." untuk IP camera
        """
        self.source = source
        self.cap = None

    def open(self):
        """Buka koneksi kamera."""
        self.cap = cv2.VideoCapture(self.source)
        if not self.cap.isOpened():
            raise RuntimeError(
                f"Tidak bisa membuka kamera: {self.source}\n"
                f"Pastikan kamera terhubung atau URL IP camera benar."
            )
        logger.info(f"Kamera terbuka: {self.source}")

    def read_frame(self) -> tuple[bool, np.ndarray | None]:
        """
        Baca satu frame dari kamera atau file video.
        Jika input berupa file video dan sudah habis, otomatis rewind ke frame awal (loop).
        """
        if self.cap is None or not self.cap.isOpened():
            return False, None
            
        ret, frame = self.cap.read()
        
        # === FITUR AUTO-LOOP UNTUK FILE VIDEO LOKAL ===
        # Jika frame gagal dibaca (video habis) dan source-nya adalah teks (bukan angka webcam/IP cam)
        if not ret and isinstance(self.source, str) and not self.source.startswith(("rtsp://", "http://", "https://")):
            logger.info(">>> Video simulasi habis. Mengulang kembali dari awal...")
            # Reset posisi frame ke indeks 0
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.cap.read()
            
        return ret, frame if ret else None

    def release(self):
        """Tutup koneksi kamera."""
        if self.cap:
            self.cap.release()
            logger.info("Kamera ditutup.")

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, *_):
        self.release()