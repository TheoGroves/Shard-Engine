taskkill /F /FI "WINDOWTITLE eq Shard Engine"
timeout /t 1 /nobreak >nul

pushd maths
call build.bat
if errorlevel 1 exit /b %errorlevel%
popd

pushd collisions\spatial_collision_engine
call build.bat
if errorlevel 1 exit /b %errorlevel%
popd

pushd rendering
call build.bat
if errorlevel 1 exit /b %errorlevel%
popd

start "Shard Engine" python main.py
timeout /t 5