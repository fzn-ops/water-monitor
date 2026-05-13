from app.core.config import settings


def determine_status(water_level_cm: float) -> str:
    """
    Tentukan status berdasarkan ketinggian air.
    Threshold diambil dari .env:
      - THRESHOLD_BAHAYA  (default 100 cm) → "bahaya"
      - THRESHOLD_WASPADA (default  50 cm) → "waspada"
      - di bawah itu                       → "aman"
    """
    if water_level_cm >= settings.THRESHOLD_BAHAYA:
        return "bahaya"
    elif water_level_cm >= settings.THRESHOLD_WASPADA:
        return "waspada"
    return "aman"
