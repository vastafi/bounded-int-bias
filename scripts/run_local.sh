#!/bin/sh
# Run the C and C++ experiments on Linux or macOS with the standard folder layout.
# Usage (from the repository root):  sh scripts/run_local.sh <source-id>
#   e.g. sh scripts/run_local.sh mac-va
set -e
ID="${1:?usage: sh scripts/run_local.sh <source-id>}"
R="results/$ID"
mkdir -p "$R/cpp-uniform" "$R/c-randmod" build

CXX="${CXX:-c++}"; CC="${CC:-cc}"
"$CXX" -O2 -std=c++17 src/languages/cpp/uniform_int.cpp -o build/uniform_int
"$CC"  -O2 src/languages/c/rand_mod.c -o build/rand_mod

# E4: same seed, same engine, different C++ standard library
./build/uniform_int 1000 20 2026 > "$R/cpp-uniform/cpp_uniform_n1000_N20_seed2026.txt" 2> "$R/cpp-uniform/library.txt"

# E3: rand() % n with the platform's C library
for n in 20000 1610612736; do
  ./build/rand_mod "$n" 100000 2026 > "$R/c-randmod/c_randmod_n${n}_N100000_seed2026.txt" 2> "$R/c-randmod/rand_max.txt"
done

# Environment: JSON if Python is available, plain text otherwise
if command -v python3 >/dev/null 2>&1; then
  python3 scripts/record_env.py "$ID" > /dev/null
else
  { uname -a; "$CXX" --version; } > "$R/environment.txt"
fi
"$CXX" --version > "$R/cpp-uniform/compiler.txt"
echo "Gata. Rezultatele sunt in $R"
