#! /usr/bin/env python3

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import aoc


class Hand(Enum):
    ROCK = 1
    PAPER = 2
    SCISSORS = 3

    @classmethod
    def from_letter(cls, letter: str) -> Hand:
        return {
            "A": Hand.ROCK,
            "B": Hand.PAPER,
            "C": Hand.SCISSORS,
            "X": Hand.ROCK,
            "Y": Hand.PAPER,
            "Z": Hand.SCISSORS,
        }[letter]

    @property
    def base_score(self) -> int:
        return {Hand.ROCK: 1, Hand.PAPER: 2, Hand.SCISSORS: 3}[self]

    def move_according_to(self, rule: Hand) -> Hand:
        return self + {Hand.ROCK: -1, Hand.PAPER: 0, Hand.SCISSORS: 1}[rule]

    def __matmul__(self, other: Hand) -> Game:
        return Game(self, other)

    def __lt__(self, other: Hand) -> bool:
        return self + 1 == other

    def __gt__(self, other: Hand) -> bool:
        return self - 1 == other

    def __add__(self, other: int) -> Hand:
        return Hand((self.base_score - 1 + other) % 3 + 1)

    def __sub__(self, other: int) -> Hand:
        return Hand((self.base_score - 1 - other) % 3 + 1)


@dataclass
class Game:
    left: Hand
    right: Hand

    @property
    def victory_score(self) -> int:
        if self.left < self.right:
            return 6
        if self.left == self.right:
            return 3
        return 0

    @property
    def total_game_score(self) -> int:
        return self.victory_score + self.right.base_score


def main(timer: aoc.Timer) -> None:
    games = [[Hand.from_letter(c) for c in lne.split(" ")] for lne in aoc.get_lines(2)]
    # games = [
    #     "A Y",
    #     "B X",
    #     "C Z",
    # ]
    print(sum((a @ b).total_game_score for a, b in games))
    timer.mark()
    print(
        sum(
            (a @ b).total_game_score
            for a, b in [(a, a.move_according_to(b)) for a, b in games]
        )
    )


if __name__ == "__main__":
    with aoc.Timer() as timer:
        main(timer)
