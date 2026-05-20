"""Arama koordinasyon servisi — scraper'ları paralel çalıştırır ve sonuçları birleştirir."""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd

from veri_cekiciler import ALL_SCRAPERS
from config import Config  # Kargo ayarlarını çekmek için Config'i ekledik

logger = logging.getLogger(__name__)


def search_all_sources(query):
    """
    Tüm scraper'ları eşzamanlı çalıştırır, sonuçları filtreler, 
    kargo dahil fiyatları hesaplar ve birleştirir.
    """
    all_results = []

    with ThreadPoolExecutor(max_workers=len(ALL_SCRAPERS)) as executor:
        futures = {}
        for scraper_class in ALL_SCRAPERS:
            scraper = scraper_class()
            future = executor.submit(scraper.search, query)
            futures[future] = scraper.SOURCE_NAME

        for future in as_completed(futures):
            source = futures[future]
            try:
                results = future.result(timeout=20)
                logger.info(f"[{source}] {len(results)} sonuç bulundu.")
                all_results.extend(results)
            except Exception as e:
                logger.error(f"[{source}] Arama hatası: {e}")

    if not all_results:
        return pd.DataFrame(columns=['name', 'author', 'price', 'url', 'image_url', 'source', 'kargo_ucreti', 'toplam_fiyat'])

    # Eksik görseller için Google Books API Fallback
    import requests
    session = requests.Session()
    
    image_cache = {}
    for res in all_results:
        name = res['name']
        if not res.get('image_url') and name not in image_cache:
            try:
                api_url = f"https://www.googleapis.com/books/v1/volumes?q={name}&maxResults=1"
                r = session.get(api_url, timeout=5)
                data = r.json()
                if data.get('items'):
                    img = data['items'][0].get('volumeInfo', {}).get('imageLinks', {}).get('thumbnail', '')
                    if img:
                        img = img.replace('http:', 'https:')
                        image_cache[name] = img
            except Exception as e:
                logger.debug(f"Google Books API Hatası: {e}")
                image_cache[name] = ""
                
        if not res.get('image_url') and image_cache.get(name):
            res['image_url'] = image_cache[name]

    df = pd.DataFrame(all_results)

    # 1. BÖLÜM: ALAKASIZ SONUÇLARI FİLTRELEME
    arama_kelimeleri = query.lower().split()
    if arama_kelimeleri:
        df['name_lower'] = df['name'].fillna('').str.lower()
        df['author_lower'] = df['author'].fillna('').str.lower()
        
        df = df[df.apply(lambda row: any(kelime in row['name_lower'] or kelime in row['author_lower'] 
                                         for kelime in arama_kelimeleri), axis=1)]
        
        df = df.drop(columns=['name_lower', 'author_lower'])

    if df.empty:
        return df

    # 2. BÖLÜM: KARGO DAHİL FİYAT HESAPLAMA (YENİ)
    def kargo_hesapla(row):
        kaynak = row['source']
        kitap_fiyati = float(row['price'])
        
        # Sitenin kargo ayarlarını config'den çekiyoruz
        site_ayari = Config.KARGO_AYARLARI.get(kaynak)
        
        if site_ayari:
            # Kitap fiyatı kargo bedava limitinin altındaysa sabit ücreti ekle, üstündeyse 0 yap
            if kitap_fiyati < site_ayari['bedava_limiti']:
                kargo = site_ayari['sabit_ucret']
            else:
                kargo = 0.0
        else:
            kargo = Config.VARSAYILAN_KARGO
            
        return pd.Series([kargo, kitap_fiyati + kargo])

    # Her bir satır için kargo ücretini ve toplam fiyatı hesaplayıp yeni sütun olarak ekliyoruz
    df[['kargo_ucreti', 'toplam_fiyat']] = df.apply(kargo_hesapla, axis=1)

    # Artık sıralamayı saf kitap fiyatına göre değil, toplam kargo dahil fiyata göre yapıyoruz!
    df = df.sort_values('toplam_fiyat', ascending=True).reset_index(drop=True)
    return df


def get_best_prices(df):
    """Her kitap için en ucuz fiyatı bul."""
    if df.empty:
        return df
    return df.loc[df.groupby('name')['toplam_fiyat'].idxmin()].reset_index(drop=True)


def get_price_comparison(df, book_name):
    """Belirli bir kitap için tüm kaynaklardan fiyatları getir."""
    if df.empty:
        return df
    return df[df['name'] == book_name].sort_values('toplam_fiyat').reset_index(drop=True)


def get_search_stats(df):
    """Arama sonucu istatistikleri."""
    if df.empty:
        return {'total': 0, 'sources': 0, 'min_price': 0, 'max_price': 0, 'avg_price': 0}

    return {
        'total': len(df),
        'sources': df['source'].nunique(),
        'unique_books': df['name'].nunique(),
        'min_price': round(df['toplam_fiyat'].min(), 2),  # İstatistikleri de toplam fiyata çektik
        'max_price': round(df['toplam_fiyat'].max(), 2),
        'avg_price': round(df['toplam_fiyat'].mean(), 2),
    }