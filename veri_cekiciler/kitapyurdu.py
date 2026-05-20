"""Kitapyurdu.com scraper modülü."""

import logging
import re
from urllib.parse import quote_plus

from veri_cekiciler.base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class KitapyurduScraper(BaseScraper):
    SOURCE_NAME = "Kitapyurdu"
    BASE_URL = "https://www.kitapyurdu.com"
    SEARCH_URL = "https://www.kitapyurdu.com/index.php?route=product/search&filter_name={query}"

    def _scrape(self, query):
        """Kitapyurdu.com'dan güncel arama sayfa yapısına göre veri çeker."""
        url = self.SEARCH_URL.format(query=quote_plus(query))
        soup = self.fetch_page(url)
        if not soup:
            return []

        results = []
        
        product_cards = soup.select('div.product-cr')

        for card in product_cards:
            try:
                title_el = card.select_one('div.name a')
                if not title_el:
                    continue
                
                raw_name = title_el.get_text(strip=True)
                
                publisher_el = card.select_one('div.publisher a')
                publisher = publisher_el.get_text(strip=True) if publisher_el else ""
                
                name = f"{raw_name} ({publisher})" if publisher else raw_name

                author_el = card.select_one('div.author a')
                author = author_el.get_text(strip=True) if author_el else ''

                price_new = card.select_one('div.price-new .value')
                price_old = card.select_one('div.price .value')
                
                price_text = ''
                if price_new:
                    price_text = price_new.get_text(strip=True)
                elif price_old:
                    price_text = price_old.get_text(strip=True)
                else:
                    price_div = card.select_one('div.price')
                    if price_div:
                        price_text = price_div.get_text(strip=True)
                
                price = 0.0
                if price_text:
                    match = re.search(r'([\d.,]+)', price_text)
                    if match:
                        clean_text = match.group(1)
                        if ',' in clean_text and '.' in clean_text:
                            clean_text = clean_text.replace('.', '').replace(',', '.')
                        elif ',' in clean_text:
                            clean_text = clean_text.replace(',', '.')
                        price = float(clean_text)

                link = title_el['href'] if title_el.has_attr('href') else '#'
                if link.startswith('/'):
                    link = self.BASE_URL + link

                img_el = card.select_one('div.image img')
                img = ''
                if img_el:
                    img = img_el.get('src') or img_el.get('data-src') or ''

                if name and price > 0:
                    results.append(self._build_product(name, author, price, link, img))
            except Exception as e:
                logger.debug(f"Kitapyurdu kart ayrıştırma hatası: {e}")
                continue

        return results