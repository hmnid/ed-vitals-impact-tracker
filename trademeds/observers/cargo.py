from collections import defaultdict
from datetime import datetime
from ..models.entities import (
    Market, 
    CargoMission, 
    DonationMission, 
    Mission, 
    MissionFactionEffect, 
    CargoSession
)
from ..journal.events import (
    MarketEvent,
    MarketSellEvent,
    MissionCompletedEvent,
    LoadGameEvent
)

class CargoSessionBuilder:
    def __init__(self):
        self._init_vars()

    def _init_vars(self):
        self.sold = defaultdict(lambda: defaultdict(int))
        self.bought = defaultdict(lambda: defaultdict(int))
        self.missions = {}
        self.last_event_at = None  # This is chronologically the last event in the session

    def observe_event_time(self, timestamp: datetime) -> None:
        if self.last_event_at is None:  # We see it first when traversing, but it's the last event chronologically
            self.last_event_at = timestamp

    def sell(self, good: str, count: int, market_id: int = -1) -> None:
        self.sold[market_id][good] += count

    def buy(self, good: str, count: int, market_id: int = -1) -> None:
        self.bought[market_id][good] += count

    def complete_mission(self, mission: CargoMission) -> None:
        self.missions[mission.mission_id] = mission

    def build(self, started_at: datetime) -> CargoSession:
        instance = CargoSession(
            started_at=started_at,  # From LoadGame event
            ended_at=self.last_event_at or started_at,  # Chronologically last event
            bought=self.bought,
            sold=self.sold,
            missions=self.missions,
        )
        self._init_vars()
        return instance

class VitalsCargoSessionCollector:
    def __init__(self, merges: int = 0):
        self.markets: dict[int, Market] = {}
        self.session_builder = CargoSessionBuilder()
        self.sessions: list[CargoSession] = []
        self.merges_remain = merges

    def handle_event(self, event):
        # All events have timestamp as datetime
        self.session_builder.observe_event_time(event.timestamp)

        if isinstance(event, MarketEvent):
            self.markets[event.market_id] = Market(
                market_id=event.market_id,
                station_name=event.station_name,
                system_name=event.star_system,
                is_carrier=event.station_type == 'FleetCarrier'
            )
        elif isinstance(event, LoadGameEvent):
            if self.merges_remain:
                self.merges_remain -= 1
            else:
                self.sessions.append(self.session_builder.build(started_at=event.timestamp))
        elif isinstance(event, MarketSellEvent):
            self.session_builder.sell(
                market_id=event.market_id,
                good=event.type,
                count=event.count
            )
        elif isinstance(event, MissionCompletedEvent):
            mission = self._create_mission(event)
            if mission:
                self.session_builder.complete_mission(mission)

    def _create_mission(self, event: MissionCompletedEvent) -> Mission | None:
        if event.commodity is not None:  # Check if it's a commodity mission
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
        if event.donated is not None:  # Check if it's a donation mission
            return DonationMission(
                mission_id=event.mission_id,
                title=event.localised_name,
                technical_name=event.name,
                faction=event.faction,
                effects=self._create_effects(event.faction_effects),
                donated=event.donated,
            )
        return None

    def _create_effects(self, faction_effects) -> list[MissionFactionEffect]:
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