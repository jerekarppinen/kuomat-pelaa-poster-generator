# Kuomat Pelaa – Posterigeneraattori

Luo 1080×1350 some/podcast-kansikuvia kahdesta kuvasta ja jakson kuvaustekstistä.

## Vaatimukset

```
pip install pillow
```

## Käyttö – UI

```
python kuomat_pelaa_ui.py
```

Avaa graafisen käyttöliittymän: valitse yläkuva, alakuva, kirjoita jakson kuvaus ja paina *Luo posteri*. Kuva tallentuu `jakso.png`-nimellä samaan kansioon.

## Käyttö – komentorivi

```
python kuomat_pelaa_poster.py kuva1.jpg kuva2.jpg --body "Jakson kuvaus tähän." -o jakso.png
```

---

## Buildaus suoritettavaksi tiedostoksi

Valmis ohjelma ei vaadi Pythonia käyttäjän koneella. Buildi tehdään aina sillä käyttöjärjestelmällä jolle se on tarkoitettu — Windows-koneella ei voi buildata Mac-versiota.

### Windows

Asenna ensin Python 3.x [python.org](https://python.org) -sivulta (valitse "Add to PATH").

```bat
build.bat
```

Valmis tiedosto: `dist\KuomaatPelaa.exe`

### macOS

```bash
pip3 install pillow pyinstaller
pyinstaller --onefile --windowed --name "KuomaatPelaa" \
    --add-data "kuomat_pelaa_poster.py:." \
    kuomat_pelaa_ui.py
```

Valmis tiedosto: `dist/KuomaatPelaa`

> **Huom:** macOS saattaa estää tuntemattoman sovelluksen avaamisen. Salli se kohdasta *Järjestelmäasetukset → Yksityisyys ja turvallisuus → Avaa silti*.

### Linux

Tkinter ei välttämättä ole asennettuna oletuksena:

```bash
# Debian/Ubuntu
sudo apt install python3-tk

# Fedora
sudo dnf install python3-tkinter
```

Sitten:

```bash
pip3 install pillow pyinstaller
pyinstaller --onefile --windowed --name "KuomaatPelaa" \
    --add-data "kuomat_pelaa_poster.py:." \
    kuomat_pelaa_ui.py
```

Valmis tiedosto: `dist/KuomaatPelaa`
