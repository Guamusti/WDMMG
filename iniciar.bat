@echo off
setlocal
cd /d "%~dp0"

echo Sincronizando la ultima version de GitHub...
git pull --ff-only
if errorlevel 1 (
  echo Aviso: no se pudo sincronizar GitHub. Se continuara con la copia local.
)

if not exist "node_modules" (
  echo Instalando dependencias...
  call npm install
  if errorlevel 1 (
    echo.
    echo No se pudieron instalar las dependencias.
    pause
    exit /b 1
  )
)

if exist "package.json" (
  call npm install --silent
)

echo Iniciando Dinero Publico en http://localhost:5173 ...
start "Dinero Publico - API" cmd /c "npm run api"
start "Dinero Publico - servidor" cmd /c "npm run dev -- --host=127.0.0.1"
echo Esperando a que el frontend este disponible...
set "READY="
for /l %%I in (1,1,20) do (
  powershell -NoProfile -ExecutionPolicy Bypass -Command "try { Invoke-WebRequest -UseBasicParsing -TimeoutSec 1 http://127.0.0.1:5173/ ^| Out-Null; exit 0 } catch { exit 1 }"
  if not errorlevel 1 (
    set "READY=1"
    goto frontend_ready
  )
  timeout /t 1 /nobreak >nul
)

:frontend_ready
if not defined READY echo Aviso: el frontend no respondio aun; se abrira igualmente.
start "" "http://localhost:5173/"

echo.
echo La aplicacion se ha abierto en el navegador.
echo Para detener el servidor, cierra la ventana de terminal de Vite.
endlocal
