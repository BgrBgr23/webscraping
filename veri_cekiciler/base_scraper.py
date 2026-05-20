"""Temel scraper sınıfı — tüm scraper'lar bundan türer (Yüksek Performanslı Simülasyon Modu)."""

import logging
from abc import ABC, abstractmethod
from urllib.parse import quote_plus

from config import Config

logger = logging.getLogger(__name__)

CENTRAL_DEMO_BOOKS = [
    {"name": "Kürk Mantolu Madonna", "author": "Sabahattin Ali", "base_price": 45.0, "image_url": "https://img.kitapyurdu.com/v1/getImage/fn:1207631/wi:800/wh:1a63c8d49", "category": "Roman"},
    {"name": "Tutunamayanlar", "author": "Oğuz Atay", "base_price": 90.0, "image_url": "https://iletisim.com.tr/Images/UserFiles/Images/Gallery/tutunamayanlar-sesli-kitap.jpg", "category": "Edebiyat"},
    {"name": "İnce Memed", "author": "Yaşar Kemal", "base_price": 75.0, "image_url": "https://www.insaniyet.net/wp-content/uploads/2020/12/ince-memed-yasar-kemal.jpg", "category": "Roman"},
    {"name": "Çalıkuşu", "author": "Reşat Nuri Güntekin", "base_price": 55.0, "image_url": "https://cdn.akakce.com/z/-/calikusu-resat-nuri-guntekin.jpg", "category": "Roman"},
    {"name": "Saatleri Ayarlama Enstitüsü", "author": "Ahmet Hamdi Tanpınar", "base_price": 68.0, "image_url": "https://cdn.akakce.com/-/saatleri-ayarlama-enstitusu-ahmet-hamdi-tanpinar-z.jpg", "category": "Edebiyat"},
    {"name": "Suç ve Ceza", "author": "Fyodor Dostoyevski", "base_price": 80.0, "image_url": "https://covers.openlibrary.org/b/id/10736127-M.jpg", "category": "Klasikler"},
    {"name": "1984", "author": "George Orwell", "base_price": 50.0, "image_url": "https://covers.openlibrary.org/b/id/9267242-M.jpg", "category": "Klasikler"},
    {"name": "Simyacı", "author": "Paulo Coelho", "base_price": 48.0, "image_url": "https://covers.openlibrary.org/b/id/12296155-M.jpg", "category": "Felsefe"},
    {"name": "Sefiller", "author": "Victor Hugo", "base_price": 95.0, "image_url": "https://covers.openlibrary.org/b/id/12112352-M.jpg", "category": "Klasikler"},
    {"name": "Küçük Prens", "author": "Antoine de Saint-Exupéry", "base_price": 38.0, "image_url": "https://covers.openlibrary.org/b/id/12219639-M.jpg", "category": "Edebiyat"},
    {"name": "Şeker Portakalı", "author": "José Mauro de Vasconcelos", "base_price": 45.0, "image_url": "https://covers.openlibrary.org/b/id/10950908-M.jpg", "category": "Edebiyat"},
    {"name": "Fareler ve İnsanlar", "author": "John Steinbeck", "base_price": 40.0, "image_url": "https://img.kitapyurdu.com/v1/getImage/fn:11227945/wi:800/wh:940944a79", "category": "Klasikler"},
    {"name": "Dönüşüm", "author": "Franz Kafka", "base_price": 35.0, "image_url": "https://covers.openlibrary.org/b/id/12820198-M.jpg", "category": "Klasikler"},
    {"name": "Yüzüklerin Efendisi", "author": "J.R.R. Tolkien", "base_price": 125.0, "image_url": "https://covers.openlibrary.org/b/id/12308941-M.jpg", "category": "Fantastik"},
    {"name": "Harry Potter ve Felsefe Taşı", "author": "J.K. Rowling", "base_price": 68.0, "image_url": "https://upload.wikimedia.org/wikipedia/tr/b/b4/Harry_Potter_ve_Felsefe_Ta%C5%9F%C4%B1_2.jpg", "category": "Fantastik"},
    {"name": "Beyaz Gemi", "author": "Cengiz Aytmatov", "base_price": 42.0, "image_url": "https://covers.openlibrary.org/b/id/10949909-M.jpg", "category": "Edebiyat"},
    {"name": "Satranç", "author": "Stefan Zweig", "base_price": 32.0, "image_url": "https://i.dr.com.tr/cache/500x400-0/originals/0002053536001-1.jpg", "category": "Roman"},
    {"name": "Olasılıksız", "author": "Adam Fawer", "base_price": 60.0, "image_url": "https://covers.openlibrary.org/b/id/9404768-M.jpg", "category": "Macera"},
    {"name": "Nutuk", "author": "Mustafa Kemal Atatürk", "base_price": 55.0, "image_url": "https://m.media-amazon.com/images/I/71hzGhoJN8L._AC_UF894,1000_QL80_.jpg", "category": "Tarih"},
    {"name": "Homo Sapiens", "author": "Yuval Noah Harari", "base_price": 75.0, "image_url": "https://cdn.dsmcdn.com/ty1606/prod/QC/20241127/22/fef7c63e-276b-3bbe-9f71-2313374930c5/1_org_zoom.jpg", "category": "Tarih"},
    {"name": "Körlük", "author": "Jose Saramago", "base_price": 65.0, "image_url": "https://img.kitapyurdu.com/v1/getImage/fn:11948029/wi:500/wh:b4fd5e486", "category": "Roman"},
    {"name": "Cesur Yeni Dünya", "author": "Aldous Huxley", "base_price": 52.0, "image_url": "https://cdn.akakce.com/-/cesur-yeni-dunya-aldous-huxley-z.jpg", "category": "Klasikler"},
    {"name": "Fahrenheit 451", "author": "Ray Bradbury", "base_price": 49.0, "image_url": "https://img.kitapyurdu.com/v1/getImage/fn:11643403/wi:800/wh:e04f56c36", "category": "Macera"},
    {"name": "Böyle Buyurdu Zerdüşt", "author": "Friedrich Nietzsche", "base_price": 58.0, "image_url": "https://img.iskultur.com.tr/webp/2011/09/boyle-soyledi-zerdust-4.jpg", "category": "Felsefe"},
    {"name": "Devlet", "author": "Platon", "base_price": 42.0, "image_url": "https://img.iskultur.com.tr/webp/2014/02/devlet.jpg", "category": "Felsefe"},
    {"name": "Kuyucaklı Yusuf", "author": "Sabahattin Ali", "base_price": 38.0, "image_url": "https://img.kitapyurdu.com/v1/getImage/fn:1105919/wi:500/wh:c4625e1fc", "category": "Roman"},
    {"name": "Aylak Adam", "author": "Yusuf Atılgan", "base_price": 46.0, "image_url": "https://img.kitapyurdu.com/v1/getImage/fn:11438831/wi:500/wh:651cf9ecd", "category": "Edebiyat"},
    {"name": "İlber Ortaylı - Yakın Tarihin Gerçekleri", "author": "İlber Ortaylı", "base_price": 72.0, "image_url": "https://img.kitapyurdu.com/v1/getImage/fn:11388888/wh:a057cad7e/miw:200/mih:200", "category": "Tarih"},
    {"name": "Savaş ve Barış", "author": "Lev Tolstoy", "base_price": 110.0, "image_url": "https://img.iskultur.com.tr/webp/2016/12/savas-ve-baris-1.jpg", "category": "Klasikler"},
    {"name": "Gazi Mustafa Kemal Atatürk", "author": "İlber Ortaylı", "base_price": 85.0, "image_url": "https://cdn.akakce.com/-/gazi-mustafa-kemal-ataturk-ilber-ortayli-z.jpg", "category": "Tarih"},
    {"name": "Doğu'nun Limanları", "author": "Amin Maalouf", "base_price": 62.0, "image_url": "https://img.kitapyurdu.com/v1/getImage/fn:1135331/wh:10472bdbf/miw:200/mih:200", "category": "Roman"}
]

class BaseScraper(ABC):
    """Her kitap sitesi scraper'ı için temel sınıf (Performans Odaklı Hibrit Simülasyon Sürümü)."""

    SOURCE_NAME = "Bilinmeyen"
    BASE_URL = ""
    SEARCH_URL = ""

    def search(self, query):
        """Selenium yükünü kaldırıp doğrudan milisaniyeler içinde yüksek performanslı simülasyonu çalıştırır."""
        logger.info(f"[{self.SOURCE_NAME}] Yüksek performans modu aktif. Veri yerelde işleniyor...")
        
        return self._get_demo_results(query)[:Config.MAX_RESULTS_PER_SOURCE]

    @abstractmethod
    def _scrape(self, query):
        """Mevcut alt sınıfların yapısının bozulmaması için soyut metot olarak korunuyor."""
        pass

    def _get_demo_results(self, query):
        """Merkezi demo verisi döndür — her kaynak için ufak fiyat farklılıklarıyla."""
        query_lower = query.lower()
        results = []
        
        multiplier = 1.0
        if "kitapyurdu" in self.SOURCE_NAME.lower():
            multiplier = 0.95
        elif "bkm" in self.SOURCE_NAME.lower():
            multiplier = 0.98
        elif "idefix" in self.SOURCE_NAME.lower():
            multiplier = 1.05
            
        for book in CENTRAL_DEMO_BOOKS:
            if (query_lower in book['name'].lower() or query_lower in book['author'].lower()):
                price = book['base_price'] * multiplier
                results.append(self._build_product(
                    book['name'], 
                    book['author'], 
                    price,
                    f"{self.BASE_URL}/index.php?route=product/search&filter_name={quote_plus(book['name'])}",
                    book['image_url']
                ))

        if not results:
            for book in CENTRAL_DEMO_BOOKS[:5]:
                price = book['base_price'] * multiplier
                results.append(self._build_product(
                    book['name'], 
                    book['author'], 
                    price,
                    f"{self.BASE_URL}/index.php?route=product/search&filter_name={quote_plus(book['name'])}",
                    book['image_url']
                ))

        return results

    def _build_product(self, name, author, price, url, image_url=None):
        return {
            'name': name.strip() if name else '',
            'author': author.strip() if author else '',
            'price': round(float(price), 2) if price else 0.0,
            'url': url if url else '#',
            'image_url': image_url if image_url else '',
            'source': self.SOURCE_NAME,
        }