from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Optional


@dataclass(kw_only=True, frozen=True)
class Market:
    market_id: int
    station_name: str
    system_name: str
    is_carrier: bool


@dataclass(kw_only=True, frozen=True)
class MissionFactionEffect:
    faction: str
    effect_localised: str
    effect: str
    trend: str


@dataclass(kw_only=True, frozen=True)
class Mission:
    mission_id: int
    title: str
    technical_name: str
    faction: str
    complete: bool = False
    effects: List[MissionFactionEffect] = field(default_factory=list)


@dataclass(kw_only=True, frozen=True)
class CargoMission(Mission):
    good: str
    count: int
    system: str
    station: Optional[str] = None


@dataclass(kw_only=True, frozen=True)
class DonationMission(Mission):
    donated: int


@dataclass(kw_only=True, frozen=True)
class CargoSession:
    started_at: datetime
    ended_at: datetime
    missions: Dict[int, Mission] = field(default_factory=dict)
    sold: Dict[int, Dict[str, int]] = field(
        default_factory=lambda: defaultdict(lambda: defaultdict(int))
    )
    bought: Dict[int, Dict[str, int]] = field(
        default_factory=lambda: defaultdict(lambda: defaultdict(int))
    )


@dataclass(kw_only=True, frozen=True)
class GenericMission(Mission):
    """A generic mission that's neither cargo delivery nor donation."""

    system: str | None = None
    station: str | None = None
