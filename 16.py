#! /usr/bin/env python3

from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from queue import PriorityQueue, Queue
from typing import Generator

import aoc
from tqdm import tqdm


@dataclass
class Valve:
    name: str
    flow_rate: int
    destination_valve_names: list[str]

    def __init__(self, name: str, flow_rate: int, destination_valve_names_string: str):
        self.name, self.flow_rate = name, flow_rate
        self.destination_valve_names = destination_valve_names_string.split(", ")


def main(timer: aoc.Timer) -> None:
    valves = {
        args[0]: Valve(*args)
        for args in aoc.Parse()
        .regex_lines(
            r"Valve (.+) has flow rate=(\d+); tunnels? leads? to valves? (.+)",
            (str, int, str),
        )
        .get()
    }
    true_valves = [v.name for v in valves.values() if v.flow_rate]

    distances: dict[dict[str, int]] = {}
    for start_valve in set(["AA", *list(true_valves)]):
        distances[start_valve] = {}
        queue = Queue()
        queue.put((start_valve, 0))
        found_nodes: set[str] = set([start_valve])
        while queue.qsize():  # BFS
            valve, distance = queue.get()
            found_nodes.add(valve)
            if valve in true_valves:
                distances[start_valve][valve] = distance
            for adjacent in valves[valve].destination_valve_names:
                if adjacent in found_nodes:
                    continue
                queue.put((adjacent, distance + 1))

    timer.mark("Reducing")

    THE_END = 30

    @dataclass(unsafe_hash=True)
    class ExplorationState:
        time_passed: int = 0
        node: str = "AA"
        open_valves: list[str] = field(default_factory=list)
        accumulated_flow_rate: int = 0

        @property
        def next_states(self) -> Generator[ExplorationState, None, None]:
            valve = valves[self.node]
            current_flow_rate = sum(valves[v].flow_rate for v in self.open_valves)
            did_at_all_continue_on = False
            if self.node not in self.open_valves and valve.flow_rate > 0:
                did_at_all_continue_on = True
                yield ExplorationState(
                    self.time_passed + 1,
                    self.node,
                    [self.node, *self.open_valves],
                    self.accumulated_flow_rate + current_flow_rate,
                )
            else:
                for adjacent_node, additional_distance in distances[self.node].items():
                    if adjacent_node in self.open_valves:
                        continue
                    if additional_distance + self.time_passed > THE_END:
                        continue
                    did_at_all_continue_on = True
                    yield ExplorationState(
                        self.time_passed + additional_distance,
                        adjacent_node,
                        self.open_valves,
                        self.accumulated_flow_rate
                        + current_flow_rate * additional_distance,
                    )
            if not did_at_all_continue_on:
                yield ExplorationState(
                    THE_END,
                    self.node,
                    self.open_valves,
                    self.accumulated_flow_rate
                    + current_flow_rate * (THE_END - self.time_passed),
                )

        def __lt__(self, other: ExplorationState) -> bool:
            return self.time_passed < other.time_passed

    def search() -> list[ExplorationState]:
        queue = PriorityQueue()
        queue.put(ExplorationState())
        final_states: list[ExplorationState] = []
        while queue.qsize():  # BFS
            state = queue.get()
            # print(state.time_passed, state.accumulated_flow_rate)
            if state.time_passed == THE_END:
                final_states.append(state)
                continue
            if state.time_passed > THE_END:
                break
            for next_state in state.next_states:
                queue.put(next_state)
        return final_states

    optimal_single_search = max(s.accumulated_flow_rate for s in search())
    print(optimal_single_search)
    timer.mark()

    THE_END = 26

    combi_flow_rates: list[int] = []
    states = [
        s for s in search() if s.accumulated_flow_rate > 0.5 * optimal_single_search
    ]
    for a, b in tqdm(
        itertools.permutations(states, 2), total=len(states) * (len(states) - 1)
    ):
        if set(a.open_valves).intersection(b.open_valves):
            continue
        combi_flow_rates.append(a.accumulated_flow_rate + b.accumulated_flow_rate)
    print(max(combi_flow_rates))


if __name__ == "__main__":
    # aoc.mock(
    #     "Valve AA has flow rate=0; tunnels lead to valves DD, II, BB\n"
    #     "Valve BB has flow rate=13; tunnels lead to valves CC, AA\n"
    #     "Valve CC has flow rate=2; tunnels lead to valves DD, BB\n"
    #     "Valve DD has flow rate=20; tunnels lead to valves CC, AA, EE\n"
    #     "Valve EE has flow rate=3; tunnels lead to valves FF, DD\n"
    #     "Valve FF has flow rate=0; tunnels lead to valves EE, GG\n"
    #     "Valve GG has flow rate=0; tunnels lead to valves FF, HH\n"
    #     "Valve HH has flow rate=22; tunnel leads to valve GG\n"
    #     "Valve II has flow rate=0; tunnels lead to valves AA, JJ\n"
    #     "Valve JJ has flow rate=21; tunnel leads to valve II"
    # )
    with aoc.Timer() as timer:
        main(timer)
