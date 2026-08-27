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
timeout /t 2 /nobreak >nul
start "" "http://localhost:5173/"

echo.
echo La aplicacion se ha abierto en el navegador.
echo Para detener el servidor, cierra la ventana de terminal de Vite.
endlocal
