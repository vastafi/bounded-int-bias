/* E7: does a standard battery (TestU01) detect the bias introduced by bounded-integer conversion?
 *
 * Four generators, all built on the same MT19937 stream (seed 2026), all returning u = y / n in [0,1):
 *   raw       : u = k / 2^32                      (control: the generator itself)
 *   rejection : y = unbiased (rejection) in [0,n) (control: correct conversion, same discretisation)
 *   mult      : y = floor(n * k / 2^32)           (R <= 3.5 sample(), INT(RAND()*n))
 *   mod       : y = k mod n                       (rand() % n with a 32-bit source)
 * n = 1.5 * 2^30 (worst-case region; heavy-value test needs ~251 samples for mult).
 *
 * Build (after installing TestU01 in $TU):
 *   cc -O2 -I$TU/include convert_battery.c -L$TU/lib -ltestu01 -lprobdist -lmylib -lm -o convert_battery
 * Run:  ./convert_battery <raw|rejection|mult|mod> <small|crush>
 * Self-check of the MT19937 code without TestU01:  cc -O2 -DSELFTEST convert_battery.c -o selftest && ./selftest
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* ---- MT19937 (Matsumoto & Nishimura 1998), 32-bit output, init_genrand seeding ---- */
static uint32_t mt[624];
static int mti = 625;

static void mt_seed(uint32_t s) {
    mt[0] = s;
    for (mti = 1; mti < 624; mti++)
        mt[mti] = 1812433253u * (mt[mti - 1] ^ (mt[mti - 1] >> 30)) + (uint32_t)mti;
}

static uint32_t mt_next(void) {
    static const uint32_t mag01[2] = {0u, 0x9908b0dfu};
    uint32_t y;
    if (mti >= 624) {
        int kk;
        for (kk = 0; kk < 624 - 397; kk++) {
            y = (mt[kk] & 0x80000000u) | (mt[kk + 1] & 0x7fffffffu);
            mt[kk] = mt[kk + 397] ^ (y >> 1) ^ mag01[y & 1u];
        }
        for (; kk < 623; kk++) {
            y = (mt[kk] & 0x80000000u) | (mt[kk + 1] & 0x7fffffffu);
            mt[kk] = mt[kk + (397 - 624)] ^ (y >> 1) ^ mag01[y & 1u];
        }
        y = (mt[623] & 0x80000000u) | (mt[0] & 0x7fffffffu);
        mt[623] = mt[396] ^ (y >> 1) ^ mag01[y & 1u];
        mti = 0;
    }
    y = mt[mti++];
    y ^= (y >> 11);
    y ^= (y << 7) & 0x9d2c5680u;
    y ^= (y << 15) & 0xefc60000u;
    y ^= (y >> 18);
    return y;
}

/* ---- conversions ---- */
static const uint64_t N_RANGE = 1610612736u; /* 1.5 * 2^30 */

static double gen_raw(void) { return mt_next() / 4294967296.0; }

static double gen_rejection(void) {
    const uint64_t W = 4294967296u, limit = W - (W % N_RANGE);
    uint64_t k;
    do { k = mt_next(); } while (k >= limit);
    return (double)(k % N_RANGE) / (double)N_RANGE;
}

static double gen_mult(void) {
    uint64_t y = ((uint64_t)mt_next() * N_RANGE) >> 32;
    return (double)y / (double)N_RANGE;
}

static double gen_mod(void) {
    uint64_t y = (uint64_t)mt_next() % N_RANGE;
    return (double)y / (double)N_RANGE;
}

#ifdef SELFTEST
int main(void) {
    mt_seed(5489u);
    printf("MT19937 seed 5489, first output: %u (expected 3499211612)\n", mt_next());
    mt_seed(2026u);
    for (int i = 0; i < 5; i++) printf("%u ", mt_next());
    printf("\n");
    return 0;
}
#else
#include "unif01.h"
#include "bbattery.h"

int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr, "usage: convert_battery <raw|rejection|mult|mod> <small|crush>\n"); return 1; }
    double (*f)(void) = NULL;
    if (!strcmp(argv[1], "raw")) f = gen_raw;
    else if (!strcmp(argv[1], "rejection")) f = gen_rejection;
    else if (!strcmp(argv[1], "mult")) f = gen_mult;
    else if (!strcmp(argv[1], "mod")) f = gen_mod;
    if (!f) { fprintf(stderr, "unknown generator %s\n", argv[1]); return 1; }
    mt_seed(2026u);
    unif01_Gen *g = unif01_CreateExternGen01(argv[1], f);
    if (!strcmp(argv[2], "crush")) bbattery_Crush(g); else bbattery_SmallCrush(g);
    unif01_DeleteExternGen01(g);
    return 0;
}
#endif
