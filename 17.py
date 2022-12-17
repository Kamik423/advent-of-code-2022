#! /usr/bin/env python3

from functools import cache
from itertools import cycle, zip_longest

import aoc
import more_itertools
from tqdm import tqdm

ROCKS = [
    [0b0011110],
    [0b0001000, 0b0011100, 0b0001000],
    [0b0011100, 0b0000100, 0b0000100],  # bottom up!
    [0b0010000, 0b0010000, 0b0010000, 0b0010000],
    [0b0011000, 0b0011000],
]

TOWER_CUTOFF_LENGTH = 40

State = (tuple[int, ...], int, int)
# tower: tuple[int, ...], piece_index: int, command_index: int


def main(timer: aoc.Timer) -> None:
    commands = aoc.get_str().strip()

    @cache
    def simulate_single_step(
        tower: tuple[int, ...], piece: tuple[int, ...], command: str
    ) -> tuple[tuple[int, ...], bool]:  # piece, terminate
        if command == ">":
            if not any(line & 0b0000001 for line in piece) and not any(
                (pl >> 1) & tl for (pl, tl) in zip(piece, tower)
            ):
                piece = tuple((line >> 1 for line in piece))
        else:
            if not any(line & 0b1000000 for line in piece) and not any(
                (pl << 1) & tl for (pl, tl) in zip(piece, tower)
            ):
                piece = tuple((line << 1 for line in piece))
        if (
            any(
                t & p
                for t, p in zip_longest([0b1111111] + list(tower), piece, fillvalue=0)
            )
            or piece[0]
        ):
            return (piece, True)
        else:
            return (piece[1:], False)

    def print_tower(tower: tuple[int, ...], prefix: any = "") -> None:
        for line in reversed(tower):
            print(str(prefix) + (f"|{line:07b}|".replace("0", " ").replace("1", "#")))
        print("+-------+")

    @cache
    def simulate_piece(
        tower: tuple[int, ...], piece_index: int, command_index: int
    ) -> tuple[State, int]:
        # tower, new piece index, new command index, height added
        piece = tuple([0] * len(tower) + [0, 0, 0] + ROCKS[piece_index])
        terminated = False
        while not terminated:
            piece, terminated = simulate_single_step(
                tower, piece, commands[command_index]
            )
            command_index = (command_index + 1) % len(commands)
        new_tower = tuple([t | p for t, p in zip_longest(tower, piece, fillvalue=0)])
        return (
            (
                new_tower[-TOWER_CUTOFF_LENGTH:],
                (piece_index + 1) % len(ROCKS),
                command_index,
            ),
            len(new_tower) - len(tower),
        )

    @cache
    def simulate_pieces(npieces: int, state: State = ((), 0, 0)) -> tuple[State, int]:
        # tower, new piece index, new command index, height added
        height = 0
        for _ in range(npieces):
            state, delta_height = simulate_piece(*state)
            height += delta_height
        return (state, height)

    _, height = simulate_pieces(2022)
    print(height)

    timer.mark()

    total = 1000000000000
    stepsize = 100_000
    state = ((), 0, 0)
    height = 0
    for _ in tqdm(range(int(total / stepsize))):
        state, delta_height = simulate_pieces(stepsize, state)
        height += delta_height
    print(height)


if __name__ == "__main__":
    # aoc.mock(">>><<><>><<<>><>>><<<>>><<<><<<>><>><<>>")
    with aoc.Timer() as timer:
        main(timer)
