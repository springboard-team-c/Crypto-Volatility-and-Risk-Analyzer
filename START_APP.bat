@echo off
TITLE Crypto Risk Analyzer - Auto Launcher
COLOR 0A

echo ======================================================
echo       CRYPTO VOLATILITY AND RISK ANALYZER
echo                 BATCH 11 TEAM C
echo ======================================================

:: 1. Run the High-Speed Data Seeder
echo.
echo [1/3] Fetching Live Market Data (Instant Mode)...
python fast_seed.py

:: 2. Start the Backend Server (Hidden in Background)
echo.
echo [2/3] Starting Backend Server...
start /B python app.py
:: Wait 2 seconds for the server to wake up
timeout /t 2 /nobreak >nul

:: 3. Launch the Dashboard
echo.
echo [3/3] Launching Dashboard UI...
streamlit run dashboard.py

pause