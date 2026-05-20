/* main.js */
// ── Navbar Toggle ───────────────────────────────
document.addEventListener('DOMContentLoaded', function() {
    const toggle = document.getElementById('nav-toggle');
    if (toggle) {
        toggle.addEventListener('click', function() {
            document.querySelector('.nav-links').classList.toggle('open');
        });
    }

    // Search loading
    const form = document.getElementById('search-form');
    if (form) {
        form.addEventListener('submit', function() {
            const btn = document.getElementById('search-btn');
            if (btn) {
                btn.querySelector('.btn-text').hidden = true;
                btn.querySelector('.btn-loader').hidden = false;
                btn.disabled = true;
            }
        });
    }

    // Sort buttons
    document.querySelectorAll('.sort-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.sort-btn').forEach(function(b) { b.classList.remove('active'); });
            btn.classList.add('active');
            sortResults(btn.dataset.sort);
        });
    });
});

// ── Sorting ─────────────────────────────────────
function sortResults(method) {
    var grid = document.getElementById('results-grid');
    if (!grid) return;
    var cards = Array.from(grid.querySelectorAll('.product-card'));
    cards.sort(function(a, b) {
        if (method === 'price-asc') return parseFloat(a.dataset.price) - parseFloat(b.dataset.price);
        if (method === 'price-desc') return parseFloat(b.dataset.price) - parseFloat(a.dataset.price);
        if (method === 'name') return a.dataset.name.localeCompare(b.dataset.name, 'tr');
        if (method === 'source') return a.dataset.source.localeCompare(b.dataset.source, 'tr');
        return 0;
    });
    cards.forEach(function(card) { grid.appendChild(card); });
}

// ── Toast Notifications ─────────────────────────
function showToast(message, type) {
    type = type || 'success';
    var container = document.getElementById('toast-container');
    if (!container) return;
    var toast = document.createElement('div');
    toast.className = 'toast toast-' + type;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(function() { toast.remove(); }, 3000);
}

// ── Helper: Button'dan item objesi oluştur ──────
function getItemFromButton(btn) {
    var imgUrl = btn.getAttribute('data-image_url') || btn.getAttribute('data-image-url') || btn.getAttribute('data-image') || '';
    
    return {
        name: btn.getAttribute('data-name') || '',
        author: btn.getAttribute('data-author') || '',
        price: parseFloat(btn.getAttribute('data-price')) || 0,
        source: btn.getAttribute('data-source') || '',
        url: btn.getAttribute('data-url') || '',
        image_url: imgUrl
    };
}

// ── Favorites ───────────────────────────────────
function addToFavoritesFromBtn(btn) {
    var item = getItemFromButton(btn);
    fetch('/api/favorites/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(item)
    })
    .then(function(r) { return r.json(); })
    .then(function(data) {
        if (data.success) {
            btn.classList.add('added');
            btn.textContent = '💖';
            showToast(data.message, 'success');
        } else {
            showToast(data.message, 'info');
        }
    })
    .catch(function() { showToast('Bir hata oluştu', 'error'); });
}

// ── Remove Favorite ─────────────────────────────
function removeFavorite(id) {
    var el = document.getElementById('fav-' + id);
    if (!el) return;

    var btn = el.querySelector('.action-remove');
    if (btn) {
        btn.disabled = true;
        btn.textContent = '⏳ Siliniyor...';
    }

    fetch('/api/favorites/remove/' + id, { method: 'DELETE' })
    .then(function(r) { return r.json(); })
    .then(function(data) {
        if (data.success) {
            el.style.transition = 'all 0.4s ease';
            el.style.opacity = '0';
            el.style.transform = 'scale(0.8)';
            showToast(data.message, 'success');
            setTimeout(function() {
                el.remove();
                var remaining = document.querySelectorAll('.fav-card');
                if (remaining.length === 0) {
                    location.reload();
                }
            }, 400);
        } else {
            if (btn) {
                btn.disabled = false;
                btn.textContent = '🗑️ Kaldır';
            }
            showToast(data.message || 'Bir hata oluştu', 'error');
        }
    })
    .catch(function() {
        if (btn) {
            btn.disabled = false;
            btn.textContent = '🗑️ Kaldır';
        }
        showToast('Bir hata oluştu', 'error');
    });
}

// ── Price Alerts ────────────────────────────────
var currentAlertItem = null;

function openAlertModalFromBtn(btn) {
    currentAlertItem = getItemFromButton(btn);
    document.getElementById('modal-book-name').textContent = currentAlertItem.name;
    document.getElementById('modal-current-price').textContent = currentAlertItem.price.toFixed(2) + ' \u20BA';
    document.getElementById('target-price').value = (currentAlertItem.price * 0.85).toFixed(2);
    document.getElementById('alert-modal').hidden = false;
}

function closeAlertModal() {
    document.getElementById('alert-modal').hidden = true;
    currentAlertItem = null;
}

function submitAlert() {
    if (!currentAlertItem) return;
    var targetPrice = parseFloat(document.getElementById('target-price').value);
    if (isNaN(targetPrice) || targetPrice <= 0) {
        showToast('Geçerli bir fiyat girin', 'error');
        return;
    }

    var submitBtn = document.getElementById('submit-alert-btn');
    submitBtn.disabled = true;
    submitBtn.textContent = '⏳ Kaydediliyor...';

    fetch('/api/alerts/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            name: currentAlertItem.name,
            author: currentAlertItem.author,
            target_price: targetPrice,
            current_price: currentAlertItem.price,
            source: currentAlertItem.source,
            url: currentAlertItem.url,
            image_url: currentAlertItem.image_url
        })
    })
    .then(function(r) { return r.json(); })
    .then(function(data) {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Alarmı Kur';
        if (data.success) {
            showToast(data.message, 'success');
            closeAlertModal();
        } else {
            showToast(data.message, 'error');
        }
    })
    .catch(function() {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Alarmı Kur';
        showToast('Bir hata oluştu', 'error');
    });
}

function removeAlert(id) {
    var el = document.getElementById('alert-' + id);
    if (!el) return;

    var btn = el.querySelector('.action-remove');
    if (btn) {
        btn.disabled = true;
        btn.textContent = '⏳ Siliniyor...';
    }

    fetch('/api/alerts/remove/' + id, { method: 'DELETE' })
    .then(function(r) { return r.json(); })
    .then(function(data) {
        if (data.success) {
            el.style.transition = 'all 0.4s ease';
            el.style.opacity = '0';
            el.style.transform = 'scale(0.8)';
            showToast(data.message, 'success');
            setTimeout(function() {
                el.remove();
                var remaining = document.querySelectorAll('.alert-card');
                if (remaining.length === 0) {
                    location.reload();
                }
            }, 400);
        } else {
            if (btn) {
                btn.disabled = false;
                btn.textContent = '🗑️ Sil';
            }
            showToast(data.message || 'Bir hata oluştu', 'error');
        }
    })
    .catch(function() {
        if (btn) {
            btn.disabled = false;
            btn.textContent = '🗑️ Sil';
        }
        showToast('Bir hata oluştu', 'error');
    });
}

// ── History ─────────────────────────────────────
function clearHistory() {
    var btn = document.getElementById('clear-history-btn');
    if (btn) {
        btn.disabled = true;
        btn.textContent = '⏳ Temizleniyor...';
    }

    fetch('/api/history/clear', { method: 'DELETE' })
    .then(function(r) { return r.json(); })
    .then(function(data) {
        if (data.success) {
            showToast(data.message, 'success');
            setTimeout(function() { location.reload(); }, 500);
        } else {
            if (btn) {
                btn.disabled = false;
                btn.textContent = '🗑️ Geçmişi Temizle';
            }
            showToast('Bir hata oluştu', 'error');
        }
    })
    .catch(function() {
        if (btn) {
            btn.disabled = false;
            btn.textContent = '🗑️ Geçmişi Temizle';
        }
        showToast('Bir hata oluştu', 'error');
    });
}

function animateCounters() {
    document.querySelectorAll('.stat-number-animate').forEach(function(counter) {
        var targetAttr = counter.getAttribute('data-target');
        var target = parseInt(targetAttr);
        if (isNaN(target)) return;
        
        var count = 0;
        var speed = target / 30; 
        
        var timer = setInterval(function() {
            count += Math.ceil(speed);
            if (count >= target) {
                counter.textContent = counter.getAttribute('data-original-text');
                clearInterval(timer);
            } else {
                counter.textContent = count;
            }
        }, 25); 
    });
}
document.addEventListener('DOMContentLoaded', animateCounters);