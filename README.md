# 🎬 Nyaa.si Anime Çeviri & Bölüm Takipçisi

[![GitHub Release](https://img.shields.io/github/v/release/KaranlikPasa/nyaa-anime-tracker?style=for-the-badge&color=2563eb)](https://github.com/KaranlikPasa/nyaa-anime-tracker/releases/latest)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-blue?style=for-the-badge)](https://github.com/KaranlikPasa/nyaa-anime-tracker/releases/latest)

Bu uygulama, **Türkçe Anime Çeviri (Fansub) Ekipleri** için özel olarak geliştirilmiş modern, hafif ve arka planda sessizce çalışan bir bildirim ve takip sistemidir.

[Nyaa.si](https://nyaa.si/) sitesine takip ettiğiniz animeyle ilgili yeni bir İngilizce bölüm (SubsPlease, Erai-raws vb.) yüklendiği anda **Windows masaüstü bildirimi** gönderir ve tek tıkla bölüme ulaşmanızı sağlar.

---

## ⬇️ İndirme (Doğrudan Çalıştırılabilir .EXE)

Terminal veya Python kurulumu ile uğraşmak istemeyenler için hazır Windows paketi:

👉 **[📦 NyaaAnimeTakipcisi-v1.0.0-Windows.zip İndir (Son Sürüm)](https://github.com/KaranlikPasa/nyaa-anime-tracker/releases/latest)**

> **Kullanım:** İndirdiğiniz `.zip` dosyasını bir klasöre çıkartın ve `NyaaAnimeTakipcisi.exe` dosyasına çift tıklayarak çalıştırın!
> 
> 💡 *Not: Windows SmartScreen mavi uyarı ekranı ("Windows kişisel bilgisayarınızı korudu") gösterirse:*
> Sol taraftaki **"Ek bilgi"** bağlantısına tıklayıp **"Yine de çalıştır"** butonuna basmanız yeterlidir. (Açık kaynaklı ve bağımsız uygulamalarda Windows ilk açılışta bunu gösterir; virüs değildir, tek seferlik izin vermeniz yeterlidir).*

---

## ✨ Özellikler

1. **Anlık Masaüstü Bildirimleri (Windows Toast)**:
   - Yeni bölüm yüklendiğinde ekranın sağ altında sesli bildirim çıkar.
   - Bildirime tıkladığınızda veya *"Nyaa'da Aç"* / *"Torrent İndir"* butonlarına bastığınızda doğrudan ilgili sayfaya yönlendirir.

2. **Gelişmiş Arayüz (CustomTkinter)**:
   - Modern, göz yormayan karanlık tema (Dark Mode).
   - Takip edilecek animeleri kolayca ekleme / silme / duraklatma.
   - Çözünürlük filtresi (`1080p`, `720p`, `Tümü`).
   - Grup filtresi (`SubsPlease`, `Erai-raws` vb. isteğe bağlı).
   - İstenmeyen kelimeleri hariç tutma (Örn: `Dub`, `Batch`, `Raw`).

3. **Bölüm Geçmişi & Magnet Link**:
   - Yakalanan tüm bölümler listelenir.
   - Tek tıkla torrent indirme, sayfayı açma veya **🧲 Magnet linkini panoya kopyalama** imkanı.

4. **Arka Planda Çalışma (Sistem Tepsisi - Tray)**:
   - Pencereyi kapattığınızda (`X`) program kapanmaz, sistem tepsisine (sağ alttaki saat yanına) küçülerek takip etmeye devam eder.
   - Tepsi ikonuna sağ tıklayarak anında durumu kontrol edebilir, duraklatabilir veya arayüzü tekrar açabilirsiniz.

5. **Bilgisayar Başlarken Otomatik Başlama**:
   - Ayarlar sekmesindeki *"Bilgisayar açıldığında otomatik başlasın"* seçeneğiyle Windows başlangıcına eklenir.
   - Bilgisayar açıldığında hiçbir pencere açmadan doğrudan arka planda sessizce başlar.

---

## 🚀 Başlatma Yöntemleri

Klasör içinde hazır kısayollar bulunmaktadır:

- **`Baslat.bat`**: Normal başlatıcı. Çift tıklayarak arayüzü doğrudan açabilirsiniz.
- **`ArkaPlandaBaslat.vbs`**: Tamamen gizli modda başlatır (herhangi bir siyah konsol penceresi açılmaz, doğrudan sistem tepsisine yerleşir).
- **`Baslat_Konsollu.bat`**: Hata ayıklama veya konsol çıktılarını görmek isterseniz.

---

## 🛠️ Kurulum & Bağımlılıklar

Gereksinimler Python ortamınızda zaten yüklü veya şu komutla kurulabilir:
```bash
pip install -r requirements.txt
```

Paketler:
- `customtkinter` (Modern arayüz)
- `winotify` (Windows yerel bildirim sistemi)
- `pystray` (Sistem tepsisi - Tray entegrasyonu)
- `pillow` (Görsel ve ikon işleme)

---

## 📦 Tek Dosya (.exe) Haline Getirme (İsteğe Bağlı)

Eğer uygulamanın Python kurulu olmayan diğer çevirmen arkadaşlarınızda da çalışmasını isterseniz:
```bash
python build_exe.py
```
komutunu çalıştırdığınızda `dist/NyaaAnimeTakipcisi.exe` adında tek parça çalıştırılabilir bir program oluşturur.
