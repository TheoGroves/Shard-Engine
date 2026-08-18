@echo off

setlocal

for /f "tokens=1,* delims==" %%A in (build_config.ini) do (
    if /I "%%A"=="generator" set "GENERATOR=%%B"
)

echo Using Generator: %GENERATOR%

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

pushd audio
call build.bat "%GENERATOR%"
if errorlevel 1 exit /b %errorlevel%
popd

timeout /t 5