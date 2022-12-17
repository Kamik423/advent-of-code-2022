#! /usr/bin/env python3

"""The basic approach is that each line is represented in binary so |..##.#.|
becomes 0011010. The tower then is a list of integers (actually a tuple since it
can be cached). A state vector is then propagated. It consists of the top 40
rows of the tower, the index of the current piece and the index of the current
command. A function outputs the new state vector and the height added in the
process.

The actual speed improvement comes from caching the resulting state vector and
added height after 100_000 steps and looking it up instead of computing it every
time. This occurs using @functools.cache. This very much relies on the fact that
the tower is always truncated to the exactly 40 so identical states can be
compared. This length is stored in `TOWER_CUTOFF_LENGTH`.
"""

from functools import cache
from itertools import cycle, zip_longest

import aoc
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
    ) -> tuple[tuple[int, ...], bool]:
        """Simulate a single step and drop.

        Args:
            tower (tuple[int, ...]): The tower. First element is bottom row.
            piece (tuple[int, ...]): The piece. First element is bottom row.
                There will be leading zero lines if it is still in the air as to
                keep it in sync with the tower. Line 0 is the very bottom of the
                tower.
            command (str): The command to execute. ">" or "<".

        Returns:
            tuple[int, ...]: The piece after the move.
            bool: Has the piece stopped
        """
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

    @cache
    def simulate_piece(
        tower: tuple[int, ...], piece_index: int, command_index: int
    ) -> tuple[State, int]:
        """Simulate the adding and dropping of a single piece.

        Afterward the tower is truncated to the top 40 lines for caching
        purposes. This way if an identical step has already been computed for a
        tower with that exact top then it can just be used instead of computed.

        Args:
            tower (tuple[int, ...]): The tower. First element is bottom row.
            piece_index (int): The current index of the piece.
            command_index (int): The index of the current command.

        Returns:
            State: The state after the drop. (Tower, Piece index, Command index)
            int: The height added to the tower in the process
        """
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
        """Simulate multiple pieces added in sequence.

        Inbetween the tower is truncated to the top 40 lines for caching
        purposes. This way if a sequence of `npieces` steps has already been
        computed for a tower with that exact top at this starting state (piece
        and position in the commands list) then it can just be used instead of
        computed. <!> this is the major reason for the speed of this solution.

        Args:
            npieces (int): The amount of pieces to simulate.
            state (State, optional): The state to compute for.
                (Tower, Piece index, Command index)

        Returns:
            State: The state after the drop. (Tower, Piece index, Command index)
            int: The height added to the tower in the process
        """
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
    # I tried and this seems to be the optimal power of 10. The number needs to
    # neatly divide the total but I was too lazy to test around more. ~7s is
    # good enogh for me.
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
