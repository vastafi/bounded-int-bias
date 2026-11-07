@echo off
rem Run the C and C++ experiments on Windows (MinGW g++/gcc, e.g. the one bundled with CLion).
rem Usage (from the repository root):  scripts\run_local.bat windows-va
if "%~1"=="" (echo usage: scripts\run_local.bat ^<source-id^> & exit /b 1)
set ID=%~1
set R=results\%ID%
if not exist "%R%\cpp-uniform" mkdir "%R%\cpp-uniform"
if not exist "%R%\c-randmod" mkdir "%R%\c-randmod"
if not exist build mkdir build

g++ -O2 -std=c++17 src\languages\cpp\uniform_int.cpp -o build\uniform_int.exe || exit /b 1
gcc -O2 src\languages\c\rand_mod.c -o build\rand_mod.exe || exit /b 1

rem E4: same seed, same engine, different C++ standard library
build\uniform_int.exe 1000 20 2026 > "%R%\cpp-uniform\cpp_uniform_n1000_N20_seed2026.txt" 2> "%R%\cpp-uniform\library.txt"

rem E3: rand() %% n with the platform's C library (RAND_MAX may be 32767 here)
for %%n in (20000 1610612736) do (
  build\rand_mod.exe %%n 100000 2026 > "%R%\c-randmod\c_randmod_n%%n_N100000_seed2026.txt" 2> "%R%\c-randmod\rand_max.txt"
)

rem Environment: JSON if Python is available, plain text otherwise
where python >nul 2>nul && (python scripts\record_env.py %ID% >nul) || (ver > "%R%\environment.txt" & g++ --version >> "%R%\environment.txt")
g++ --version > "%R%\cpp-uniform\compiler.txt"
echo Gata. Rezultatele sunt in %R%
