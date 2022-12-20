#! /usr/bin/env python3

import aoc

KEY = 811589153


def main(timer: aoc.Timer) -> None:
    vector: list[tuple[int, int]] = list(enumerate(aoc.get_integers()))
    numbers_to_shift = list(vector)

    def mix() -> None:
        for thingy in numbers_to_shift:
            index = vector.index(thingy)
            vector.pop(index)
            vector.insert((index + thingy[1]) % len(vector), thingy)
            # print(vector)

    def score() -> int:
        zero_index = next(i for i, a in enumerate(vector) if a[1] == 0)
        return sum(
            vector[(zero_index + i) % len(vector)][1] for i in [1000, 2000, 3000]
        )

    mix()
    print(score())
    timer.mark()

    numbers_to_shift = [(a, b * KEY) for (a, b) in numbers_to_shift]
    vector = list(numbers_to_shift)
    for _ in range(10):
        mix()
    print(score())


if __name__ == "__main__":
    # aoc.mock("1\n2\n-3\n3\n-2\n0\n4")
    with aoc.Timer() as timer:
        main(timer)
