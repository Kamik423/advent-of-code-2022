#! /usr/bin/env python3

from queue import Queue

import aoc

DIRECTIONS = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]


def main(timer: aoc.Timer) -> None:
    positions: list[tuple[int, int, int]] = [
        tuple(line)
        for line in aoc.Parse().regex_lines("(\d+),(\d+),(\d+)", (int, int, int)).get()
    ]
    world = [
        [[(x, y, z) in positions for z in range(22)] for y in range(22)]
        for x in range(22)
    ]

    print(
        sum(
            world[x][y][z] and not world[x + dx][y + dy][z + dz]
            for x in range(21)
            for y in range(21)
            for z in range(21)
            for (dx, dy, dz) in DIRECTIONS
        )
    )

    timer.mark()

    queue = Queue()
    queue.put((-1, -1, -1))
    found: set[tuple[int, int, int]] = set()
    found_faces = 0

    while queue.qsize():
        x, y, z = position = queue.get()
        if position in found:
            continue
        found.add(position)
        for dx, dy, dz in DIRECTIONS:
            x_, y_, z_ = next_position = x + dx, y + dy, z + dz
            if -1 <= x_ <= 21 and -1 <= y_ <= 21 and -1 <= z_ <= 21:
                if world[x_][y_][z_]:
                    found_faces += 1
                else:
                    queue.put(next_position)
    print(found_faces)


if __name__ == "__main__":
    with aoc.Timer() as timer:
        main(timer)
