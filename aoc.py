"""Library to get advent of code input for 2022.

It uses a cookie file (COOKIE.txt) to authenticate you on the aoc server. It
then downloads and caches the input as not to spam the server.

The cookie is a long hexadecimal number that you can manually extract from a
manual request in your browser. Extract it and put it into the file COOKIE.txt
next to your main Python scripts. Remember to append COOKIE.txt to your
.gitignore.

Files will be downloaded to a directory named `input` in the same directory as
your main Python script. It will be created if it does not exist. For every day
the script downloads the input and returns it from there. You don't need to
manually call code to download the file, it will just happen automatically the
first time you request anything for that day. All you have to do is call one
of the following lines:

    aoc.get(1) # bytes data for day one
    aoc.get_str(1) # string data for day one
    aoc.get_lines(1) # input lines for day one
    aoc.get_integers(1) # integers for day one (one per line)
    aoc.get_comma_integers(1) # get one line of integers separated by commas
    aoc.get_dense_int_matrix(1) # get a 2d matrix of ints with one per character

    aoc.get_integers() # when called from `01-minimal.py` gets ints for day 1.

You can also leave out the number and it will get guessed from the file name of
the main Python file by just taking all the numbers in the file name. So for
example `day_03.py` or `03-alternate.py` would query day 3; however files like
`aoc-2022-day-03-part-2.py` would attempt to query day 2022032 which is not
what you want. You can rewrite that method, rename your files, or specify the
day manually.

Complex queries are possible, read the documentation for Parse below.

    foo, bar = aoc.Parse().comma_integers().regex(r"(\d+) => (.+)", (int, str))

would parse a file that looks like

    1,2,3,4,5,6

    1 => a
    2 => b
    3 => c

and write a list of integers into foo, and a list of tuples, here [(1, "a"),
(2, "b"), ...] into bar.

This module also provides timer functionality. Read the documentation for Timer
below.

Attributes:
    CACHE_DIRECTORY (Path): The directory to put the daily inputs in.
    CACHE_FILE_NAME_TEMPLATE (str): The name template for daily cache files.
    COOKIE_PATH (Path): The computed path to the cookie file.
    MOCKS (dict[int | None, bytes]): Mocked inputs for testing.
    PROJECT_FOLDER (Path): The computed directory the main file is in.
    URL (str): A format url for a given day.
"""

from __future__ import annotations

import re
import sys
import time
from itertools import pairwise
from pathlib import Path
from typing import Callable, Iterator

import requests

PROJECT_FOLDER = Path(sys.argv[0]).parent
COOKIE_PATH = PROJECT_FOLDER / "COOKIE.txt"
URL = "https://adventofcode.com/2022/day/{}/input"
CACHE_FILE_NAME_TEMPLATE = "{:02d}.txt"
CACHE_DIRECTORY = PROJECT_FOLDER / "input"
MOCKS: dict[int | None, bytes] = {}

# ==============================================================================
# General functions to interface with AOC and fetch files


def cache_file_for_day(day: int) -> Path:
    """Return the cache file path for a given day.

    Args:
        day (int): The day number

    Returns:
        Path: The cache file for the day.
    """
    return CACHE_DIRECTORY / CACHE_FILE_NAME_TEMPLATE.format(day)


def ensure_downloaded(day: int) -> None:
    """Ensure the input for a given day is downloaded.

    Args:
        day (int): The day number.
    """
    cache_file = cache_file_for_day(day)
    if not cache_file.exists():
        cookies = {"session": COOKIE_PATH.read_text().strip()}
        CACHE_DIRECTORY.mkdir(exist_ok=True)
        cache_file.write_bytes(requests.get(URL.format(day), cookies=cookies).content)


def guess_day_from_filename() -> int:
    """Compute the day from the main filename.

    Every digit character is put together and converted to integer.

    Returns:
        int: The guessed day.
    """
    filename = Path(sys.argv[0]).name
    return int("".join([letter for letter in filename if letter.isdigit()]))


def get(day: int | None = None) -> bytes:
    """Get bytes input for a specified day.

    If no day is specified it will try to guess from your file name by grabbing
    all of the integers.

    Args:
        day (int | None, optional): The day number.

    Returns:
        bytes: The input for they day.
    """
    if (mocked := MOCKS.get(None)) is not None:
        return mocked
    day = day or guess_day_from_filename()
    if (mocked := MOCKS.get(day)) is not None:
        return mocked
    ensure_downloaded(day)
    return cache_file_for_day(day).read_bytes()


def get_str(day: int | None = None) -> str:
    """Get the string input for a specified day.

    If no day is specified it will try to guess from your file name by grabbing
    all of the integers.

    Args:
        day (int | None, optional): The day number.

    Returns:
        str: The input for the day.
    """
    return get(day).decode("utf8")


def get_lines(day: int | None = None) -> list[str]:
    """Get one string per line for a specified day.

    If no day is specified it will try to guess from your file name by grabbing
    all of the integers.

    Args:
        day (int | None, optional): The day number.

    Returns:
        list[str]: The lines.
    """
    return get_str(day).strip().split("\n")


# ==============================================================================
# Mocking inputs


def mock_bytes(data: bytes, day: int | None = None) -> None:
    """Mock a bytes content for a given day or any.

    Args:
        content (str): The mocked bytes message.
        day (int | None, optional): The day to mock for; otherwise mock all.
    """
    MOCKS[day] = data


def mock(content: str, day: int | None = None) -> None:
    """Mock a string content for a given day or any.

    Args:
        content (str): The mocked string message.
        day (int | None, optional): The day to mock for; otherwise mock all.
    """
    mock_bytes(content.encode("utf8"), day)


# ==============================================================================
# Getting complex queries


class Parse:
    """Do complex parses of multiple different blocks if necessary.

    For example

        foo, bar = aoc.Parse().comma_integers().regex(r"(\d+) => (.+)", (int, str))

    would parse a file that looks like

        1,2,3,4,5,6

        1 => a
        2 => b
        3 => c

    and write a list of integers into foo, and a list of tuples, here
    [(1, "a"), (2, "b"), ...] into bar. Read the documentation for each function
    below. A single item would not automatically be unwrapped from the list so
    it can be gotten with

        foo = aoc.Parse().comma_integers().get()

    Parse can be supplied with an optional day in the constructor.

    Attributes:
        buffer (str): The buffer of the remaining input.
        day (int): The observed day.
        sections (list): The sections that have already been parsed.
    """

    day: int
    sections: list[any]
    buffer: str

    def __init__(self, day: int | None = None, alt: str | None = None):
        self.day = day or guess_day_from_filename()
        self.sections = []
        self.buffer = get_lines(self.day) if alt is None else alt.split("\n")

    def __iter__(self) -> Iterator[any]:
        return iter(self.sections)

    def __getitem__(self, key: int) -> any:
        return self.sections[key]

    def get(self) -> any:
        """Get the single first item that has already been parsed."""
        assert len(self.sections) == 1
        return self.sections[0]

    def _remove_trailing_next(self) -> None:
        """Remove the next line if it is empty."""
        if self.buffer and (self.buffer[0] == ""):
            self.buffer.pop(0)

    def line(self) -> Parse:
        """Gets a single line."""
        self.sections.append(self.buffer.pop(0))
        self._remove_trailing_next()
        return self

    def lines(self) -> Parse:
        """Gets a list of lines until one is empty."""
        current_section: list[str] = []
        while self.buffer and (line := self.buffer.pop(0)):
            current_section.append(line)
        self.sections.append(current_section)
        return self

    def regex_lines(self, query: str, data_types: list[Callable]) -> Parse:
        """Match a list of lines until one is empty to regex and convert them
        to given data types.

        For example

            foo = aoc.Parse().regex(r"(\d+) => (.+)", (int, str)).get()

        would parse a file that looks like

            1 => a
            2 => b
            3 => c

        And write it into foo as a list of tuples looking like [(1, "a"),
        (2, "b"), (3, "c")].

        Args:
            query (str): The regex query.
            data_types (list[Callable]): The datatype conversion.
        """
        self.lines()
        pattern = re.compile(query)
        self.sections[-1] = [
            [
                dtype(match)
                for match, dtype in zip(pattern.match(line).groups(), data_types)
            ]
            for line in self.sections[-1]
        ]
        return self

    def regex_lines_single(self, query: str, data_type: Callable) -> Parse:
        """Like regex_lines but does not return a tuple but a single element."""
        self.regex_lines(query, [data_type])
        self.sections[-1] = [line[0] for line in self.sections[-1]]
        return self

    def integers(self) -> Parse:
        """Reads the lines as integers until there is an empty line."""
        self.lines()
        self.sections[-1] = [int(line) for line in self.sections[-1]]
        return self

    def comma_integers(self, separator=",") -> Parse:
        """Reads a single line as comma separated integers.

        Args:
            separator (str, optional): The separator, by default ",".
        """
        self.sections.append([int(x) for x in self.buffer.pop(0).split(separator)])
        self._remove_trailing_next()
        return self

    def dense_int_matrix(self) -> Parse:
        """Read a dense integer matrix with one integer per character into a 2d
        array. For example

            1234
            5678
            9012

        yields [[1, 2, 3, 4], [5, 6, 7, 8], [9, 0, 1, 2]].
        """
        self.lines()
        self.sections[-1] = [[int(char) for char in line] for line in self.sections[-1]]
        return self

    def remaining_lines(self) -> Parse:
        """Put the remaining lines into the next variable for manual parsing."""
        self.sections.append(self.buffer)
        self.buffer = ""
        return self


# ==============================================================================
# Simple aliases

get_integers = lambda *args: Parse(*args).integers().get()
get_comma_integers = lambda *args: Parse(*args).comma_integers().get()
get_dense_int_matrix = lambda *args: Parse(*args).dense_int_matrix().get()


# ==============================================================================
# Checks for --test command line argument


def is_test() -> bool:
    if "test" in sys.argv:
        sys.argv.remove("test")
        return True
    return False


# ==============================================================================
# Timing code runtime


class Timer:
    """Used to time days.

    Usage like:

        with aoc.Timer() as timer:
            part1()
            timer.mark()
            part2()

    It will automatically print a timed table. The initializer can get a custom
    day name if you feel like it. If you don't call mark it will be timed as one
    piece. I prefer to use it as

        import aoc

        def main(timer: aoc.Timer) -> None:
            # part 1 code
            timer.mark()
            # part 2 code


        if __name__ == "__main__":
            with aoc.Timer() as timer:
                main(timer)

    Mark can be used with a title too: mark("Fetching") to label the previous
    section. The ones which you do not provide a title for will be labeled
    "Part 1", "Part 2" and "Postprocessing" in order. The ones after will not
    receive a label.
    """

    times: list[float]
    sections: list[str]
    remaining_labels: list[str]
    finished: bool = False
    silent: bool = False

    day: str = ""

    def __init__(self, day: any | None = None, silent: bool = False):
        self.day = str(day) if day is not None else str(guess_day_from_filename())
        self.remaining_labels = ["Part 1", "Part 2", "Postprocessing"]
        self.times = []
        self.sections = []
        self.finished = False
        self.silent = silent

    def next_label(self) -> str:
        """Get the next automatically computed label

        Returns:
            str: The next free one of ["Part 1", "Part 2", "Postprocessing"].
                Otherwise just ""
        """
        return self.remaining_labels.pop(0) if self.remaining_labels else ""

    def __enter__(self) -> Timer:
        self.times = [time.time()]
        return self

    def mark(self, name: str = None) -> None:
        """Mark the end current part or section.

        Args:
            name (str, optional): The name of the section. Autolabeled usually.
        """
        self.times.append(time.time())
        self.sections.append(name or self.next_label())

    def last_mark(self, name: str = None) -> None:
        """Mark the end current part or section. Don't start a sequence after.

        Args:
            name (str, optional): The name of the section. Autolabeled usually.
        """
        self.mark(name)
        self.finished = True

    def __exit__(self, exception_type, exception_value, traceback) -> None:
        if not self.finished:
            self.times.append(time.time())
            self.sections.append(self.next_label())

        if self.silent or exception_type is not None:
            return

        self.times = [1000 * t for t in self.times]

        label_length = max(len(label) for label in self.sections)
        last_col_length = len(f"{self.times[-1] - self.times[0]:.03f}") + 3

        def separator(character: str, continuous: bool = True) -> str:
            return (
                (character * label_length)
                + (character if continuous else " ") * 4
                + (character * last_col_length)
            )

        toprule = separator("━")
        midrule = separator("─")
        bottomrule = toprule

        print(toprule)
        print(f"{'Day'.ljust(label_length)}    {self.day.rjust(last_col_length)}")
        print(midrule)
        if len(self.times) > 2:
            for (time_a, time_b), label in zip(pairwise(self.times), self.sections):
                print(
                    label.ljust(label_length)
                    + "    "
                    + f"{time_b - time_a:.03f} ms".rjust(last_col_length)
                )
            print(midrule)
        print(
            "Total".ljust(label_length)
            + "    "
            + f"{self.times[-1] - self.times[0]:.03f} ms".rjust(last_col_length)
        )

        print(bottomrule)
