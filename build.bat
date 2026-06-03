@echo off
echo === Kuomat Pelaa - EXE Build ===
echo.

echo Asennetaan PyInstaller...
pip install pyinstaller --quiet
if errorlevel 1 (
    echo VIRHE: pip ei toimi. Varmista etta Python on asennettu.
    pause
    exit /b 1
)

echo Rakennetaan .exe...
pyinstaller ^
    --onefile ^
    --windowed ^
    --name "KuomaatPelaa" ^
    --add-data "kuomat_pelaa_poster.py;." ^
    kuomat_pelaa_ui.py

if errorlevel 1 (
    echo.
    echo VIRHE: Build epaonnistui.
    pause
    exit /b 1
)

echo.
echo Valmis! Loydat tiedoston: dist\KuomaatPelaa.exe
echo.
pause
