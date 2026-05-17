from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import locations, readings, alerts, camera
from app.core.config import settings
from app.core.database import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: pastikan tabel sudah ada (development only)
    if settings.DEBUG:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown: tutup koneksi engine
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",       # Swagger UI
    redoc_url="/redoc",     # ReDoc
    lifespan=lifespan,
)

origins = [
    "http://localhost:5173",  # Port default Vite React
    "http://127.0.0.1:5173",
]

# CORS - izinkan frontend akses API
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,    # ganti dengan domain frontend saat production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# from app.routes import locations, readings, alerts
app.include_router(locations.router, prefix="/api/v1/locations", tags=["Locations"])
app.include_router(readings.router, prefix="/api/v1/readings", tags=["Readings"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["Alerts"])
app.include_router(camera.router, prefix="/api/v1/camera", tags=["Camera Worker"])


@app.get("/", tags=["Health"])
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}
