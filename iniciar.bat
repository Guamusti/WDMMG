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
set "API_REUSED="
for /f %%A in ('powershell -NoProfile -Command "$f='public/api-port.json'; if (Test-Path $f) { try { $p=(Get-Content -Raw $f | ConvertFrom-Json).port; $r=Invoke-WebRequest -UseBasicParsing -Uri ('http://127.0.0.1:'+ $p +'/api/health') -TimeoutSec 1; if ($r.StatusCode -eq 200) { $p } } catch {} }"') do set "APIPORT=%%A"
if defined APIPORT set "API_REUSED=1"
if not defined APIPORT for /f %%A in ('powershell -NoProfile -Command "$p=8787; while (Get-NetTCPConnection -LocalPort $p -State Listen -ErrorAction SilentlyContinue) { $p++ }; $p"') do set "APIPORT=%%A"
powershell -NoProfile -Command "$json = @{ port = %APIPORT% } | ConvertTo-Json; Set-Content -LiteralPath 'public/api-port.json' -Value $json -Encoding utf8"
echo API local en http://127.0.0.1:%APIPORT% %API_REUSED%
if not defined API_REUSED powershell -NoProfile -Command "$apiArgs = '/c set ATLAS_API_PORT=%APIPORT%&& npm run api'; Start-Process -FilePath 'cmd.exe' -ArgumentList $apiArgs -WorkingDirectory '%~dp0' -WindowStyle Hidden -RedirectStandardOutput '%~dp0api.log' -RedirectStandardError '%~dp0api-error.log'"

set "FRONTEND_REUSED="
for /f %%P in ('powershell -NoProfile -Command "$f='.atlas-frontend-port'; if (Test-Path $f) { try { $p=(Get-Content -Raw $f).Trim(); $r=Invoke-WebRequest -UseBasicParsing -Uri ('http://127.0.0.1:'+ $p +'/') -TimeoutSec 1; if ($r.StatusCode -eq 200) { $p } } catch {} }"') do set "PORT=%%P"
if defined PORT set "FRONTEND_REUSED=1"
if not defined PORT for /f %%P in ('powershell -NoProfile -Command "$p=5173; while (Get-NetTCPConnection -LocalPort $p -State Listen -ErrorAction SilentlyContinue) { $p++ }; $p"') do set "PORT=%%P"
>".atlas-frontend-port" echo %PORT%
echo Frontend local en http://localhost:%PORT% %FRONTEND_REUSED%
if not defined FRONTEND_REUSED powershell -NoProfile -Command "$viteArgs = '/c npm run dev -- --host=127.0.0.1 --port=%PORT%'; Start-Process -FilePath 'cmd.exe' -ArgumentList $viteArgs -WorkingDirectory '%~dp0' -WindowStyle Hidden -RedirectStandardOutput '%~dp0vite.log' -RedirectStandardError '%~dp0vite-error.log'"

powershell -NoProfile -Command "Start-Sleep -Seconds 4"
start "" "http://localhost:%PORT%"
endlocal
