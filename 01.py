#! /usr/bin/env python3

import aoc


def main(timer: aoc.Timer) -> None:
    elves = list(
        reversed(
            sorted(
                [
                    sum(int(line.strip()) for line in elf.split("\n") if line)
                    for elf in aoc.get_str(1).split("\n\n")
                ]
            )
        )
    )
    print(elves[0])
    timer.mark()
    print(sum(elves[:3]))


if __name__ == "__main__":
    with aoc.Timer() as timer:
        main(timer)
