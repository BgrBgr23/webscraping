"""BKM Kitap scraper modülü."""

import logging
from urllib.parse import quote_plus

from veri_cekiciler.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class BkmKitapScraper(BaseScraper):
    SOURCE_NAME = "BKM Kitap"
    BASE_URL = "https://www.bkmkitap.com"
    SEARCH_URL = "https://www.bkmkitap.com/arama?q={query}"

    def _scrape(self, query):
        """BKM Kitap'tan gerçek arama."""
        url = self.SEARCH_URL.format(query=quote_plus(query))
        soup = self.fetch_page(url)
        if not soup:
            return []

        results = []
        product_cards = soup.select('div.productItem')

        for card in product_cards:
            try:
                name_el = card.select_one('a.productName')
                name = name_el.get_text(strip=True) if name_el else None

                author_el = card.select_one('a.productAuthor, div.productAuthor a')
                author = author_el.get_text(strip=True) if author_el else ''

                price_el = card.select_one('span.product-price, div.currentPrice')
                price_text = price_el.get_text(strip=True) if price_el else '0'
                price = float(price_text.replace('.', '').replace(',', '.').replace('TL', '').strip())

                link = name_el['href'] if name_el and name_el.has_attr('href') else '#'
                if link.startswith('/'):
                    link = self.BASE_URL + link

                img_el = card.select_one('img')
                img = img_el.get('data-src', img_el.get('src', '')) if img_el else ''

                if name and price > 0:
                    results.append(self._build_product(name, author, price, link, img))
            except Exception as e:
                logger.debug(f"BKM kart ayrıştırma hatası: {e}")
                continue

        return results
