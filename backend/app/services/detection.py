import cv2
import numpy as np
from ultralytics import YOLO
from pathlib import Path
import logging
import torch

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

    def __init__(self, model_path: str = str(MODEL_PATH), pixel_to_cm: float = 0.5):
        """
        Args:
            model_path   : Path ke file .pt hasil training
            pixel_to_cm  : Faktor konversi pixel ke cm (kalibrasi manual)
                           Contoh: 0.5 berarti 1 pixel = 0.5 cm
                           Sesuaikan dengan jarak kamera ke meteran
        """
        self.pixel_to_cm = pixel_to_cm
        self.model = None
        self._load_model(model_path)

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

    def detect_frame(self, frame: np.ndarray) -> dict:
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
            print(f">>> TERPILIH: staff_gauge (conf: {best_meter_conf:.2f})")
        if water_box:
            print(f">>> TERPILIH: water_level (conf: {best_water_conf:.2f})")

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

        # Hitung jarak air pakai fungsi yang sudah kamu perbaiki sebelumnya
        pixel_distance, water_level_cm = self._calculate_water_level(meter_box, water_box)

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
        Hitung tinggi air dalam cm menggunakan meteran sebagai referensi skala.

        Rumus:
            pixel_per_cm   = tinggi_pixel_meteran / tinggi_fisik_meteran_cm
            pixel_distance = meter_bottom - water_top
            water_level_cm = pixel_distance / pixel_per_cm
        """
        if water_box is None:
            return 0.0, 0.0

        DASAR_METERAN_Y = 400.0

        # === 2. AMBIL TITIK PERMUKAAN AIR ===
        water_y = (water_box[1] + water_box[3]) / 2

        # === 3. HITUNG JARAK ===
        # Jarak dari dasar sungai (0 cm) naik ke permukaan air
        pixel_distance = DASAR_METERAN_Y - water_y
        
        # Jika air berada di bawah dasar meteran, anggap 0
        if pixel_distance < 0:
            pixel_distance = 0.0

        # === 4. KONVERSI KE CM (Gunakan self.pixel_to_cm dari __init__) ===
        water_level_cm = round(pixel_distance * self.pixel_to_cm, 2)

        print(f">>> Posisi Air Y  : {water_y:.1f}px")
        print(f">>> Jarak Naiknya : {pixel_distance:.1f}px")
        print(f">>> Tinggi Air    : {water_level_cm:.2f} cm")

        return pixel_distance, water_level_cm


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
        Baca satu frame dari kamera.

        Returns:
            (True, frame)  — jika berhasil
            (False, None)  — jika gagal
        """
        if self.cap is None or not self.cap.isOpened():
            return False, None
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