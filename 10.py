#! /usr/bin/env python3

import aoc


class CPU:
    cycle = 0
    register = 1

    highlights: dict[int, int] = dict()
    screen: list[list[bool]] = list()

    def noop(self) -> None:
        self.cycle += 1
        cursor = (self.cycle - 1) % 40
        if cursor == 0:
            self.screen.append([])
        self.screen[-1].append(abs(self.register - cursor) <= 1)
        if (self.cycle - 20) % 40 == 0:
            self.highlights[self.cycle] = self.register

    def addx(self, value: int) -> None:
        self.noop()
        self.noop()
        self.register += value


def main(timer: aoc.Timer) -> None:
    cpu = CPU()
    for line in aoc.get_lines():
        match line.split(" "):
            case ["noop"]:
                cpu.noop()
            case ["addx", value]:
                cpu.addx(int(value))
            case _:
                assert False, f"unrecognized command {line}"
    print(sum(key * value for key, value in cpu.highlights.items()))
    print(
        "\n".join("".join("█" if pixel else " " for pixel in row) for row in cpu.screen)
    )


if __name__ == "__main__":
    with aoc.Timer() as timer:
        main(timer)
