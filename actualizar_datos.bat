@echo off
setlocal
cd /d "%~dp0"
echo Ejecutando los loaders de los datos disponibles...
python -m etl.run_available
if errorlevel 1 (
  echo Se produjo un error en una actualizacion. Revisa el resultado anterior.
  pause
  exit /b 1
)
echo Actualizacion terminada.
endlocal
