"""Matplotlib ile fiyat karşılaştırma grafikleri oluşturma servisi."""

import io
import base64
import logging

import matplotlib
matplotlib.use('Agg')  # GUI olmadan çalıştır
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd

logger = logging.getLogger(__name__)

# Kaynak renk paleti
SOURCE_COLORS = {
    'Kitapyurdu': '#6C5CE7',
    'BKM Kitap': '#00B894',
    'İdefix': '#E17055',
}

DEFAULT_COLOR = '#74B9FF'


def create_comparison_chart(df, query):
    """
    Fiyat karşılaştırma bar chart oluştur.
    Returns: base64 encoded PNG string
    """
    if df.empty:
        return None

    try:
        # Dark tema ayarları
        plt.rcParams.update({
            'figure.facecolor': '#0f0f23',
            'axes.facecolor': '#1a1a35',
            'axes.edgecolor': '#2d2d5e',
            'axes.labelcolor': '#e0e0ff',
            'text.color': '#e0e0ff',
            'xtick.color': '#b0b0d0',
            'ytick.color': '#b0b0d0',
            'grid.color': '#2d2d5e',
            'grid.alpha': 0.5,
            'font.size': 11,
        })

        # Kitap başına kaynak bazlı fiyat pivot tablosu
        unique_books = df['name'].unique()

        if len(unique_books) == 1:
            # Tek kitap: kaynak bazlı yatay bar chart
            book_df = df[df['name'] == unique_books[0]]
            fig, ax = plt.subplots(figsize=(10, max(4, len(book_df) * 0.8)))

            colors = [SOURCE_COLORS.get(s, DEFAULT_COLOR) for s in book_df['source']]
            bars = ax.barh(book_df['source'], book_df['price'], color=colors,
                          height=0.5, edgecolor='none', alpha=0.9)

            # Fiyat etiketleri
            for bar, price in zip(bars, book_df['price']):
                ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height() / 2,
                       f'{price:.2f} ₺', va='center', fontweight='bold', fontsize=12,
                       color='#e0e0ff')

            ax.set_xlabel('Fiyat (₺)', fontsize=12, fontweight='bold')
            ax.set_title(f'📚 {unique_books[0]}', fontsize=14, fontweight='bold', pad=15)
            ax.xaxis.set_major_formatter(mticker.FormatStrFormatter('%.0f ₺'))

        else:
            # Birden fazla kitap: gruplu bar chart
            sources = df['source'].unique()
            pivot = df.pivot_table(index='name', columns='source', values='price', aggfunc='min')

            fig, ax = plt.subplots(figsize=(12, max(5, len(unique_books) * 1.2)))

            y_positions = range(len(pivot.index))
            bar_height = 0.25
            offset = 0

            for i, source in enumerate(sources):
                if source in pivot.columns:
                    values = pivot[source].fillna(0)
                    color = SOURCE_COLORS.get(source, DEFAULT_COLOR)
                    positions = [y + (i - len(sources) / 2) * bar_height for y in y_positions]
                    bars = ax.barh(positions, values, height=bar_height, label=source,
                                  color=color, alpha=0.85, edgecolor='none')

                    for bar, val in zip(bars, values):
                        if val > 0:
                            ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
                                   f'{val:.0f}₺', va='center', fontsize=9, color='#c0c0e0')

            ax.set_yticks(list(y_positions))
            # Kitap isimlerini kısalt
            short_names = [n[:30] + '…' if len(n) > 30 else n for n in pivot.index]
            ax.set_yticklabels(short_names, fontsize=10)
            ax.set_xlabel('Fiyat (₺)', fontsize=12, fontweight='bold')
            ax.set_title(f'📊 "{query}" Fiyat Karşılaştırması', fontsize=14, fontweight='bold', pad=15)
            ax.legend(loc='lower right', framealpha=0.3, edgecolor='none')
            ax.xaxis.set_major_formatter(mticker.FormatStrFormatter('%.0f ₺'))

        ax.grid(axis='x', linestyle='--', alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        plt.tight_layout()

        # Base64'e dönüştür
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight',
                    facecolor=fig.get_facecolor(), edgecolor='none')
        plt.close(fig)
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        return img_base64

    except Exception as e:
        logger.error(f"Grafik oluşturma hatası: {e}")
        plt.close('all')
        return None


def create_price_history_chart(prices, book_name):
    """Fiyat geçmişi çizgi grafiği (gelecek genişleme için)."""
    # İleride fiyat takibi eklendiğinde kullanılacak
    pass
