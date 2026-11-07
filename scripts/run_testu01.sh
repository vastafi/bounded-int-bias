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
R="results/$ID/testu01"
mkdir -p "$R" build

if [ ! -f "$TU/include/bbattery.h" ]; then
  echo "Installing TestU01 in $TU (once)..."
  rm -rf build/TestU01-src
  git clone -q --depth 1 https://github.com/umontreal-simul/TestU01-2009.git build/TestU01-src
  cd build/TestU01-src
  ./configure --prefix="$TU" --disable-shared > ../testu01-configure.log 2>&1 \
    || ./configure --prefix="$TU" --disable-shared --build="$(uname -m)-apple-darwin" > ../testu01-configure.log 2>&1
  make -j4 > ../testu01-make.log 2>&1
  make install > ../testu01-install.log 2>&1
  cd ../..
fi

cc -O2 -I"$TU/include" src/testu01/convert_battery.c -L"$TU/lib" \
   -ltestu01 -lprobdist -lmylib -lm -o build/convert_battery

for g in raw rejection mult mod; do
  echo "SmallCrush: $g"
  ./build/convert_battery "$g" small > "$R/${g}_smallcrush.txt" 2>&1
done
if [ "$MODE" = "crush" ]; then
  for g in raw rejection mult mod; do
    echo "Crush: $g (takes a while)"
    ./build/convert_battery "$g" crush > "$R/${g}_crush.txt" 2>&1
  done
fi
echo "Done. Results are in $R"
