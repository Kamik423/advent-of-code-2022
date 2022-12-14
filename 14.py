#! /usr/bin/env python3

import itertools

import aoc


def main(timer: aoc.Timer) -> None:
    occupied_spaces: set[tuple[int, int]] = set()
    for line in aoc.get_lines():
        for (x1, y1), (x2, y2) in itertools.pairwise(
            [
                (int(pair.split(",")[0]), int(pair.split(",")[1]))
                for pair in line.split(" -> ")
            ]
        ):
            if x1 == x2:
                for y in range(min(y1, y2), max(y1, y2) + 1):
                    occupied_spaces.add((x1, y))
            elif y1 == y2:
                for x in range(min(x1, x2), max(x1, x2) + 1):
                    occupied_spaces.add((x, y1))
            else:
                assert False

    timer.mark("Preprocessing")

    max_y = max([space[1] for space in occupied_spaces])
    sand_count = 0
    running = True
    while running:
        x = 500
        y = 0
        sand_count += 1
        while True:
            if y > max_y:
                running = False
                break
            for x_, y_ in ((x, y + 1), (x - 1, y + 1), (x + 1, y + 1)):
                if (x_, y_) not in occupied_spaces:
                    x, y = x_, y_
                    break
            else:
                occupied_spaces.add((x, y))
                break

    sand_count -= 1
    print(sand_count)

    timer.mark()
    running = True
    while running:
        x = 500
        y = 0
        sand_count += 1
        while True:
            for x_, y_ in ((x, y + 1), (x - 1, y + 1), (x + 1, y + 1)):
                if (x_, y_) not in occupied_spaces and y_ < max_y + 2:
                    x, y = x_, y_
                    break
            else:
                occupied_spaces.add((x, y))
                if (x, y) == (500, 0):
                    running = False
                break

    print(sand_count)


if __name__ == "__main__":
    # aoc.mock("498,4 -> 498,6 -> 496,6\n503,4 -> 502,4 -> 502,9 -> 494,9")
    with aoc.Timer() as timer:
        main(timer)
