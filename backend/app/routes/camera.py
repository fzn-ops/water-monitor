import asyncio
import cv2
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

router = APIRouter()

# Simpan task worker yang sedang berjalan
_worker_task: asyncio.Task | None = None


class WorkerConfig(BaseModel):
    location_id: int
    camera_source: int | str = 0       # 0 = webcam, atau URL IP cam
    interval_seconds: int = 5          # jeda antar pembacaan
    tinggi_fisik_meter_cm: float = 200.0           # faktor konversi pixel → cm


@router.post("/start", status_code=status.HTTP_200_OK)
async def start_worker(config: WorkerConfig):
    """Mulai camera worker di background."""
    global _worker_task

    if _worker_task and not _worker_task.done():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Worker sudah berjalan. Stop dulu sebelum start ulang."
        )

    from app.services.camera_worker import run_camera_worker

    _worker_task = asyncio.create_task(
        run_camera_worker(
            location_id=config.location_id,
            camera_source=config.camera_source,
            interval_seconds=config.interval_seconds,
            tinggi_fisik_meter_cm=config.tinggi_fisik_meter_cm,
        )
    )

    return {
        "status": "started",
        "location_id": config.location_id,
        "camera_source": config.camera_source,
        "interval_seconds": config.interval_seconds,
        "tinggi_fisik_meter_cm": config.tinggi_fisik_meter_cm,
    }


@router.post("/stop", status_code=status.HTTP_200_OK)
async def stop_worker():
    """Hentikan camera worker."""
    global _worker_task

    if not _worker_task or _worker_task.done():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tidak ada worker yang sedang berjalan."
        )

    _worker_task.cancel()
    return {"status": "stopped"}


@router.get("/status", status_code=status.HTTP_200_OK)
async def worker_status():
    """Cek apakah camera worker sedang berjalan."""
    running = _worker_task is not None and not _worker_task.done()
    return {"running": running}

# ... (Endpoint /start, /stop, dan /status milikmu ada di atas sini) ...

async def generate_frames(camera_source: int | str = 0):
    """Generator untuk menghasilkan frame MJPEG secara terus-menerus"""
    from app.services.detection import WaterLevelDetector, CameraStream
    import asyncio
    camera_source = "simulasi_sungai1.mp4"
    # Load model tanpa kalkulasi konversi ke cm karena kita cuma butuh visual
    detector = WaterLevelDetector(tinggi_fisik_meter_cm=200.0)
    
    with CameraStream(source=camera_source) as cam:
        while True:
            ret, frame = cam.read_frame()
            if not ret or frame is None:
                await asyncio.sleep(0.1)
                continue

            # Jalankan deteksi YOLO
            result = detector.detect_frame(frame)
            annotated_frame = result["annotated_frame"]

            # Encode frame gambar numpy (OpenCV) menjadi format JPEG
            ret_encode, buffer = cv2.imencode('.jpg', annotated_frame)
            if not ret_encode:
                continue

            frame_bytes = buffer.tobytes()

            # Yield data dalam format MJPEG
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            # Jeda agar tidak membebani CPU (sekitar 30 FPS)
            await asyncio.sleep(0.03)

@router.get("/stream")
async def video_stream(camera_source: str = "0"):
    """
    Endpoint untuk menampilkan live streaming dari kamera beserta deteksi YOLO.
    """
    # Konversi ke int jika angka, biarkan string jika URL
    source = int(camera_source) if camera_source.isdigit() else camera_source
    
    return StreamingResponse(
        generate_frames(source),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )