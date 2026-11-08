#!/bin/sh
# M7: SmallCrush on the dithered generators with several seeds (about 2 minutes per seed).
# Usage (repository root, after scripts/run_testu01.sh has built build/convert_battery once):
#   sh scripts/run_testu01_seeds.sh <source-id> [seeds...]      default seeds: 1 2 3 4 5
set -e
ID="${1:?usage: sh scripts/run_testu01_seeds.sh <source-id> [seeds...]}"; shift
SEEDS="${*:-1 2 3 4 5}"
S=build/TestU01-src
TU="$HOME/testu01"
if [ -f "$TU/include/bbattery.h" ]; then
  cc -O2 -I"$TU/include" src/testu01/convert_battery.c -L"$TU/lib" -ltestu01 -lprobdist -lmylib -lm -o build/convert_battery
else
  cc -O2 -I$S/include -I$S/testu01 -I$S/probdist -I$S/mylib src/testu01/convert_battery.c \
     $S/testu01/.libs/libtestu01.a $S/probdist/.libs/libprobdist.a $S/mylib/.libs/libmylib.a -lm -o build/convert_battery
fi
R="results/$ID/testu01/seeds"
mkdir -p "$R"
for s in $SEEDS; do
  for g in raw rejection_d mult_d mod_d mult53_d mod53_d; do
    echo "seed $s: SmallCrush $g"
    ./build/convert_battery "$g" small "$s" > "$R/${g}_seed${s}_smallcrush.txt" 2>&1
  done
done
echo "Done. Results are in $R"
