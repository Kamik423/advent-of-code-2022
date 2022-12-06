#! /usr/bin/env python3

import aoc
import more_itertools


def main(timer: aoc.Timer) -> None:
    signal = aoc.get_str()

    def first_window_end(size: int) -> int:
        return next(
            index + size
            for index, window in enumerate(more_itertools.sliding_window(signal, size))
            if len(set(window)) == size
        )

    print(first_window_end(4))
    timer.mark()
    print(first_window_end(14))


if __name__ == "__main__":
    with aoc.Timer() as timer:
        main(timer)
