taskkill /F /FI "WINDOWTITLE eq Shard Engine"
timeout /t 1 /nobreak >nul
pushd collisions\spatial_collision_engine
cmake -S . -B build -G "Visual Studio 18 2026"
cmake --build build
pip install -e .
popd
start "Shard Engine" python main.py
timeout /t 5