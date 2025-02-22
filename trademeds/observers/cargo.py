from collections import defaultdict
from datetime import datetime
from typing import Optional, cast
from ..models.entities import (
    Market,
    CargoMission,
    DonationMission,
    Mission,
    MissionFactionEffect,
    CargoSession,
    GenericMission,
)
from ..journal.events import (
    GameEvent,
    MarketEvent,
    MarketSellEvent,
    MissionCompletedEvent,
    LoadGameEvent,
    FactionEffectGroup,
    FactionEffect as JournalFactionEffect,
)


class CargoSessionBuilder:
    def __init__(self) -> None:
        self._init_vars()

    def _init_vars(self) -> None:
        self.sold: dict[int, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.bought: dict[int, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.missions: dict[int, Mission] = {}
        self.last_event_at: Optional[datetime] = (
            None  # We see it first when traversing, but it's the last event chronologically
        )

    def observe_event_time(self, timestamp: datetime) -> None:
        if self.last_event_at is None:
            self.last_event_at = timestamp

    def sell(self, good: str, count: int, market_id: int = -1) -> None:
        self.sold[market_id][good] += count

    def buy(self, good: str, count: int, market_id: int = -1) -> None:
        self.bought[market_id][good] += count

    def complete_mission(self, mission: Mission) -> None:
        self.missions[mission.mission_id] = mission

    def build(self, started_at: datetime) -> CargoSession:
        instance = CargoSession(
            started_at=started_at,
            ended_at=self.last_event_at or started_at,
            bought=dict(self.bought),
            sold=dict(self.sold),
            missions=self.missions,
        )
        self._init_vars()
        return instance


class VitalsCargoSessionCollector:
    def __init__(self, merges: int = 0) -> None:
        self.markets: dict[int, Market] = {}
        self.session_builder = CargoSessionBuilder()
        self.sessions: list[CargoSession] = []
        self.merges_remain = merges

    def handle_event(self, event: GameEvent) -> None:
        self.session_builder.observe_event_time(event.timestamp)

        if isinstance(event, MarketEvent):
            self.markets[event.market_id] = Market(
                market_id=event.market_id,
                station_name=event.station_name,
                system_name=event.star_system,
                is_carrier=event.station_type == "FleetCarrier",
            )
        elif isinstance(event, LoadGameEvent):
            if self.merges_remain:
                self.merges_remain -= 1
            else:
                self.sessions.append(
                    self.session_builder.build(started_at=event.timestamp)
                )
        elif isinstance(event, MarketSellEvent):
            self.session_builder.sell(
                market_id=event.market_id, good=event.type, count=event.count
            )
        elif isinstance(event, MissionCompletedEvent):
            mission = self._create_mission(event)
            self.session_builder.complete_mission(mission)

    def _create_mission(self, event: MissionCompletedEvent) -> Mission:
        if event.commodity is not None:
            assert (
                event.destination_system is not None
            ), "Commodity mission must have a destination system"
            assert (
                event.commodity_localised is not None
            ), "Commodity mission must have a localised commodity name"
            assert event.count is not None, "Commodity mission must have a count"

            return CargoMission(
                mission_id=event.mission_id,
                title=event.localised_name,
                technical_name=event.name,
                faction=event.faction,
                system=event.destination_system,
                station=event.destination_station,
                effects=self._create_effects(event.faction_effects),
                good=event.commodity_localised,
                count=event.count,
            )
        if event.donated is not None:
            return DonationMission(
                mission_id=event.mission_id,
                title=event.localised_name,
                technical_name=event.name,
                faction=event.faction,
                effects=self._create_effects(event.faction_effects),
                donated=event.donated,
            )
        # Any other mission type
        return GenericMission(
            mission_id=event.mission_id,
            title=event.localised_name,
            technical_name=event.name,
            faction=event.faction,
            system=event.destination_system,
            station=event.destination_station,
            effects=self._create_effects(event.faction_effects),
        )

    def _create_effects(
        self, faction_effects: list[FactionEffectGroup]
    ) -> list[MissionFactionEffect]:
        return [
            MissionFactionEffect(
                faction=feffect.faction,
                effect=effect.effect,
                effect_localised=effect.effect_localised,
                trend=effect.trend,
            )
            for feffect in faction_effects
            for effect in feffect.effects
        ]
