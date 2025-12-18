@echo off
echo ========================================
echo   EXPENSE TRACKER - DEPLOY HELPER
echo ========================================
echo.

echo Verificando estado de Git...
git status
echo.

echo ¿Querés commitear y pushear los cambios? (S/N)
set /p choice="> "

if /i "%choice%"=="S" (
    echo.
    echo Ingresá el mensaje de commit:
    set /p commit_msg="> "

    echo.
    echo Agregando archivos...
    git add .

    echo Creando commit...
    git commit -m "%commit_msg%"

    echo Pusheando a GitHub...
    git push

    echo.
    echo ========================================
    echo ✅ Código pusheado a GitHub!
    echo ========================================
    echo.
    echo Próximos pasos:
    echo 1. Andá a https://share.streamlit.io
    echo 2. Click en "New app"
    echo 3. Seleccioná tu repo de GitHub
    echo 4. Main file path: dashboard/streamlit_app.py
    echo 5. Configurá los secrets en Advanced settings
    echo 6. Click en Deploy!
    echo.
    echo Abriendo Streamlit Cloud...
    start https://share.streamlit.io
) else (
    echo.
    echo Deploy cancelado.
)

pause
