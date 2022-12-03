#! /usr/bin/env python3

import string

import aoc
import more_itertools


def priority(character: str) -> int:
    return string.ascii_letters.index(character) + 1


def halfs(rucksack: str) -> tuple[str, str]:
    halfway = int(len(rucksack) / 2)
    return rucksack[:halfway], rucksack[halfway:]


def intersection(left: str, right: str, very_right: str | None = None) -> str:
    for character in left:
        if character in right:
            if very_right is None or character in very_right:
                return character
    assert False


def groups(rucksacks: list[str]) -> list[tuple[str, str, str]]:
    return list(more_itertools.chunked(rucksacks, 3))


def main(timer: aoc.Timer) -> None:
    print(sum(priority(intersection(*halfs(rucksack))) for rucksack in aoc.get_lines()))
    timer.mark()
    print(sum(priority(intersection(*group)) for group in groups(aoc.get_lines())))


if __name__ == "__main__":
    with aoc.Timer() as timer:
        main(timer)
