from collections import defaultdict
from dataclasses import dataclass
from typing import DefaultDict, Dict
from ..observers.incomplete_cargo import IncompleteMission


@dataclass(frozen=True)
class CargoGroup:
    good: str
    count: int
    faction: str


class PendingCargoView:
    def __init__(self, missions: Dict[int, IncompleteMission]) -> None:
        self.missions = missions

    def display(self) -> None:
        total_cargo = sum(mission.count for mission in self.missions.values())

        # Group by system and good
        by_system: DefaultDict[str, Dict[str, CargoGroup]] = defaultdict(dict)
        for mission in self.missions.values():
            existing = by_system[mission.system].get(mission.good)
            if existing:
                by_system[mission.system][mission.good] = CargoGroup(
                    good=mission.good,
                    count=existing.count + mission.count,
                    faction=(
                        existing.faction
                        if existing.faction == mission.faction
                        else "Multiple factions"
                    ),
                )
            else:
                by_system[mission.system][mission.good] = CargoGroup(
                    good=mission.good, count=mission.count, faction=mission.faction
                )

        print(f"\nPending cargo missions (total: {total_cargo:,} units):\n")
        for system, goods in sorted(by_system.items()):
            print(f"{system}:")
            for cargo in sorted(goods.values(), key=lambda x: (-x.count, x.good)):
                print(f"  {cargo.good}: {cargo.count:,} units for {cargo.faction}")
            print()
