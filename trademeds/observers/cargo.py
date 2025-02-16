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

class CargoSessionBuilder:
    def __init__(self):
        self._init_vars()

    def _init_vars(self):
        self.sold = defaultdict(lambda: defaultdict(int))
        self.bought = defaultdict(lambda: defaultdict(int))
        self.missions = {}

    def sell(self, good: str, count: int, market_id: int = -1) -> None:
        self.sold[market_id][good] += count

    def buy(self, good: str, count: int, market_id: int = -1) -> None:
        self.bought[market_id][good] += count

    def complete_mission(self, mission: CargoMission) -> None:
        self.missions[mission.mission_id] = mission

    def build(self, started_at: datetime) -> CargoSession:
        instance = CargoSession(
            started_at=started_at,
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

    def handle_event(self, event_type: str, event: dict):
        if event_type == 'Market':
            self.markets[event['MarketID']] = Market(
                market_id=event['MarketID'],
                station_name=event['StationName'],
                system_name=event['StarSystem'],
                is_carrier=event['StationType'] == 'FleetCarrier'
            )
        elif event_type == 'LoadGame':
            if self.merges_remain:
                self.merges_remain -= 1
            else:
                started_at = datetime.fromisoformat(event['timestamp'])
                self.sessions.append(self.session_builder.build(started_at=started_at))
        elif event_type == 'MarketSell':
            self.session_builder.sell(
                market_id=event['MarketID'],
                good=event['Type'],
                count=event['Count']
            )
        elif event_type == 'MissionCompleted':
            mission = self._create_mission(event)
            if mission:
                self.session_builder.complete_mission(mission)

    def _create_mission(self, event: dict) -> Mission | None:
        if 'Commodity' in event:
            return CargoMission(
                mission_id=event['MissionID'],
                title=event['LocalisedName'],
                technical_name=event['Name'],
                faction=event['Faction'],
                system=event['DestinationSystem'],
                station=event.get('DestinationStation'),
                effects=self._create_effects(event['FactionEffects']),
                good=event['Commodity_Localised'],
                count=event['Count'],
            )
        if 'Donated' in event:
            return DonationMission(
                mission_id=event['MissionID'],
                title=event['LocalisedName'],
                technical_name=event['Name'],
                faction=event['Faction'],
                effects=self._create_effects(event['FactionEffects']),
                donated=event['Donated'],
            )
        return None

    def _create_effects(self, faction_effects: list) -> list[MissionFactionEffect]:
        return [
            MissionFactionEffect(
                faction=feffect['Faction'],
                effect=effect['Effect'],
                effect_localised=effect['Effect_Localised'],
                trend=effect['Trend'],
            )
            for feffect in faction_effects 
            for effect in feffect['Effects']
        ] 