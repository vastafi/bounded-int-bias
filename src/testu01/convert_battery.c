/* E7: does a standard battery (TestU01) detect the bias introduced by bounded-integer conversion?
 *
 * Nine generators on the same MT19937 stream (seed 2026); the first four return u = y / n in [0,1):
 *   raw       : u = k / 2^32                      (control: the generator itself)
 *   rejection : y = unbiased (rejection) in [0,n) (control: correct conversion, same discretisation)
 *   mult      : y = floor(n * k / 2^32)           (R <= 3.5 sample(), INT(RAND()*n))
 *   mod       : y = k mod n                       (rand() % n with a 32-bit source)
 * n = 1.5 * 2^30 (worst-case region; heavy-value test needs ~251 samples for mult).
 *
 * Dithered variants (suffix _d): u = (y + V) / n with V = k' / 2^32 from the next MT19937 output.
 * If y is uniform on {0..n-1}, u is uniform on [0,1) at 32-bit resolution, so the battery sees only the bias
 * of y, not the coarse lattice of y / n (which has ~30.6 bits and fails bit-level tests even for rejection).
 *
 * 53-bit variants (w = 53, as Python random() / Java nextDouble()): k53 = (a*2^26 + b) with a = k1>>5, b = k2>>6
 *   mult53_d : y = floor(n * k53 / 2^53), dithered     mod53_d : y = k53 mod n, dithered
 *   The bias exists but N* ~ 1.1e15 samples, far beyond SmallCrush/Crush: both are expected to pass.
 *
 * Build (after installing TestU01 in $TU):
 *   cc -O2 -I$TU/include convert_battery.c -L$TU/lib -ltestu01 -lprobdist -lmylib -lm -o convert_battery
 * Run:  ./convert_battery <raw|rejection|mult|mod|rejection_d|mult_d|mod_d|mult53_d|mod53_d> <small|crush>
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

static uint64_t (*int_conv)(void);
static uint64_t y_rejection(void) {
    const uint64_t W = 4294967296u, limit = W - (W % N_RANGE);
    uint64_t k;
    do { k = mt_next(); } while (k >= limit);
    return k % N_RANGE;
}
static uint64_t y_mult(void) { return ((uint64_t)mt_next() * N_RANGE) >> 32; }
static uint64_t y_mod(void) { return (uint64_t)mt_next() % N_RANGE; }
static uint64_t k53(void) {
    uint64_t a = mt_next() >> 5, b = mt_next() >> 6;
    return (a << 26) | b;                                 /* uniform on [0, 2^53) */
}
static uint64_t y_mult53(void) {                          /* floor(n * k53 / 2^53) without overflow */
    unsigned __int128 p = (unsigned __int128)k53() * N_RANGE;
    return (uint64_t)(p >> 53);
}
static uint64_t y_mod53(void) { return k53() % N_RANGE; }
static double gen_dithered(void) {
    uint64_t y = int_conv();
    return ((double)y + mt_next() / 4294967296.0) / (double)N_RANGE;
}

#ifdef SELFTEST
int main(void) {
    mt_seed(5489u);
    printf("MT19937 seed 5489, first output: %u (expected 3499211612)\n", mt_next());
    mt_seed(2026u);
    for (int i = 0; i < 5; i++) printf("%u ", mt_next());
    printf("\n");
    /* dithered rejection: mean and fraction below 1/3 over 10^7 draws (expect 0.5 and 0.3333) */
    int_conv = y_rejection; mt_seed(2026u);
    double s1 = 0; long lo = 0;
    for (long i = 0; i < 10000000; i++) { double u = gen_dithered(); s1 += u; lo += u < 1.0 / 3; if (u < 0 || u >= 1) return 2; }
    printf("dithered rejection: mean %.5f, P(u<1/3) %.5f\n", s1 / 1e7, lo / 1e7);
    /* k53 must equal Python's random() * 2^53 for the same MT stream (seed 2026 via init_genrand) */
    mt_seed(2026u);
    printf("first k53 / 2^53 = %.17f\n", k53() / 9007199254740992.0);
    int_conv = y_mult53; mt_seed(2026u);
    printf("first mult53 y = %llu\n", (unsigned long long)y_mult53());
    return 0;
}
#else
#include "unif01.h"
#include "bbattery.h"

int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr, "usage: convert_battery <raw|rejection|mult|mod|rejection_d|mult_d|mod_d|mult53_d|mod53_d> <small|crush>\n"); return 1; }
    double (*f)(void) = NULL;
    if (!strcmp(argv[1], "raw")) f = gen_raw;
    else if (!strcmp(argv[1], "rejection")) f = gen_rejection;
    else if (!strcmp(argv[1], "mult")) f = gen_mult;
    else if (!strcmp(argv[1], "mod")) f = gen_mod;
    else if (!strcmp(argv[1], "rejection_d")) { int_conv = y_rejection; f = gen_dithered; }
    else if (!strcmp(argv[1], "mult_d")) { int_conv = y_mult; f = gen_dithered; }
    else if (!strcmp(argv[1], "mod_d")) { int_conv = y_mod; f = gen_dithered; }
    else if (!strcmp(argv[1], "mult53_d")) { int_conv = y_mult53; f = gen_dithered; }
    else if (!strcmp(argv[1], "mod53_d")) { int_conv = y_mod53; f = gen_dithered; }
    if (!f) { fprintf(stderr, "unknown generator %s\n", argv[1]); return 1; }
    mt_seed(2026u);
    unif01_Gen *g = unif01_CreateExternGen01(argv[1], f);
    if (!strcmp(argv[2], "crush")) bbattery_Crush(g); else bbattery_SmallCrush(g);
    unif01_DeleteExternGen01(g);
    return 0;
}
#endif
