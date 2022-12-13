#! /usr/bin/env python3

import string
from queue import Queue

import aoc


def main(timer: aoc.Timer) -> None:
    height_map = aoc.get_lines()
    start: tuple[int, int]
    end: tuple[int, int]
    altitudes: list[list[int]] = []
    for y, line in enumerate(height_map):
        altitudes.append([])
        for x, char in enumerate(line):
            value: int
            try:
                value = string.ascii_lowercase.index(char)
            except ValueError:
                if char == "S":
                    start = (y, x)
                    value = 0
                elif char == "E":
                    end = (y, x)
                    value = 25
                else:
                    assert False, char
            altitudes[-1].append(value)
    timer.mark("Parsing")

    explored: set[tuple[int, int]] = set()
    queue = Queue()
    queue.put((*start, 0))

    while queue.qsize():  # BFS
        y, x, distance = queue.get()
        if (y, x) == end:
            print(distance)
            break
        if (y, x) in explored:
            continue
        for y_, x_ in [(y - 1, x), (y, x - 1), (y + 1, x), (y, x + 1)]:
            if not (0 <= y_ < len(altitudes) and 0 <= x_ < len(altitudes[0])):
                continue
            if altitudes[y_][x_] > altitudes[y][x] + 1:
                continue
            queue.put((y_, x_, distance + 1))
        explored.add((y, x))
    else:
        print("No path??")

    timer.mark()
    # crappy paste

    explored: set[tuple[int, int]] = set()
    queue = Queue()
    queue.put((*end, 0))

    while queue.qsize():  # BFS
        y, x, distance = queue.get()
        if (altitude := altitudes[y][x]) == 0:
            print(distance)
            break
        if (y, x) in explored:
            continue
        for y_, x_ in [(y - 1, x), (y, x - 1), (y + 1, x), (y, x + 1)]:
            if not (0 <= y_ < len(altitudes) and 0 <= x_ < len(altitudes[0])):
                continue
            if altitudes[y_][x_] < altitude - 1:
                continue
            queue.put((y_, x_, distance + 1))
        explored.add((y, x))
    else:
        print("No path??")


if __name__ == "__main__":
    # aoc.mock("Sabqponm\nabcryxxl\naccszExk\nacctuvwj\nabdefghi")
    with aoc.Timer() as timer:
        main(timer)
