"""Exact model of the Windows C runtime rand() (MSVCRT/UCRT, also used by MinGW):
state = state*214013 + 2531011 (mod 2^32); return (state >> 16) & 0x7FFF; srand(s) sets state = s."""


class MsvcRand:
    def __init__(self, seed: int):
        self.state = seed & 0xFFFFFFFF

    def rand(self) -> int:
        self.state = (self.state * 214013 + 2531011) & 0xFFFFFFFF
        return (self.state >> 16) & 0x7FFF
