# Water Monitor Backend

Backend API untuk sistem monitoring level air berbasis YOLOv8 + FastAPI.

## Tech Stack
- **FastAPI** — Web framework async
- **PostgreSQL** — Database utama
- **SQLAlchemy 2.0** — ORM async
- **Alembic** — Database migrations
- **YOLOv8** — Object detection
- **python-telegram-bot** — Notifikasi Telegram

---

## Setup Project

### 1. Clone & buat virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Konfigurasi environment
```bash
cp .env.example .env
# Edit file .env sesuai konfigurasi kamu
```

Isi `.env`:
```
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/water_monitor
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id
THRESHOLD_WASPADA=50
THRESHOLD_BAHAYA=100
DEBUG=True
```

### 4. Buat database PostgreSQL
```bash
# Masuk ke psql
psql -U postgres

# Buat database
CREATE DATABASE water_monitor;
\q
```

### 5. Jalankan migrasi database
```bash
# Buat migrasi pertama
alembic revision --autogenerate -m "create initial tables"

# Jalankan migrasi
alembic upgrade head
```

### 6. Jalankan server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Buka browser: http://localhost:8000/docs

---

## Struktur Folder

```
water-monitor/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py           # Konfigurasi settings dari .env
│   │   │   └── database.py         # Koneksi PostgreSQL
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── alert.py            # Model tabel alerts
│   │   │   ├── location.py         # Model tabel locations
│   │   │   └── reading.py          # Model tabel readings
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── alert.py            # Schema request/response alert
│   │   │   ├── location.py         # Schema request/response location
│   │   │   └── reading.py          # Schema request/response reading
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── alerts.py           # Endpoint alerts
│   │   │   ├── camera.py           # Endpoint kontrol kamera worker
│   │   │   ├── locations.py        # Endpoint lokasi sensor
│   │   │   └── readings.py         # Endpoint data pembacaan air
│   │   ├── services/
│   │   │   ├── camera_worker.py    # Background worker kamera realtime
│   │   │   ├── detection.py        # YOLOv8 + OpenCV water detection
│   │   │   └── reading_service.py  # Business logic pembacaan air
│   │   ├── utils/                  # Helper / utility functions
│   │   └── main.py                 # Entry point FastAPI
│   │
│   ├── alembic/
│   │   ├── versions/
│   │   │   └── 02ec2916ff76_create_initial_tables.py
│   │   ├── env.py
│   │   └── script.py.mako
│   │
│   ├── yolo_model/
│   │   └── best.pt                 # Model YOLO hasil training
│   │
│   ├── .env.example
│   ├── alembic.ini
│   ├── README.md
│   └── requirements.txt
│
├── .gitignore
└── venv/                           # Virtual environment (tidak dipush)
```

---

## API Endpoints (akan datang)

| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| GET | `/api/v1/locations` | List semua lokasi |
| POST | `/api/v1/locations` | Tambah lokasi baru |
| GET | `/api/v1/readings` | List semua pembacaan |
| POST | `/api/v1/readings` | Tambah pembacaan baru |
| GET | `/api/v1/alerts` | List semua alert |

---

## Database Schema

```
locations (1) ──< readings (1) ──< alerts
```

- **locations** — Data lokasi monitoring (nama, koordinat, foto)
- **readings** — Hasil pembacaan level air per waktu
- **alerts** — Log peringatan yang dikirim ke Telegram
```
