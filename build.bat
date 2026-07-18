@echo off

setlocal

for /f "tokens=1,* delims==" %%A in (build_config.ini) do (
    if /I "%%A"=="generator" set "GENERATOR=%%B"
)

echo Using Generator: %GENERATOR%

taskkill /F /FI "WINDOWTITLE eq Shard Engine"
timeout /t 1 /nobreak >nul

pushd maths
call build.bat "%GENERATOR%"
if errorlevel 1 exit /b %errorlevel%
popd

pushd collisions\spatial_collision_engine
call build.bat "%GENERATOR%"
if errorlevel 1 exit /b %errorlevel%
popd

pushd rendering
call build.bat "%GENERATOR%"
if errorlevel 1 exit /b %errorlevel%
popd

start "Shard Engine" python main.py
timeout /t 5