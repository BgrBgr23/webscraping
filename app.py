"""Flask ana uygulama — Web Scraping Fiyat Karşılaştırma Aracı."""

import logging
import os
from pathlib import Path
from flask import Flask, render_template, request, jsonify, redirect, url_for

from config import Config


logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(name)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


proje_dizini = Path(__file__).resolve().parent
taslak_yolu = proje_dizini / 'arayuz' / 'templates'  
statik_yolu = proje_dizini / 'arayuz' / 'statik'     

app = Flask(__name__, 
            template_folder=str(taslak_yolu), 
            static_folder=str(statik_yolu))
app.config.from_object(Config)

from servisler.veritabani import (
    init_db, save_search, get_search_history, clear_search_history,
    add_favorite, get_favorites, remove_favorite,
    add_price_alert, get_price_alerts, remove_price_alert
)
from servisler.arama_servisi import search_all_sources, get_search_stats
from servisler.grafik_servisi import create_comparison_chart
init_db()


@app.route('/')
def index():
    """Ana sayfa — arama formu."""
    history = get_search_history(limit=5)
    return render_template('index.html', recent_searches=history)


@app.route('/search')
def search():
    """Arama sonuçları sayfası."""
    query = request.args.get('q', '').strip()
    if not query:
        return redirect(url_for('index'))

    logger.info(f"Arama yapılıyor: '{query}'")

    df = search_all_sources(query)
    stats = get_search_stats(df)

    save_search(query, stats['total'])

    chart_base64 = create_comparison_chart(df, query)

    results = df.to_dict('records') if not df.empty else []

    return render_template('results.html',
                           query=query,
                           results=results,
                           stats=stats,
                           chart_base64=chart_base64)


@app.route('/category/<cat_name>')
def category_filter(cat_name):
    """Seçilen kategoriye ait kitapları listeler."""
    from veri_cekiciler.base_scraper import CENTRAL_DEMO_BOOKS
    import pandas as pd
    
    logger.info(f"Kategori filtreleniyor: '{cat_name}'")

    filtered_books = [b for b in CENTRAL_DEMO_BOOKS if b.get('category', '').lower() == cat_name.lower()]
    
    if not filtered_books:
        return render_template('results.html', results=[], query=f"Kategori: {cat_name}", stats={'total': 0, 'sources': 0, 'min_price': 0, 'avg_price': 0})
    
    all_results = []
    for book in filtered_books:
        df_book = search_all_sources(book['name'])
        if not df_book.empty:
            all_results.append(df_book)
            
    if all_results:
        df_all = pd.concat(all_results, ignore_index=True)
        stats = get_search_stats(df_all)
        chart_base64 = create_comparison_chart(df_all, f"Kategori: {cat_name}")
        results = df_all.to_dict('records')
    else:
        results = []
        stats = {'total': 0, 'sources': 0, 'min_price': 0, 'avg_price': 0}
        chart_base64 = None

    return render_template('results.html',
                           query=f"Kategori: {cat_name}",
                           results=results,
                           stats=stats,
                           chart_base64=chart_base64)



@app.route('/history')
def history():
    """Arama geçmişi sayfası."""
    searches = get_search_history(limit=50)
    return render_template('history.html', searches=searches)


@app.route('/favorites')
def favorites():
    """Favoriler sayfası."""
    favs = get_favorites()
    return render_template('favorites.html', favorites=favs)


@app.route('/alerts')
def alerts():
    """Fiyat alarmları sayfası."""
    alert_list = get_price_alerts()
    return render_template('alerts.html', alerts=alert_list)




@app.route('/api/favorites/add', methods=['POST'])
def api_add_favorite():
    """Favorilere ekle."""
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'success': False, 'message': 'Geçersiz veri'}), 400

    result = add_favorite(
        product_name=data['name'],
        author=data.get('author', ''),
        min_price=data.get('price', 0),
        source=data.get('source', ''),
        url=data.get('url', ''),
        image_url=data.get('image_url', '')
    )

    if result:
        return jsonify({'success': True, 'message': 'Favorilere eklendi!'})
    else:
        return jsonify({'success': False, 'message': 'Bu kitap zaten favorilerde.'})


@app.route('/api/favorites/remove/<int:fav_id>', methods=['DELETE'])
def api_remove_favorite(fav_id):
    """Favorilerden kaldır."""
    remove_favorite(fav_id)
    return jsonify({'success': True, 'message': 'Favorilerden kaldırıldı.'})


@app.route('/api/alerts/add', methods=['POST'])
def api_add_alert():
    """Fiyat alarmı ekle (Resim destekli)."""
    data = request.get_json()
    if not data or 'name' not in data or 'target_price' not in data:
        return jsonify({'success': False, 'message': 'Geçersiz veri'}), 400

    add_price_alert(
        product_name=data['name'],
        author=data.get('author', ''),
        target_price=float(data['target_price']),
        current_price=float(data.get('current_price', 0)),
        source=data.get('source', ''),
        url=data.get('url', ''),
        image_url=data.get('image_url', '') 
    )

    return jsonify({'success': True, 'message': 'Fiyat alarmı oluşturuldu!'})


@app.route('/api/alerts/remove/<int:alert_id>', methods=['DELETE'])
def api_remove_alert(alert_id):
    """Fiyat alarmını sil."""
    remove_price_alert(alert_id)
    return jsonify({'success': True, 'message': 'Alarm silindi.'})


@app.route('/api/history/clear', methods=['DELETE'])
def api_clear_history():
    """Arama geçmişini temizle."""
    clear_search_history()
    return jsonify({'success': True, 'message': 'Geçmiş temizlendi.'})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)