// Same seed, same engine (mt19937), std::uniform_int_distribution on different C++ standard libraries.
// The engine output is fixed by the standard; the distribution algorithm is not.
// Build:  g++ -O2 -std=c++17 uniform_int.cpp -o uniform_int      (Linux/MinGW: libstdc++)
//         clang++ -O2 -std=c++17 uniform_int.cpp -o uniform_int  (macOS: libc++)
// Run:    ./uniform_int <n> <N> <seed> > out.txt
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <random>

int main(int argc, char** argv) {
    if (argc < 4) { std::cerr << "usage: uniform_int n N seed\n"; return 1; }
    const std::uint64_t n = std::strtoull(argv[1], nullptr, 10);
    const std::uint64_t N = std::strtoull(argv[2], nullptr, 10);
    const std::uint32_t seed = static_cast<std::uint32_t>(std::strtoul(argv[3], nullptr, 10));
    std::mt19937 eng(seed);
    std::uniform_int_distribution<std::uint64_t> dist(0, n - 1);
    for (std::uint64_t i = 0; i < N; ++i) std::cout << dist(eng) << '\n';
#if defined(_LIBCPP_VERSION)
    std::cerr << "library: libc++ " << _LIBCPP_VERSION << '\n';
#elif defined(__GLIBCXX__)
    std::cerr << "library: libstdc++ " << __GLIBCXX__ << '\n';
#elif defined(_MSC_VER)
    std::cerr << "library: MSVC " << _MSC_VER << '\n';
#endif
    return 0;
}
