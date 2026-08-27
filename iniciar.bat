@echo off
setlocal
cd /d "%~dp0"

echo ========================================
echo   ATLAS UNIVERSITARIO - INICIO LOCAL
echo ========================================
echo.
echo Actualizando dependencias del proyecto...
call npm install
if errorlevel 1 (
  echo.
  echo No se pudieron instalar las dependencias.
  pause
  exit /b 1
)

echo.
for /f %%A in ('powershell -NoProfile -Command "$p=8787; while (Get-NetTCPConnection -LocalPort $p -State Listen -ErrorAction SilentlyContinue) { $p++ }; $p"') do set "APIPORT=%%A"
echo Iniciando API local en http://127.0.0.1:%APIPORT%
start "Atlas Universitario - API" /D "%~dp0" cmd /c "set ATLAS_API_PORT=%APIPORT%&& npm run api"

for /f %%P in ('powershell -NoProfile -Command "$p=5173; while (Get-NetTCPConnection -LocalPort $p -State Listen -ErrorAction SilentlyContinue) { $p++ }; $p"') do set "PORT=%%P"
echo Iniciando la ultima version en http://localhost:%PORT%
start "Atlas Universitario - servidor" /D "%~dp0" npm run dev -- --host=127.0.0.1 --port=%PORT%

timeout /t 4 /nobreak >nul
start "" "http://localhost:%PORT%"
endlocal
