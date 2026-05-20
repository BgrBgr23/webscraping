from .base_scraper import BaseScraper
from .bkm_kitap import BkmKitapScraper
from .idefix import IdefixScraper
from .kitapyurdu import KitapyurduScraper

ALL_SCRAPERS = [BkmKitapScraper, IdefixScraper, KitapyurduScraper]
