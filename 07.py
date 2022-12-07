#! /usr/bin/env python3

from __future__ import annotations

from abc import ABC
from dataclasses import dataclass

import aoc
from cached_property import cached_property


class FileSystemObject(ABC):
    size: int


@dataclass
class File(FileSystemObject):
    size: int


@dataclass
class Directory(FileSystemObject):
    children: dict[str, FileSystemObject]

    @cached_property
    def size(self) -> int:
        return sum(child.size for child in self.children.values())

    @cached_property
    def all_directories(self) -> list[Directory]:
        return [
            subchild
            for child in self.children.values()
            if isinstance(child, Directory)
            for subchild in child.all_directories
        ] + [self]

    def children_of_size(self, size: int) -> list[Directory]:
        return [
            directory for directory in self.all_directories if directory.size <= size
        ]


def main(timer: aoc.Timer) -> None:
    stack: [Directory] = [root := Directory({})]
    for line in aoc.get_lines():
        cwd = stack[-1]
        match line.split(" "):
            case ["$", "cd", "/"]:
                stack = [root]
            case ["$", "cd", ".."]:
                stack.pop()
            case ["$", "cd", name]:
                stack.append(cwd.children[name])
            case ["$", "ls"]:
                pass
            case ["dir", name]:
                cwd.children[name] = Directory({})
            case [size, name]:
                cwd.children[name] = File(int(size))
            case _:
                assert False, f"Ununderstood line {line}"
    timer.mark("Loading")
    print(sum(directory.size for directory in root.children_of_size(100000)))
    timer.mark()
    required_size = 30000000 - (70000000 - root.size)
    print(
        min(
            size
            for directory in root.all_directories
            if (size := directory.size) >= required_size
        )
    )


if __name__ == "__main__":
    with aoc.Timer() as timer:
        main(timer)
