cmake -S . -B build -G %*
cmake --build build --config Release
timeout /t 5