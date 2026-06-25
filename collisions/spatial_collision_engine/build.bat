cmake -S . -B build -G "Visual Studio 18 2026"
cmake --build build
pip install -e .
timeout /t 10