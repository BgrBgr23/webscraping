import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'kitap-fiyat-karsilastirma-gizli-2024')
    
    DATABASE_PATH = os.path.join(BASE_DIR, 'veri.db')
    
    CHART_DIR = os.path.join(BASE_DIR, 'arayuz', 'statik', 'grafikler')
    
    SCRAPER_TIMEOUT = 30
    SCRAPER_MAX_RETRIES = 2
    MAX_RESULTS_PER_SOURCE = 10
    
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
    ]

    KARGO_AYARLARI = {
        'Kitapyurdu': {'sabit_ucret': 45.0, 'bedava_limiti': 400.0},
        'BKM Kitap':   {'sabit_ucret': 39.0, 'bedava_limiti': 350.0},
        'İdefix':      {'sabit_ucret': 49.0, 'bedava_limiti': 500.0}
    }
    VARSAYILAN_KARGO = 40.0