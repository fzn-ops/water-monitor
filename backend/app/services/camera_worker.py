import asyncio
import traceback
from datetime import datetime
import httpx
import torch
import ultralytics.nn.tasks

# URL API Backend (Pastikan URL ini sesuai dengan port uvicorn kamu berjalan)
API_BASE = "http://127.0.0.1:8000/api/v1"

async def run_camera_worker(location_id: int, camera_source: int | str = 0,
                            interval_seconds: int = 5, pixel_to_cm: float = 0.5):
    """
    Background worker: baca frame kamera setiap `interval_seconds` detik,
    deteksi level air menggunakan YOLO, lalu kirim ke API /readings.
    """
    print("\n========== WORKER KAMERA DIMULAI ==========")
    print(f"-> Lokasi ID     : {location_id}")
    print(f"-> Sumber Kamera : {camera_source}")
    print(f"-> Interval      : {interval_seconds} detik")
    
    try:
        # 1. Bypass keamanan PyTorch 2.6 agar YOLO bisa di-load (PENTING)
        print("-> Mempersiapkan environment PyTorch...")
        torch.serialization.add_safe_globals([ultralytics.nn.tasks.DetectionModel])
        
        # 2. Import class deteksi di dalam fungsi
        from app.services.detection import WaterLevelDetector, CameraStream

        # 3. Load Model YOLO
        print("-> Mencoba load model YOLO (best.pt)...")
        detector = WaterLevelDetector(pixel_to_cm=pixel_to_cm)
        print("-> [SUCCESS] Model YOLO berhasil dimuat!")

        # 4. Hubungkan ke Kamera (Webcam / IP Cam)
        print(f"-> Mencoba menyambungkan ke kamera...")
        with CameraStream(source=camera_source) as cam:
            print("\n>>> [SUCCESS] KAMERA TERHUBUNG! Memulai pemantauan... <<<\n")
            
            async with httpx.AsyncClient() as client:
                while True:
                    try:
                        # Ambil frame dari kamera
                        ret, frame = cam.read_frame()
                        if not ret or frame is None:
                            print(f"[{datetime.now().strftime('%H:%M:%S')}] [WARNING] Gagal membaca frame dari kamera. Mencoba lagi...")
                            await asyncio.sleep(2)
                            continue

                        # Lakukan deteksi YOLO
                        result = detector.detect_frame(frame)

                        # Jika tidak ada meteran/air terdeteksi (0.0 cm)
                        if result["water_level_cm"] == 0.0:
                            print(f"[{datetime.now().strftime('%H:%M:%S')}] Tidak ada objek terdeteksi di kamera. Skip ke frame selanjutnya...")
                            await asyncio.sleep(interval_seconds)
                            continue

                        # Siapkan Payload JSON untuk dikirim ke API POST /readings/
                        payload = {
                            "location_id": location_id,
                            "water_level_cm": float(result["water_level_cm"]),
                            "pixel_distance": float(result["pixel_distance"]),
                        }

                        # Kirim request ke Database via API FastAPI
                        response = await client.post(f"{API_BASE}/readings/", json=payload)
                        response.raise_for_status()

                        # Berhasil disimpan!
                        print(
                            f"[{datetime.now().strftime('%H:%M:%S')}] "
                            f"[BERHASIL DISIMPAN] Level Air: {result['water_level_cm']} cm | "
                            f"Jarak: {result['pixel_distance']} px"
                        )

                    except httpx.HTTPError as e:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] [ERROR API] Gagal mengirim data ke Database: {e}")
                    except Exception as e:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] [ERROR DETEKSI] Terjadi kesalahan saat memproses gambar: {e}")

                    # Tunggu sebelum membaca frame berikutnya
                    await asyncio.sleep(interval_seconds)

    except asyncio.CancelledError:
        # Ini ditrigger otomatis saat kamu menembak endpoint POST /stop
        print("\n========== WORKER KAMERA DIHENTIKAN OLEH USER ==========")
        
    except Exception as e:
        # Menangkap error fatal seperti Path YOLO salah, atau Kamera tidak ada
        print(f"\n[FATAL ERROR] Worker kamera mati mendadak! Penyebab:")
        print(e)
        traceback.print_exc()
        
    finally:
        print("========== PROSES WORKER SELESAI ==========\n")