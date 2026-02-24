@echo off
echo ============================================
echo   Image to PDF Pro Bot - Railway Setup
echo ============================================
echo.

REM Railway CLI orqali sozlash
REM Bu skriptni bir marta ishga tushiring

echo [1/4] Railway ga login bo'lish...
echo Brauzer ochiladi - Railway akkauntingizga kiring
railway login
if %errorlevel% neq 0 (
    echo ERROR: Railway login muvaffaqiyatsiz
    pause
    exit /b 1
)

echo.
echo [2/4] Loyiha bilan bog'lanish...
echo Ro'yxatdan loyihangizni tanlang
railway link
if %errorlevel% neq 0 (
    echo ERROR: Loyiha bog'lanmadi
    pause
    exit /b 1
)

echo.
echo [3/4] Environment variables sozlanmoqda...
railway variables set BOT_TOKEN=8653145011:AAGsTosm1Y_TB84N5_5Dpx0gl3Le3RdVeaY
railway variables set ADMIN_IDS=7091543940
railway variables set LOG_LEVEL=INFO
railway variables set MAX_FILE_SIZE=20971520
railway variables set MAX_IMAGES_PER_SESSION=50
railway variables set HISTORY_DAYS=7

echo.
echo [4/4] Bot qayta ishga tushirilmoqda...
railway redeploy

echo.
echo ============================================
echo   MUVAFFAQIYAT! Bot Railway da ishlamoqda
echo ============================================
echo.
echo Botni tekshiring: @PDF_BOT_USERNAME
echo Railway dashboard: https://railway.app
echo.
pause
