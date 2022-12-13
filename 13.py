#! /usr/bin/env python3

from __future__ import annotations

import itertools
from enum import Enum, auto
from functools import cmp_to_key

import aoc

Package = list["Package"] | int


class Order(Enum):
    RIGHT = -1
    EQUAL = 0
    WRONG = 1


def main(timer: aoc.Timer) -> None:
    inputs: list[tuple[Package, Package]] = [
        [eval(line) for line in block.strip().split("\n")]
        for block in aoc.get_str().split("\n\n")
    ]

    def order(left: Package, right: Package) -> Order:
        if isinstance(left, int) and isinstance(right, int):
            if left == right:
                return Order.EQUAL
            if left < right:
                return Order.RIGHT
            if left > right:
                return Order.WRONG
        if isinstance(left, list) and isinstance(right, list):
            for left_, right_ in itertools.zip_longest(left, right):
                if left_ is None:
                    return Order.RIGHT
                if right_ is None:
                    return Order.WRONG
                if (sub_order := order(left_, right_)) != Order.EQUAL:
                    return sub_order
            return Order.EQUAL
        if isinstance(left, list) and isinstance(right, int):
            return order(left, [right])
        if isinstance(left, int) and isinstance(right, list):
            return order([left], right)
        assert False, "This case does not exist"

    print(
        sum(
            [
                index + 1
                for index, (left, right) in enumerate(inputs)
                if order(left, right) == Order.RIGHT
            ]
        )
    )

    timer.mark()

    all_packages = sorted(
        [*[instr for block in inputs for instr in block], [[2]], [[6]]],
        key=cmp_to_key(lambda left, right: order(left, right).value),
    )
    print((all_packages.index([[2]]) + 1) * (all_packages.index([[6]]) + 1))


if __name__ == "__main__":
    with aoc.Timer() as timer:
        main(timer)
