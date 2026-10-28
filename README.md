# 🎬 Nyaa.si Anime Çeviri & Bölüm Takipçisi

[![Arch Linux](https://img.shields.io/badge/Arch%20Linux-AUR%20%7C%20PKGBUILD-1793d1?style=for-the-badge&logo=arch-linux&logoColor=white)](https://github.com/KaranlikPasa/nyaa-anime-tracker)
[![Platform](https://img.shields.io/badge/Platform-Arch%20Linux%20%7C%20Windows-blue?style=for-the-badge)](https://github.com/KaranlikPasa/nyaa-anime-tracker)
[![GitHub Release](https://img.shields.io/github/v/release/KaranlikPasa/nyaa-anime-tracker?style=for-the-badge&color=2563eb)](https://github.com/KaranlikPasa/nyaa-anime-tracker/releases/latest)

Bu uygulama, **Türkçe Anime Çeviri (Fansub) Ekipleri** için özel olarak geliştirilmiş modern, hafif ve arka planda sessizce çalışan bir bildirim ve takip sistemidir. **Arch Linux** ve **Windows** üzerinde tam uyumlu çalışır.

[Nyaa.si](https://nyaa.si/) sitesine takip ettiğiniz animeyle ilgili yeni bir İngilizce bölüm (SubsPlease, Erai-raws vb.) yüklendiği anda **masaüstü bildirimi** gönderir ve tek tıkla bölüme ulaşmanızı sağlar.

---

## 📥 Kurulum

### 🐧 1. Arch Linux Kurulumu

#### Yöntem A: PKGBUILD ile Kurulum
```bash
git clone https://github.com/KaranlikPasa/nyaa-anime-tracker.git
cd nyaa-anime-tracker
makepkg -si
```

#### Yöntem B: Tek Komutla Kurulum Betiği (`install.sh`)
```bash
git clone https://github.com/KaranlikPasa/nyaa-anime-tracker.git
cd nyaa-anime-tracker
chmod +x install.sh
sudo ./install.sh
```

Kurulum tamamlandıktan sonra uygulama menünüzden (Rofi, Wofi, GNOME, KDE) **Nyaa Anime Takipçisi**'ni başlatabilir veya terminalden doğrudan şu komutu verebilirsiniz:
```bash
nyaa-anime-tracker
```

---

### 🪟 2. Windows Kurulumu (.EXE veya Kaynak Kod)

#### Hazır .EXE İle:
👉 **[📦 NyaaAnimeTakipcisi-v1.0.0-Windows.zip İndir (Son Sürüm)](https://github.com/KaranlikPasa/nyaa-anime-tracker/releases/latest)**

#### Kaynak Koddan:
- `Baslat.bat`: Çift tıklayarak başlatabilirsiniz.
- `ArkaPlandaBaslat.vbs`: Konsol penceresi olmadan doğrudan sessizce başlatır.

---

## ✨ Özellikler

1. **Anlık Masaüstü Bildirimleri**:
   - **Linux:** `notify-send` (libnotify) ile masaüstü ortamınızla (GNOME, KDE, Dunst, Mako vb.) entegre native bildirimler.
   - **Windows:** Sesli Windows 10/11 Toast bildirimleri.
   - Bildirime tıkladığınızda doğrudan ilgili sayfaya yönlendirir.

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
   - Pencereyi kapattığınızda (`X`) program kapanmaz, sistem tepsisine küçülerek takip etmeye devam eder.
   - Tepsi ikonuna sağ tıklayarak anında durumu kontrol edebilir, duraklatabilir veya arayüzü tekrar açabilirsiniz.

5. **Sistem Başlangıcında Otomatik Başlama**:
   - **Linux:** `~/.config/autostart` üzerinden sistem açılışında arka planda başlar.
   - **Windows:** Windows Başlangıç kayıt defteri üzerinden otomatik başlar.

---

## 🛠️ Manuel Çalıştırma (Python)

```bash
pip install -r requirements.txt
python main.py
```

---

## 📄 Lisans
MIT License
