#! /usr/bin/env python3


import aoc


def main(timer: aoc.Timer) -> None:
    ranges: list[tuple[int, int, int, int]] = (
        aoc.Parse().regex_lines(r"(\d+)-(\d+),(\d+)-(\d+)", (int, int, int, int)).get()
    )
    print(sum(a <= c <= d <= b or c <= a <= b <= d for a, b, c, d in ranges))
    timer.mark()
    print(sum(a <= d and c <= b for a, b, c, d in ranges))


if __name__ == "__main__":
    with aoc.Timer() as timer:
        main(timer)
