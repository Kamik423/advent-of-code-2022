#! /usr/bin/env python3

from dataclasses import dataclass
from functools import cached_property

import aoc
from tqdm import tqdm


def manhattan(x1: int, y1: int, x2: int, y2: int) -> int:
    return abs(x1 - x2) + abs(y1 - y2)


@dataclass(unsafe_hash=True)
class Sensor:
    x: int
    y: int
    bx: int
    by: int

    def manhattan(self, other_x: int, other_y: int) -> int:
        return manhattan(
            self.x,
            self.y,
            other_x,
            other_y,
        )

    @cached_property
    def radius(self) -> int:
        return self.manhattan(self.bx, self.by)

    def cannot_contain_beacon(self, test_x: int, test_y: int) -> bool:
        return self.manhattan(test_x, test_y) <= self.radius

    @property
    def perimeter(self) -> list[tuple[int, int]]:
        width = self.radius + 1
        return [
            (self.x + dx, self.y + factor * (width - abs(dx)))
            for factor in (1, -1)
            for dx in range(-width, width + 1)
        ]
        # there are duplicates at both extrema but filtering them is slower and


def main(timer: aoc.Timer, simple: bool = False) -> None:
    sensors = [
        Sensor(*args)
        for args in aoc.Parse()
        .regex_lines(
            r"Sensor at x=(-?\d+), y=(-?\d+): closest beacon is at x=(-?\d+), y=(-?\d+)",
            (int, int, int, int),
        )
        .get()
    ]

    scanline = 2_000_000
    width = 4_000_000

    if simple:
        scanline = 10
        width = 20

    min_x = min(sensor.x - sensor.radius for sensor in sensors)
    max_x = max(sensor.x + sensor.radius for sensor in sensors)
    min_y = min(sensor.y - sensor.radius for sensor in sensors)
    max_y = max(sensor.y + sensor.radius for sensor in sensors)

    def cannot_contain_beacon(
        test_x: int, test_y: int, exclude_beacon: bool = True
    ) -> bool:
        return any(
            sensor.cannot_contain_beacon(test_x, test_y)
            and not (exclude_beacon and (sensor.bx, sensor.by) == (test_x, test_y))
            for sensor in sensors
        )

    timer.mark("Preprocessing")

    print(
        sum(cannot_contain_beacon(x, scanline) for x in tqdm(range(min_x, max_x + 1)))
    )

    timer.mark()

    # # Brute Force: 3.5 years
    # x, y = next(
    #     (x, y)
    #     for x in tqdm(range(width + 1))
    #     for y in tqdm(range(width + 1), leave=False)
    #     if not cannot_contain_beacon(x, y, exclude_beacon=False)
    # )

    # since we know that there is only one valid beacon we search the perimeter
    # of each sensor, so just outside its allowed range. This greatly reduces
    # the search space and reduces the runtime from ~3.5years to a few minutes.
    x, y = next(
        (x, y)
        for sensor in tqdm(sensors, leave=False)
        for (x, y) in tqdm(sensor.perimeter, leave=False)
        if 0 <= x <= width
        and 0 <= y <= width
        and not cannot_contain_beacon(x, y, exclude_beacon=False)
    )

    print(x * 4_000_000 + y)


if __name__ == "__main__":
    # aoc.mock(
    #     "Sensor at x=2, y=18: closest beacon is at x=-2, y=15\n"
    #     "Sensor at x=9, y=16: closest beacon is at x=10, y=16\n"
    #     "Sensor at x=13, y=2: closest beacon is at x=15, y=3\n"
    #     "Sensor at x=12, y=14: closest beacon is at x=10, y=16\n"
    #     "Sensor at x=10, y=20: closest beacon is at x=10, y=16\n"
    #     "Sensor at x=14, y=17: closest beacon is at x=10, y=16\n"
    #     "Sensor at x=8, y=7: closest beacon is at x=2, y=10\n"
    #     "Sensor at x=2, y=0: closest beacon is at x=2, y=10\n"
    #     "Sensor at x=0, y=11: closest beacon is at x=2, y=10\n"
    #     "Sensor at x=20, y=14: closest beacon is at x=25, y=17\n"
    #     "Sensor at x=17, y=20: closest beacon is at x=21, y=22\n"
    #     "Sensor at x=16, y=7: closest beacon is at x=15, y=3\n"
    #     "Sensor at x=14, y=3: closest beacon is at x=15, y=3\n"
    #     "Sensor at x=20, y=1: closest beacon is at x=15, y=3"
    # )
    with aoc.Timer() as timer:
        main(timer, simple=False)  # Simple is for moch
