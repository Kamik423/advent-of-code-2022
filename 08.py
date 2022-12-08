#! /usr/bin/env python3

import aoc
import matplotlib.pyplot as plt


def main(timer: aoc.Timer) -> None:
    tree_heights: list[list[int]] = aoc.get_dense_int_matrix()
    height = len(tree_heights)
    width = len(tree_heights[0])

    def is_hidden(y: int, x: int) -> bool:
        target_height = tree_heights[y][x]
        return (
            any(tree_heights[y_][x] >= target_height for y_ in range(y))
            and any(tree_heights[y_][x] >= target_height for y_ in range(y + 1, height))
            and any(tree_heights[y][x_] >= target_height for x_ in range(x))
            and any(tree_heights[y][x_] >= target_height for x_ in range(x + 1, width))
        )

    def scenic_score(y: int, x: int) -> int:
        target_height = tree_heights[y][x]
        score = 1
        accumulator = 0
        for y_ in range(y - 1, -1, -1):
            accumulator += 1
            if tree_heights[y_][x] >= target_height:
                break
        score *= accumulator
        accumulator = 0
        for y_ in range(y + 1, height):
            accumulator += 1
            if tree_heights[y_][x] >= target_height:
                break
        score *= accumulator
        accumulator = 0
        for x_ in range(x - 1, -1, -1):
            accumulator += 1
            if tree_heights[y][x_] >= target_height:
                break
        score *= accumulator
        accumulator = 0
        for x_ in range(x + 1, width):
            accumulator += 1
            if tree_heights[y][x_] >= target_height:
                break
        score *= accumulator
        return score

    hidden_trees = [
        [is_hidden(y, x) for x, _ in enumerate(row)]
        for y, row in enumerate(tree_heights)
    ]
    print(width * height - sum(sum(row) for row in hidden_trees))
    timer.mark()
    scenic_scores = [
        [scenic_score(y, x) for x, _ in enumerate(row)]
        for y, row in enumerate(tree_heights)
    ]
    print(max(max(row) for row in scenic_scores))

    # plt.imshow(tree_heights)
    # # plt.imshow(hidden_trees)
    # plt.show()


if __name__ == "__main__":
    with aoc.Timer() as timer:
        main(timer)
