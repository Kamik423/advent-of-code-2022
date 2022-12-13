#! /usr/bin/env python3
from __future__ import annotations

from functools import reduce
from operator import mul
from typing import Callable

import aoc
from tqdm import tqdm


def main(timer: aoc.Timer) -> None:
    monkeys: list[Monkey] = []
    least_common_multiple: int

    class Monkey:
        number: int
        items: list[int]
        divisor: int
        target_monkeys: tuple[int, int]  # [false, true] for easy indexing
        items_evaluated = 0
        do_add: bool
        other_side: int | None

        def operation(self, number: int) -> int:
            if self.do_add:
                return number + (self.other_side or number)
            return number * (self.other_side or number)

        def __init__(self, spec: str):
            lines = spec.split("\n")
            self.number = int(lines[0].split(":")[0].split(" ")[-1])
            self.items = [
                int(x) for x in lines[1].split("  Starting items: ")[1].split(", ")
            ]
            operation_spec = lines[2].split("new = ")[1].split(" ")
            match operation_spec:
                case ["old", "*", other]:
                    self.do_add = False
                    try:
                        self.other_side = int(other)
                    except ValueError:
                        self.other_side = None
                case ["old", "+", other]:
                    self.do_add = True
                    try:
                        self.other_side = int(other)
                    except ValueError:
                        self.other_side = None
                case _:
                    assert False, f"Unknown operation: {operation_spec}"
            self.divisor = int(lines[3].split("Test: divisible by ")[1])
            self.target_monkeys = (
                int(lines[5].split("If false: throw to monkey ")[1]),
                int(lines[4].split("If true: throw to monkey ")[1]),
            )

        def evaluate(self, unlimited_worry: bool = False) -> None:
            for item in self.items:
                value: int
                if unlimited_worry:
                    value = self.operation(item) % least_common_multiple
                else:
                    value = int(self.operation(item) / 3.0)
                monkeys[self.target_monkeys[value % self.divisor == 0]].items.append(
                    value
                )
                self.items_evaluated += 1
            self.items = []

    monkeys = [Monkey(spec) for spec in aoc.get_str().split("\n\n")]

    for _ in range(20):
        for monkey in monkeys:
            monkey.evaluate()

    print(reduce(mul, sorted([monkey.items_evaluated for monkey in monkeys])[-2:], 1))

    timer.mark()

    monkeys = [Monkey(spec) for spec in aoc.get_str().split("\n\n")]
    least_common_multiple = reduce(mul, [monkey.divisor for monkey in monkeys], 1)

    for _ in tqdm(range(10000)):
        for monkey in monkeys:
            monkey.evaluate(unlimited_worry=True)

    print(reduce(mul, sorted([monkey.items_evaluated for monkey in monkeys])[-2:], 1))


if __name__ == "__main__":
    with aoc.Timer() as timer:
        main(timer)
