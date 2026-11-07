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

# E3: language standard functions and common idioms (each runs only if the language is installed)
NB=1610612736; NN=100000; SEED=2026
if command -v python3 >/dev/null 2>&1; then
  python3 src/languages/python/sample_python.py $NB $NN $SEED "$R/python-sample"
else echo "Python not found: skipped"; fi
if command -v Rscript >/dev/null 2>&1; then
  Rscript src/languages/r/sample_r.R $NB $NN $SEED "$R/r-sample" > /dev/null
  R --version | head -1 > "$R/r-sample/version.txt"
else echo "R not found: skipped"; fi
if command -v java >/dev/null 2>&1; then
  java src/languages/java/SampleJava.java $NB $NN $SEED "$R/java-sample"
else echo "Java not found: skipped"; fi
if command -v node >/dev/null 2>&1; then
  node src/languages/javascript/sample_js.js $NB $NN "$R/js-sample"
else echo "Node.js not found: skipped"; fi
# compress large raw files (analyze_sample.py reads .gz directly)
find "$R" -name '*_N100000_*.txt' -exec gzip -f {} \;

# Environment: JSON if Python is available, plain text otherwise
if command -v python3 >/dev/null 2>&1; then
  python3 scripts/record_env.py "$ID" > /dev/null
else
  { uname -a; "$CXX" --version; } > "$R/environment.txt"
fi
"$CXX" --version > "$R/cpp-uniform/compiler.txt"
echo "Done. Results are in $R"
