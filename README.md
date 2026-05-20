# 📚 KitapBul - Kitap Fiyat Karşılaştırma ve Web Scraping Sistemi

## 📖 Proje Hakkında

KitapBul, farklı kitap satış platformlarındaki ürünleri karşılaştırarak kullanıcılara en uygun fiyatı sunmayı amaçlayan bir web tabanlı fiyat karşılaştırma sistemidir. 

Sistem; Kitapyurdu, BKM Kitap ve İdefix gibi popüler kitap satış sitelerinden gerçek zamanlı veriler çekerek kullanıcıya fiyat, kargo durumu ve kitap bilgilerini tek ekranda göstermektedir.

Bu proje, web scraping teknolojileri ile veri toplama, Flask ile web uygulaması geliştirme ve SQLite ile veri yönetimi konularını bir araya getiren kapsamlı bir uygulamadır.

---

# 🎯 Projenin Amacı

Bu projenin temel amacı:

- Kullanıcının aynı kitabı farklı sitelerde tek tek aramak zorunda kalmasını önlemek
- En uygun fiyatı hızlı şekilde bulabilmek
- Fiyat karşılaştırmasını otomatik hale getirmek
- Kullanıcı deneyimini kolaylaştırmak
- Web scraping mantığını gerçek bir proje üzerinde uygulamak

---

# 🚀 Proje Özellikleri

## ✅ Gerçek Zamanlı Veri Çekme
Sistem, kitap satış sitelerinden anlık veriler çekmektedir.

Desteklenen platformlar:
- Kitapyurdu
- BKM Kitap
- İdefix

---

## ✅ Fiyat Karşılaştırma Sistemi
Aynı kitabın farklı sitelerdeki fiyatları karşılaştırılır ve kullanıcıya listelenir.

---

## ✅ Kargo Dahil Fiyat Hesaplama
Bazı sitelerde ürün fiyatı düşük olsa bile kargo ücreti toplam maliyeti artırabilir.

Bu nedenle sistem:
- Ürün fiyatını
- Kargo durumunu
- Toplam maliyeti

birlikte değerlendirir.

---

## ✅ Favoriler Sistemi
Kullanıcılar beğendikleri kitapları favorilere ekleyebilir.

---

## ✅ Fiyat Alarmı Sistemi
Kullanıcı belirli bir fiyat girerek alarm oluşturabilir.

Kitap bu fiyatın altına düştüğünde sistem uyarı verecek şekilde hazırlanmıştır.

---

## ✅ Arama Geçmişi
Yapılan aramalar SQLite veritabanında saklanır.

Bu sayede:
- Kullanıcı geçmiş aramalarını görebilir
- Veri analizi yapılabilir
- Popüler kitaplar takip edilebilir

---

## ✅ Grafiksel Veri Analizi
Matplotlib ve Pandas kullanılarak:
- Fiyat dağılımı
- Site karşılaştırmaları
- Ortalama fiyat analizleri

grafik halinde gösterilmektedir.

---

# 🛠️ Kullanılan Teknolojiler

## Backend
- Python
- Flask
- SQLite

## Web Scraping
- BeautifulSoup4
- Requests
- lxml

## Veri Analizi
- Pandas
- Matplotlib

## Frontend
- HTML5
- CSS3
- JavaScript

---