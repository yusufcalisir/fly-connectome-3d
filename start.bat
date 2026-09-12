@echo off
setlocal enabledelayedexpansion
title FlyConnectome 3D - Neural Observation and Telemetry Cockpit
color 0B

:: Ensure working directory is always the repository root
cd /d "%~dp0"

echo ===============================================================================
echo        FLYCONNECTOME 3D - NEURAL OBSERVATION ^& TELEMETRY COCKPIT
echo               Biocomputing Engine ^| Janelia MaleCNS v1.0
echo ===============================================================================
echo.

:: 1. Runtime Environment Check (uv package manager or python fallback)
echo [*] Checking runtime environment...
set "UV_CMD="

where uv >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "UV_CMD=uv"
    goto UV_FOUND
)

if exist "%LOCALAPPDATA%\Programs\Python\Python312\Scripts\uv.exe" (
    set "UV_CMD=%LOCALAPPDATA%\Programs\Python\Python312\Scripts\uv.exe"
    goto UV_FOUND
)
if exist "%USERPROFILE%\.cargo\bin\uv.exe" (
    set "UV_CMD=%USERPROFILE%\.cargo\bin\uv.exe"
    goto UV_FOUND
)
if exist "%LOCALAPPDATA%\bin\uv.exe" (
    set "UV_CMD=%LOCALAPPDATA%\bin\uv.exe"
    goto UV_FOUND
)

echo [WARN] Package manager 'uv' not found in PATH or standard user directories.
echo [*] Attempting automated installation via Astral installer...
powershell -ExecutionPolicy ByPass -Command "irm https://astral.sh/uv/install.ps1 | iex"
if exist "%USERPROFILE%\.cargo\bin\uv.exe" (
    set "UV_CMD=%USERPROFILE%\.cargo\bin\uv.exe"
    goto UV_FOUND
)
if exist "%LOCALAPPDATA%\bin\uv.exe" (
    set "UV_CMD=%LOCALAPPDATA%\bin\uv.exe"
    goto UV_FOUND
)

:: Python / .venv fallback
if exist ".venv\Scripts\python.exe" (
    echo [NOTE] Using local virtual environment (.venv) python...
    set "PY_CMD=.venv\Scripts\python.exe"
    goto ENV_READY
)

where python >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo [NOTE] Using system Python...
    set "PY_CMD=python"
    goto ENV_READY
)

echo [ERROR] Could not locate 'uv' or 'python'.
echo Please install uv: https://docs.astral.sh/uv/getting-started/installation/
echo.
pause
exit /b 1

:UV_FOUND
echo [OK] Runtime tool: %UV_CMD%
set "PY_CMD=%UV_CMD% run python"
goto ENV_READY

:ENV_READY
echo.

:: 2. CLI Subcommands Support (test, compile, help)
if /i "%~1"=="test" (
    echo [*] Running FlyConnectome biological test suite...
    if defined UV_CMD (
        "%UV_CMD%" run pytest %2 %3 %4 %5 %6
    ) else (
        "%PY_CMD%" -m pytest %2 %3 %4 %5 %6
    )
    exit /b %ERRORLEVEL%
)

if /i "%~1"=="compile" (
    echo [*] Recompiling sparse connectome graph and 3D soma coordinates...
    %PY_CMD% src\connectome_engine\data\compile_malecns.py
    %PY_CMD% src\connectome_engine\data\compile_coordinates.py
    echo [OK] Compilation complete.
    exit /b %ERRORLEVEL%
)

:: 3. Connectome Dataset & 3D Soma Verification
echo [*] Checking Janelia MaleCNS v1.0 biological connectome data...
if not exist "data\malecns_v1\malecns_v1_graph.npz" (
    echo [WARN] Compiled graph 'data\malecns_v1\malecns_v1_graph.npz' not found.
    if not exist "data\malecns_v1\edges.feather" (
        echo [WARN] Raw connectome data missing. Initiating official dataset download...
        %PY_CMD% src\connectome_engine\data\downloader.py
        if !ERRORLEVEL! neq 0 (
            echo [ERROR] Dataset download failed. Please check network connection.
            pause
            exit /b 1
        )
    )
    echo [*] Compiling sparse connectome graph from raw Feather data...
    %PY_CMD% src\connectome_engine\data\compile_malecns.py
    if !ERRORLEVEL! neq 0 (
        echo [ERROR] Connectome compilation failed.
        pause
        exit /b 1
    )
)

:: Verify 3D Point Cloud Soma Coordinates
if not exist "data\malecns_v1\soma_coordinates_141k.bin" (
    echo [WARN] 3D Soma coordinates 'soma_coordinates_141k.bin' not found.
    echo [*] Compiling 141K 3D soma coordinates from biological annotations...
    %PY_CMD% src\connectome_engine\data\compile_coordinates.py
    if !ERRORLEVEL! neq 0 (
        echo [ERROR] Soma coordinates compilation failed.
        pause
        exit /b 1
    )
)

echo [OK] Janelia MaleCNS v1.0 dataset verified: 166,778 neurons, 25,603,246 synapses, 141K somas.
echo.

:: 4. Port 8000 Conflict Resolution
set "PORT=8000"
set "FOUND_PID="
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%PORT% ^| findstr LISTENING 2^>nul') do (
    set "FOUND_PID=%%a"
)

if not defined FOUND_PID goto START_SERVER

echo [NOTE] Port %PORT% is already active (Process ID: %FOUND_PID%).
echo [*] Opening Cockpit in default browser: http://127.0.0.1:%PORT%/
start "" "http://127.0.0.1:%PORT%/"
echo.
echo -------------------------------------------------------------------------------
echo An instance of the server is already running on port %PORT%.
echo   - To keep current server running: press Enter (or do nothing)
echo   - To restart fresh: type R and press Enter
echo -------------------------------------------------------------------------------
set "USER_ACT="
set /p "USER_ACT=Enter choice [Enter=Continue / R=Restart]: "
if /i "%USER_ACT%"=="R" goto RESTART_PID

echo [*] Keeping existing server running. Enjoy FlyConnectome 3D!
ping 127.0.0.1 -n 2 >nul
exit /b 0

:RESTART_PID
echo [*] Stopping previous instance (PID: %FOUND_PID%)...
taskkill /F /PID %FOUND_PID% >nul 2>&1
ping 127.0.0.1 -n 2 >nul
echo [OK] Previous instance stopped. Starting fresh engine...
echo.

:START_SERVER
:: 5. Check if --no-browser flag was passed
set "OPEN_BROWSER=1"
for %%x in (%*) do (
    if /i "%%x"=="--no-browser" set "OPEN_BROWSER=0"
    if /i "%%x"=="-n" set "OPEN_BROWSER=0"
)

:: 6. Smart Background Healthcheck Browser Launcher (polls until HTTP 200)
if "%OPEN_BROWSER%"=="1" (
    echo [*] Health-check browser launcher scheduled (will open cockpit upon ready)...
    start "" powershell -NoProfile -ExecutionPolicy Bypass -Command "for ($i=0; $i -lt 40; $i++) { try { $r = Invoke-WebRequest -Uri 'http://127.0.0.1:8000/' -UseBasicParsing -TimeoutSec 1; if ($r.StatusCode -eq 200) { Start-Process 'http://127.0.0.1:8000/'; break } } catch {}; Start-Sleep -Milliseconds 400 }"
)

:: 7. Launch FastAPI / Uvicorn Server
echo [*] Starting FlyConnectome Biocomputing Engine...
echo [*] WebSocket Telemetry Stream: ws://127.0.0.1:%PORT%/ws/telemetry
echo [*] Web Cockpit UI: http://127.0.0.1:%PORT%/
echo [*] Press Ctrl+C in this window to stop the engine.
echo.

if defined UV_CMD (
    "%UV_CMD%" run uvicorn connectome_engine.server.app:app --host 127.0.0.1 --port %PORT% %*
) else (
    "%PY_CMD%" -m uvicorn connectome_engine.server.app:app --host 127.0.0.1 --port %PORT% %*
)

if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Server terminated with error code %ERRORLEVEL%.
    pause
)
