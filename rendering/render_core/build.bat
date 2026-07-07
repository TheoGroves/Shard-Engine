cmake -S . -B build -G "Visual Studio 18 2026"
cmake --build build --config Release
timeout /t 5