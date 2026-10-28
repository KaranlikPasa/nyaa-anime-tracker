# Maintainer: KaranlikPasa <https://github.com/KaranlikPasa>
pkgname=nyaa-anime-tracker
pkgver=1.0.1
pkgrel=1
pkgdesc="Anime çevirmenleri ve fansub ekipleri için Nyaa.si otomatik bölüm yakalama ve masaüstü bildirim sistemi"
arch=('any')
url="https://github.com/KaranlikPasa/nyaa-anime-tracker"
license=('MIT')
depends=('python' 'python-pillow' 'python-requests' 'tk' 'libnotify')
optdepends=(
    'python-customtkinter: Modern arayüz bileşenleri'
    'python-pystray: Sistem tepsisi (system tray) simgesi'
)
provides=('nyaa-anime-tracker')
conflicts=('nyaa-anime-tracker')

package() {
    install -d "${pkgdir}/opt/nyaa-anime-tracker"
    cp -r "${srcdir}/.."/{config.py,gui.py,main.py,matcher.py,notifier.py,nyaa_client.py,startup.py,tracker.py,tray.py,icon.png,icon.ico,nyaa-anime-tracker,run.sh,nyaa-anime-tracker.desktop,requirements.txt,README.md} "${pkgdir}/opt/nyaa-anime-tracker/" 2>/dev/null || \
    cp -r "${startdir}"/{config.py,gui.py,main.py,matcher.py,notifier.py,nyaa_client.py,startup.py,tracker.py,tray.py,icon.png,icon.ico,nyaa-anime-tracker,run.sh,nyaa-anime-tracker.desktop,requirements.txt,README.md} "${pkgdir}/opt/nyaa-anime-tracker/"
    
    chmod -R 755 "${pkgdir}/opt/nyaa-anime-tracker"
    chmod +x "${pkgdir}/opt/nyaa-anime-tracker/nyaa-anime-tracker"
    chmod +x "${pkgdir}/opt/nyaa-anime-tracker/run.sh"

    # Wrapper executable
    install -d "${pkgdir}/usr/bin"
    ln -sf /opt/nyaa-anime-tracker/nyaa-anime-tracker "${pkgdir}/usr/bin/nyaa-anime-tracker"

    # Desktop entry
    install -Dm644 "${pkgdir}/opt/nyaa-anime-tracker/nyaa-anime-tracker.desktop" "${pkgdir}/usr/share/applications/nyaa-anime-tracker.desktop"

    # Icon
    if [ -f "${pkgdir}/opt/nyaa-anime-tracker/icon.png" ]; then
        install -Dm644 "${pkgdir}/opt/nyaa-anime-tracker/icon.png" \
            "${pkgdir}/usr/share/icons/hicolor/256x256/apps/nyaa-anime-tracker.png"
        install -Dm644 "${pkgdir}/opt/nyaa-anime-tracker/icon.png" \
            "${pkgdir}/usr/share/pixmaps/nyaa-anime-tracker.png"
    fi
}
