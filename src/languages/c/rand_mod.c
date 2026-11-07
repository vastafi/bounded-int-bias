/* The hand-written idiom rand() % n with the platform's C library.
 * RAND_MAX differs by platform (glibc: 2^31-1, macOS: 2^31-1, MSVC/MinGW: 32767), so the bias differs too.
 * Build: cc -O2 rand_mod.c -o rand_mod      Run: ./rand_mod <n> <N> <seed> > out.txt
 * Analyse with --method mod --w <bits of RAND_MAX+1> (31 on glibc/macOS, 15 on Windows). */
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv) {
    if (argc < 4) { fprintf(stderr, "usage: rand_mod n N seed\n"); return 1; }
    unsigned long n = strtoul(argv[1], NULL, 10);
    unsigned long N = strtoul(argv[2], NULL, 10);
    srand((unsigned)strtoul(argv[3], NULL, 10));
    for (unsigned long i = 0; i < N; ++i) printf("%lu\n", (unsigned long)rand() % n);
    fprintf(stderr, "RAND_MAX=%d\n", RAND_MAX);
    return 0;
}
