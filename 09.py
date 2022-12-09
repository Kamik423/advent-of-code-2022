#! /usr/bin/env python3

from __future__ import annotations

import itertools
from dataclasses import dataclass

import aoc


def sign(value: int) -> int:
    if value > 0:
        return 1
    if value < 0:
        return -1
    return 0


@dataclass
class Position:
    x: int
    y: int

    def translated(self, dx: int, dy: int) -> Position:
        return Position(self.x + dx, self.y + dy)

    def translated_in_direction(self, direction: str) -> Position:
        return self.translated(
            *({"U": (0, 1), "L": (-1, 0), "D": (0, -1), "R": (1, 0)}[direction])
        )

    def __sub__(self, other: Position) -> Position:
        return self.translated(dx=-other.x, dy=-other.y)

    def __add__(self, other: Position) -> Position:
        return self.translated(dx=other.x, dy=other.y)

    @property
    def is_adjacent(self) -> bool:
        return abs(self.x) <= 1 and abs(self.y) <= 1

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def following(self, other: Position) -> Position:
        if not (delta := other - self).is_adjacent:
            return self.translated(dx=sign(delta.x), dy=sign(delta.y))
        return self


def main(timer: aoc.Timer) -> None:
    commands: list[tuple[str, int]] = (
        aoc.Parse().regex_lines(r"(\w) (\d+)", (str, int)).get()
    )
    timer.mark("Parsing")

    head = Position(0, 0)
    tail = Position(0, 0)
    visited: set[Position] = set()
    for direction, distance in commands:
        for _ in range(distance):
            head = head.translated_in_direction(direction)
            visited.add(tail := tail.following(head))
    print(len(visited))

    timer.mark()

    joints = [Position(0, 0) for _ in ["H", 1, 2, 3, 4, 5, 6, 7, 8, 9]]
    visited = set()
    for direction, distance in commands:
        for _ in range(distance):
            joints[0] = joints[0].translated_in_direction(direction)
            joints = [joints[0]] + [
                relative_tail.following(relative_head)
                for relative_head, relative_tail in itertools.pairwise(joints)
            ]
            visited.add(joints[-1])
    print(len(visited))


if __name__ == "__main__":
    with aoc.Timer() as timer:
        main(timer)
