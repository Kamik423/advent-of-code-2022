#! /usr/bin/env python3

import aoc


def main(timer: aoc.Timer) -> None:
    stack_config = aoc.get_str().split("\n\n", 1)[0].split("\n")[-2::-1]

    def get_stacks() -> list[list[str]]:
        return [
            [c for line in stack_config if (c := line[stack_index * 4 - 3]) != " "]
            for stack_index in range(1, int((len(stack_config[0]) + 5) / 4))
        ]

    def move(amount: int, from_stack_index: int, to_stack_index: int) -> None:
        for _ in range(amount):
            stacks[to_stack_index - 1].append(stacks[from_stack_index - 1].pop())

    def move2(amount: int, from_stack_index: int, to_stack_index: int) -> None:
        for index in range(-amount, 0):
            stacks[to_stack_index - 1].append(stacks[from_stack_index - 1].pop(index))

    def move_all(do_print: bool = False) -> None:
        for amount, from_stack_index, to_stack_index in (
            aoc.Parse()
            .regex_lines("(.+)", [str])
            .regex_lines(r"move (\d+) from (\d) to (\d)", [int, int, int])[1]
        ):
            if do_print:
                printstacks()
                print(
                    f">>> move {amount} from {from_stack_index} to {to_stack_index}\n"
                )
            move(amount, from_stack_index, to_stack_index)
        if do_print:
            printstacks()

    def move_all2(do_print: bool = False) -> None:
        for amount, from_stack_index, to_stack_index in (
            aoc.Parse()
            .regex_lines("(.+)", [str])
            .regex_lines(r"move (\d+) from (\d) to (\d)", [int, int, int])[1]
        ):
            if do_print:
                printstacks()
                print(
                    f">>> move {amount} from {from_stack_index} to {to_stack_index}\n"
                )
            move2(amount, from_stack_index, to_stack_index)
        if do_print:
            printstacks()

    def printstacks() -> None:
        maxheight = max(len(stack) for stack in stacks)
        for height in range(maxheight - 1, -1, -1):
            for stack in stacks:
                try:
                    print(f"[{stack[height]}]", end=" ")
                except IndexError:
                    print("   ", end=" ")
            print()
        for index in range(1, len(stacks) + 1):
            print(f"{index:^3}", end=" ")
        print()

    def get_status_line() -> str:
        return "".join(stack[-1] for stack in stacks)

    stacks = get_stacks()
    move_all()
    print(get_status_line())
    timer.mark()
    stacks = get_stacks()
    move_all2()
    print(get_status_line())


if __name__ == "__main__":
    #     aoc.mock(
    #         """    [D] [ ]
    # [N] [C] [ ]
    # [Z] [M] [P]
    #  1   2   3

    # move 1 from 2 to 1
    # move 3 from 1 to 3
    # move 2 from 2 to 1
    # move 1 from 1 to 2"""
    #     )
    with aoc.Timer() as timer:
        main(timer)
