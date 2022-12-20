#! /usr/bin/env python3

from __future__ import annotations

import sys
from dataclasses import dataclass
from enum import Enum, auto
from functools import cache, reduce

import aoc
from cached_property import cached_property
from joblib import Parallel, delayed

mul = lambda l: reduce((lambda x, y: x * y), l)


@dataclass(unsafe_hash=True)
class Blueprint:
    blueprint_number: int
    ore_robot_ore_cost: int
    clay_robot_ore_cost: int
    obsidian_robot_ore_cost: int
    obsidian_robot_clay_cost: int
    geode_robot_ore_cost: int
    geode_robot_obsidian_cost: int

    @cached_property
    def maximal_ore_costs(self) -> int:
        return max(
            self.ore_robot_ore_cost,
            self.clay_robot_ore_cost,
            self.obsidian_robot_ore_cost,
            self.geode_robot_ore_cost,
        )


class Robot(Enum):
    ORE = auto()
    CLAY = auto()
    OBSIDIAN = auto()
    GEODE = auto()


def main(timer: aoc.Timer) -> None:
    blueprints: list[Blueprint] = [
        Blueprint(*args)
        for args in aoc.Parse()
        .regex_lines(
            r"Blueprint (\d+): "
            r"Each ore robot costs (\d+) ore. "
            r"Each clay robot costs (\d+) ore. "
            r"Each obsidian robot costs (\d+) ore and (\d+) clay. "
            r"Each geode robot costs (\d+) ore and (\d+) obsidian.",
            (int, int, int, int, int, int, int),
        )
        .get()
    ]

    @dataclass(unsafe_hash=True)
    class State:
        blueprint_index: int

        minute: int = 0

        ore_robot_count: int = 1
        clay_robot_count: int = 0
        obsidian_robot_count: int = 0
        geode_robot_count: int = 0

        ore_count: int = 0
        clay_count: int = 0
        obsidian_count: int = 0
        geode_count: int = 0

        wants_to_build: Robot | None = None

        @property
        def blueprint(self) -> Blueprint:
            return blueprints[self.blueprint_index - 1]

        @property
        def can_construct_ore_robot(self) -> bool:
            blueprint = self.blueprint
            return self.ore_count >= blueprint.ore_robot_ore_cost

        @property
        def can_construct_clay_robot(self) -> bool:
            blueprint = self.blueprint
            return self.ore_count >= blueprint.clay_robot_ore_cost

        @property
        def can_construct_obsidian_robot(self) -> bool:
            blueprint = self.blueprint
            return (
                self.ore_count >= blueprint.obsidian_robot_ore_cost
                and self.clay_count >= blueprint.obsidian_robot_clay_cost
            )

        @property
        def can_construct_geode_robot(self) -> bool:
            blueprint = self.blueprint
            return (
                self.ore_count >= blueprint.geode_robot_ore_cost
                and self.obsidian_count >= blueprint.geode_robot_obsidian_cost
            )

        @property
        def should_still_construct_ore_robot(self) -> bool:
            blueprint = self.blueprint
            return self.ore_robot_count < blueprint.maximal_ore_costs

        @property
        def should_still_construct_clay_robot(self) -> bool:
            blueprint = self.blueprint
            return self.clay_robot_count < blueprint.obsidian_robot_clay_cost

        @property
        def will_be_able_to_construct_geode_ever(self) -> bool:
            return self.obsidian_robot_count > 0

        @property
        def will_be_able_to_construct_obsidian_ever(self) -> bool:
            return self.clay_robot_count > 0

        def can_construct(self, robot: Robot | None) -> bool:
            return (
                (robot is None)
                or ((robot is Robot.ORE) and self.can_construct_ore_robot)
                or ((robot is Robot.CLAY) and self.can_construct_clay_robot)
                or ((robot is Robot.OBSIDIAN) and self.can_construct_obsidian_robot)
                or ((robot is Robot.GEODE) and self.can_construct_geode_robot)
            )

        def next_state_constructing(self, robot: Robot | None) -> State:
            ccr = self.can_construct(robot)
            make_ore = (robot is Robot.ORE) and ccr
            make_clay = (robot is Robot.CLAY) and ccr
            make_obsidian = (robot is Robot.OBSIDIAN) and ccr
            make_geode = (robot is Robot.GEODE) and ccr
            blueprint = self.blueprint
            return State(
                blueprint_index=self.blueprint_index,
                minute=self.minute + 1,
                ore_robot_count=self.ore_robot_count + make_ore,
                clay_robot_count=self.clay_robot_count + make_clay,
                obsidian_robot_count=self.obsidian_robot_count + make_obsidian,
                geode_robot_count=self.geode_robot_count + make_geode,
                ore_count=self.ore_count
                + self.ore_robot_count
                - make_ore * blueprint.ore_robot_ore_cost
                - make_clay * blueprint.clay_robot_ore_cost
                - make_obsidian * blueprint.obsidian_robot_ore_cost
                - make_geode * blueprint.geode_robot_ore_cost,
                clay_count=self.clay_count
                + self.clay_robot_count
                - make_obsidian * blueprint.obsidian_robot_clay_cost,
                obsidian_count=self.obsidian_count
                + self.obsidian_robot_count
                - make_geode * blueprint.geode_robot_obsidian_cost,
                geode_count=self.geode_count + self.geode_robot_count,
                wants_to_build=None if ccr else robot,
            )

        @property
        def builds(self) -> list[Robot]:
            if (wants_to_build := self.wants_to_build) is not None:
                return [wants_to_build]

            if self.can_construct_geode_robot:
                return [Robot.GEODE]
            # # This would be a massive speedup (x16) but unfortunately it fails
            # # on part 2. on part 1 it is fine.
            # if self.can_construct_obsidian_robot:
            #     if self.will_be_able_to_construct_geode_ever:
            #         return [Robot.GEODE, Robot.OBSIDIAN]
            #     return [Robot.OBSIDIAN]
            return (
                ([Robot.GEODE] if self.will_be_able_to_construct_geode_ever else [])
                + (
                    [Robot.OBSIDIAN]
                    if self.will_be_able_to_construct_obsidian_ever
                    else []
                )
                + ([Robot.CLAY] if self.should_still_construct_clay_robot else [])
                + ([Robot.ORE] if self.should_still_construct_ore_robot else [])
            )

    # @cache
    def ideal_outcome(state: State, total_minutes: int) -> int:
        if state.minute >= total_minutes:
            return state.geode_count

        def ideal_outcome_constructing(robot: Robot | None) -> int:
            return ideal_outcome(state.next_state_constructing(robot), total_minutes)

        return_value = max(ideal_outcome_constructing(robot) for robot in state.builds)
        return return_value

    print(
        sum(
            Parallel(n_jobs=8)(
                delayed(
                    lambda b: ideal_outcome(State(b.blueprint_number), 24)
                    * b.blueprint_number
                )(blueprint)
                for blueprint in blueprints
            )
        )
    )

    timer.mark()

    print(
        mul(
            Parallel(n_jobs=8)(
                delayed(lambda b: ideal_outcome(State(b.blueprint_number), 32))(
                    blueprint
                )
                for blueprint in blueprints[:3]
            )
        )
    )


if __name__ == "__main__":
    # aoc.mock(
    #     "Blueprint 1: "
    #     "Each ore robot costs 4 ore. "
    #     "Each clay robot costs 2 ore. "
    #     "Each obsidian robot costs 3 ore and 14 clay. "
    #     "Each geode robot costs 2 ore and 7 obsidian."
    #     "\n"
    #     "Blueprint 2: "
    #     "Each ore robot costs 2 ore. "
    #     "Each clay robot costs 3 ore. "
    #     "Each obsidian robot costs 3 ore and 8 clay. "
    #     "Each geode robot costs 3 ore and 12 obsidian."
    # )
    with aoc.Timer() as timer:
        main(timer)
