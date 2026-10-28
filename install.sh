#!/usr/bin/env bash
# ==============================================================================
# Nyaa Anime Takipçisi - Arch Linux & Linux Kurulum Betiği
# ==============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}======================================================${NC}"
echo -e "${CYAN}   📺 Nyaa Anime Takipçisi - Linux Kurulum Sihirbazı  ${NC}"
echo -e "${CYAN}======================================================${NC}"

if [ "$EUID" -ne 0 ]; then
  echo -e "${YELLOW}[Bilgi] Sistem geneline (/opt/nyaa-anime-tracker) kurulum için root yetkisi gereklidir.${NC}"
  echo -e "Yönetici şifreniz istenebilir..."
  exec sudo "$0" "$@"
fi

INSTALL_DIR="/opt/nyaa-anime-tracker"
BIN_LINK="/usr/bin/nyaa-anime-tracker"
DESKTOP_DIR="/usr/share/applications"
ICONS_BASE="/usr/share/icons/hicolor"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo -e "\n${BLUE}1/4: Sistem Bağımlılıkları Kontrol Ediliyor...${NC}"

if command -v pacman >/dev/null 2>&1; then
    echo -e "${GREEN}Arch Linux tespit edildi. pacman ile bağımlılıklar kuruluyor...${NC}"
    pacman -S --noconfirm --needed python python-pillow python-requests tk libnotify
elif command -v apt-get >/dev/null 2>&1; then
    echo -e "${GREEN}Debian/Ubuntu tespit edildi. apt ile bağımlılıklar kuruluyor...${NC}"
    apt-get update && apt-get install -y python3 python3-pil python3-requests python3-tk libnotify-bin
elif command -v dnf >/dev/null 2>&1; then
    echo -e "${GREEN}Fedora tespit edildi. dnf ile bağımlılıklar kuruluyor...${NC}"
    dnf install -y python3 python3-pillow python3-requests python3-tkinter libnotify
fi

echo -e "${BLUE}Python kütüphaneleri kontrol ediliyor (customtkinter, pystray)...${NC}"
pip install --break-system-packages -r "$SCRIPT_DIR/requirements.txt" 2>/dev/null || \
pip install -r "$SCRIPT_DIR/requirements.txt" 2>/dev/null || true

echo -e "\n${BLUE}2/4: Uygulama Dosyaları $INSTALL_DIR Dizinine Kopyalanıyor...${NC}"
mkdir -p "$INSTALL_DIR"
cp -r "$SCRIPT_DIR/config.py" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/gui.py" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/main.py" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/matcher.py" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/notifier.py" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/nyaa_client.py" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/startup.py" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/tracker.py" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/tray.py" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/icon.png" "$INSTALL_DIR/" 2>/dev/null || true
cp -r "$SCRIPT_DIR/icon.ico" "$INSTALL_DIR/" 2>/dev/null || true
cp -r "$SCRIPT_DIR/nyaa-anime-tracker" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/run.sh" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/nyaa-anime-tracker.desktop" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/requirements.txt" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/README.md" "$INSTALL_DIR/" 2>/dev/null || true

chmod -R 755 "$INSTALL_DIR"
chmod +x "$INSTALL_DIR/nyaa-anime-tracker"
chmod +x "$INSTALL_DIR/run.sh"

echo -e "\n${BLUE}3/4: Sistem Başlatıcısı ve Masaüstü Kısayolu Oluşturuluyor...${NC}"
ln -sf "$INSTALL_DIR/nyaa-anime-tracker" "$BIN_LINK"

mkdir -p "$DESKTOP_DIR"
cp "$INSTALL_DIR/nyaa-anime-tracker.desktop" "$DESKTOP_DIR/nyaa-anime-tracker.desktop"
chmod 644 "$DESKTOP_DIR/nyaa-anime-tracker.desktop"

echo -e "\n${BLUE}4/4: Simgeler ve Önbellek Güncelleniyor...${NC}"
if [ -f "$INSTALL_DIR/icon.png" ]; then
    mkdir -p "$ICONS_BASE/256x256/apps"
    cp "$INSTALL_DIR/icon.png" "$ICONS_BASE/256x256/apps/nyaa-anime-tracker.png"
    mkdir -p /usr/share/pixmaps
    cp "$INSTALL_DIR/icon.png" /usr/share/pixmaps/nyaa-anime-tracker.png
fi

if command -v gtk-update-icon-cache >/dev/null 2>&1; then
  gtk-update-icon-cache -f -t "$ICONS_BASE" 2>/dev/null || true
fi
if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
fi

echo -e "\n${GREEN}======================================================${NC}"
echo -e "${GREEN}   ✅ Nyaa Anime Takipçisi Başarıyla Kuruldu!${NC}"
echo -e "${GREEN}======================================================${NC}"
echo -e "Uygulamayı çalıştırmak için:"
echo -e "  - Uygulama menünüzden ${CYAN}Nyaa Anime Takipçisi${NC} seçin"
echo -e "  - Veya terminalde doğrudan ${CYAN}nyaa-anime-tracker${NC} komutunu verin."
echo -e ""
echo -e "Kaldırmak isterseniz: ${YELLOW}sudo rm -rf /opt/nyaa-anime-tracker /usr/bin/nyaa-anime-tracker /usr/share/applications/nyaa-anime-tracker.desktop${NC}\n"
