import asyncio
import cv2
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

router = APIRouter()

# Ganti dari satu task → dictionary of tasks
_worker_tasks: dict[int, asyncio.Task] = {}


class WorkerConfig(BaseModel):
    location_id: int
    location_name: str
    camera_source: int | str = 0
    interval_seconds: int = 5
    tinggi_fisik_meter_cm: float = 200.0


@router.post("/start", status_code=status.HTTP_200_OK)
async def start_worker(config: WorkerConfig):
    """Mulai camera worker di background."""
    # Cek apakah lokasi ini sudah ada worker yang jalan
    existing = _worker_tasks.get(config.location_id)
    if existing and not existing.done():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Worker untuk lokasi {config.location_id} sudah berjalan."
        )

    from app.services.camera_worker import run_camera_worker

    task = asyncio.create_task(
        run_camera_worker(
            location_id=config.location_id,
            camera_source=config.camera_source,
            location_name=config.location_name,
            interval_seconds=config.interval_seconds,
            tinggi_fisik_meter_cm=config.tinggi_fisik_meter_cm,
        )
    )
    _worker_tasks[config.location_id] = task

    return {
        "status": "started",
        "location_id": config.location_id,
        "camera_source": config.camera_source,
    }


@router.post("/stop", status_code=status.HTTP_200_OK)
async def stop_worker(location_id: int):
    """Hentikan camera worker berdasarkan location_id."""
    task = _worker_tasks.get(location_id)

    if not task or task.done():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tidak ada worker yang berjalan untuk lokasi {location_id}."
        )

    task.cancel()
    del _worker_tasks[location_id]
    return {"status": "stopped", "location_id": location_id}


@router.post("/stop-all", status_code=status.HTTP_200_OK)
async def stop_all_workers():
    """Hentikan semua camera worker."""
    if not _worker_tasks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tidak ada worker yang sedang berjalan."
        )

    stopped = []
    for loc_id, task in list(_worker_tasks.items()):
        if not task.done():
            task.cancel()
            stopped.append(loc_id)
    _worker_tasks.clear()

    return {"status": "all stopped", "location_ids": stopped}


@router.get("/status", status_code=status.HTTP_200_OK)
async def worker_status():
    """Cek status semua camera worker."""
    return {
        "workers": [
            {"location_id": loc_id, "running": not task.done()}
            for loc_id, task in _worker_tasks.items()
        ]
    }

async def generate_frames(camera_source: int | str = 0, tinggi_fisik_meter_cm: float = 200.0):
    """Generator untuk menghasilkan frame MJPEG secara terus-menerus"""
    from app.services.detection import WaterLevelDetector, CameraStream

    detector = WaterLevelDetector(tinggi_fisik_meter_cm=tinggi_fisik_meter_cm)

    with CameraStream(source=camera_source) as cam:
        while True:
            ret, frame = cam.read_frame()
            if not ret or frame is None:
                await asyncio.sleep(0.1)
                continue

            result = detector.detect_frame(frame,trigger_alarm=False)
            annotated_frame = result["annotated_frame"]

            ret_encode, buffer = cv2.imencode('.jpg', annotated_frame)
            if not ret_encode:
                continue

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

            await asyncio.sleep(0.03)


@router.get("/stream")
async def video_stream(camera_source: str = "0", tinggi_fisik_meter_cm: float = 200.0):
    """Live streaming dari kamera beserta deteksi YOLO."""
    source = int(camera_source) if camera_source.isdigit() else camera_source

    return StreamingResponse(
        generate_frames(source, tinggi_fisik_meter_cm),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )