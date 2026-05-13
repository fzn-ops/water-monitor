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
        """
        Proses satu frame gambar.

        Returns dict:
        {
            "water_level_cm": float,   # estimasi tinggi air dalam cm
            "pixel_distance": float,   # jarak pixel permukaan air
            "meter_box": list | None,  # bounding box meteran [x1,y1,x2,y2]
            "water_box": list | None,  # bounding box permukaan air
            "annotated_frame": ndarray # frame dengan anotasi kotak deteksi
        }
        """
        results = self.model(frame, verbose=False)[0]
        annotated = results.plot()  # frame dengan kotak deteksi

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

            # >>> BARIS DEBUGGING (Akan muncul di terminal) <<<
            print(f">>> YOLO MELIHAT OBJEK: {cls_name} (conf: {conf:.2f})")

            # >>> PENYESUAIAN LABEL NAMA CLASS <<<
            if conf < MIN_CONF:
                print(f">>> DIABAIKAN: {cls_name} confidence terlalu rendah ({conf:.2f} < {MIN_CONF})")
                continue
            if cls_name == "staff_gauge" and conf > best_meter_conf:
                meter_box = coords
                best_meter_conf = conf
            elif cls_name == "water_level" and conf > best_water_conf:
                water_box = coords
                best_water_conf = conf

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
        meter_height_cm: float = 240.0,  # ← sesuaikan tinggi fisik meteran kamu
    ) -> tuple[float, float]:
        """
        Hitung tinggi air dalam cm menggunakan meteran sebagai referensi skala.

        Rumus:
            pixel_per_cm   = tinggi_pixel_meteran / tinggi_fisik_meteran_cm
            pixel_distance = meter_bottom - water_top
            water_level_cm = pixel_distance / pixel_per_cm
        """
        if meter_box is None or water_box is None:
            return 0.0, 0.0

        # Tinggi meteran dalam pixel
        meter_top    = meter_box[1]   # y1 meteran (atas)
        meter_bottom = meter_box[3]   # y2 meteran (bawah)
        meter_height_px = meter_bottom - meter_top

        if meter_height_px <= 0:
            return 0.0, 0.0

        # Skala: berapa pixel per 1 cm
        pixel_per_cm = meter_height_px / meter_height_cm

        # Jarak pixel dari permukaan air ke dasar meteran
        water_y = (water_box[1] + water_box[3]) / 2
        pixel_distance = max(0.0, round(meter_bottom - water_y, 2))

        # Konversi ke cm
        water_level_cm = round(pixel_distance / pixel_per_cm, 2)

        print(f">>> Meteran: {meter_height_px:.1f}px = {meter_height_cm}cm")
        print(f">>> Skala: {pixel_per_cm:.2f} px/cm")
        print(f">>> Jarak pixel air: {pixel_distance:.1f}px")
        print(f">>> Tinggi air: {water_level_cm:.2f} cm")

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