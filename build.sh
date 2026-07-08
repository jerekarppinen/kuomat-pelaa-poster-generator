#!/usr/bin/env bash
set -euo pipefail

echo "=== Kuomat Pelaa - Linux Build (Mint) ==="
echo

# Siirry skriptin kansioon, jotta suhteelliset polut toimivat
cd "$(dirname "$0")"

# Tarkista python3
if ! command -v python3 >/dev/null 2>&1; then
    echo "VIRHE: python3 ei ole asennettuna."
    echo "Asenna:  sudo apt install python3 python3-pip python3-tk"
    exit 1
fi

# Tarkista tkinter (tarvitaan käyttöliittymään)
if ! python3 -c "import tkinter" >/dev/null 2>&1; then
    echo "VIRHE: tkinter puuttuu."
    echo "Asenna:  sudo apt install python3-tk"
    exit 1
fi

# Tarkista pip ja venv (Mintissä nämä eivät ole aina oletuksena)
if ! python3 -c "import ensurepip" >/dev/null 2>&1 || ! python3 -c "import venv" >/dev/null 2>&1; then
    echo "VIRHE: python3-venv puuttuu."
    echo "Asenna:  sudo apt install python3-venv python3-pip"
    exit 1
fi

# Luo eristetty virtuaaliympäristö buildia varten
VENV=".buildenv"
echo "Luodaan virtuaaliympäristö ($VENV)..."
python3 -m venv "$VENV"
# shellcheck disable=SC1091
source "$VENV/bin/activate"

echo "Asennetaan riippuvuudet (pillow, pyinstaller)..."
pip install --quiet --upgrade pip
pip install --quiet pillow pyinstaller

# Tyhjennä vanhat buildin tulokset, jotta paketti on aina ajan tasalla
echo "Tyhjennetään vanhat buildit (build/ dist/)..."
rm -rf build dist

echo "Rakennetaan suoritettava tiedosto..."
pyinstaller \
    --onefile \
    --windowed \
    --name "KuomaatPelaa" \
    --add-data "kuomat_pelaa_poster.py:." \
    kuomat_pelaa_ui.py

deactivate

echo
echo "Valmis! Suoritettava tiedosto: dist/KuomaatPelaa"
echo "Aja:  ./dist/KuomaatPelaa"
