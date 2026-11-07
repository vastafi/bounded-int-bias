#!/bin/sh
# E7: run TestU01 batteries on the raw generator and on three bounded-integer conversions.
# Usage (from the repository root):
#   sh scripts/run_testu01.sh <source-id>            # SmallCrush only (about 1 minute in total)
#   sh scripts/run_testu01.sh <source-id> crush      # SmallCrush + Crush (several hours; run overnight)
# TestU01 is downloaded from github.com/umontreal-simul/TestU01-2009 and installed in ~/testu01 (once).
set -e
ID="${1:?usage: sh scripts/run_testu01.sh <source-id> [crush]}"
MODE="${2:-small}"
TU="$HOME/testu01"
# TestU01 (2009) uses pre-C99 constructs that recent compilers reject by default
export CFLAGS="${CFLAGS:--O2 -Wno-implicit-function-declaration -Wno-implicit-int -Wno-int-conversion}"
R="results/$ID/testu01"
mkdir -p "$R" build

if [ ! -f "$TU/include/bbattery.h" ]; then
  echo "Installing TestU01 in $TU (once)..."
  rm -rf build/TestU01-src
  git clone -q --depth 1 https://github.com/umontreal-simul/TestU01-2009.git build/TestU01-src
  cd build/TestU01-src
  # helper scripts lose their executable bit in the git copy (install-sh: Permission denied)
  chmod +x configure install-sh config.guess config.sub depcomp missing ltmain.sh 2>/dev/null || true
  ./configure --prefix="$TU" --disable-shared > ../testu01-configure.log 2>&1 \
    || ./configure --prefix="$TU" --disable-shared --build="$(uname -m)-apple-darwin" > ../testu01-configure.log 2>&1 \
    || { echo "TestU01 configure failed; see build/testu01-configure.log"; exit 1; }
  make -j4 > ../testu01-make.log 2>&1 || { echo "TestU01 build failed; see build/testu01-make.log"; exit 1; }
  make install > ../testu01-install.log 2>&1 || { echo "TestU01 install failed; see build/testu01-install.log"; exit 1; }
  cd ../..
fi

cc -O2 -I"$TU/include" src/testu01/convert_battery.c -L"$TU/lib" \
   -ltestu01 -lprobdist -lmylib -lm -o build/convert_battery 2> build/convert_battery-compile.log \
  || { echo "Compiling convert_battery failed:"; cat build/convert_battery-compile.log; exit 1; }
echo "TestU01 ready; running SmallCrush (about 1 minute per generator)"

for g in raw rejection mult mod rejection_d mult_d mod_d mult53_d mod53_d; do
  echo "SmallCrush: $g"
  ./build/convert_battery "$g" small > "$R/${g}_smallcrush.txt" 2>&1
done
if [ "$MODE" = "crush" ]; then
  for g in raw rejection mult mod rejection_d mult_d mod_d mult53_d mod53_d; do
    echo "Crush: $g (takes a while)"
    ./build/convert_battery "$g" crush > "$R/${g}_crush.txt" 2>&1
  done
fi
echo "Done. Results are in $R"
