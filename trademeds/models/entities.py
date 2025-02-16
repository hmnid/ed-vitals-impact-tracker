from dataclasses import dataclass, field
from datetime import datetime
from functools import partial
from collections import defaultdict

dataclass = partial(dataclass, kw_only=True)


@dataclass
class Market:
    market_id: int
    station_name: str
    system_name: str
    is_carrier: bool


@dataclass
class MissionFactionEffect:
    faction: str
    effect_localised: str
    effect: str
    trend: str


@dataclass
class Mission:
    mission_id: int
    title: str
    technical_name: str
    faction: str
    effects: list = field(default_factory=list)
    complete: bool = False


@dataclass
class CargoMission(Mission):
    good: str
    count: int
    system: str
    station: str | None


@dataclass
class DonationMission(Mission):
    donated: int


@dataclass
class CargoSession:
    started_at: datetime
    ended_at: datetime
    sold: dict[int, dict[str, int]]
    bought: dict[int, dict[str, int]]
    missions: dict[int, CargoMission]
