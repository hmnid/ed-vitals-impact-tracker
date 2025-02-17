from dataclasses import dataclass
from typing import Dict
from ..journal.observer import JournalObserver
from ..journal.events import (
    GameEvent,
    MissionAcceptedEvent,
    MissionCompletedEvent,
    MissionAbandonedEvent,
    CargoDepotEvent,
    CargoDepotUpdateType,
    LoadGameEvent,
)
from ..models.entities import CargoMission


@dataclass
class IncompleteMission:
    mission_id: int
    good: str
    count: int
    faction: str
    system: str


class IncompleteCargoTracker(JournalObserver):
    def __init__(self, depth: int = 10) -> None:
        self.depth = depth
        self.missions: Dict[int, IncompleteMission] = {}
        self.sessions_seen = 0

    def handle_event(self, event: GameEvent) -> None:
        if isinstance(event, LoadGameEvent):
            self.sessions_seen += 1

        if self.sessions_seen >= self.depth:
            return

        if isinstance(event, MissionAcceptedEvent):
            if event.commodity is not None:
                assert (
                    event.destination_system is not None
                ), "Cargo mission must have a destination"
                assert (
                    event.commodity_localised is not None
                ), "Cargo mission must have a commodity name"
                assert event.count is not None, "Cargo mission must have a count"

                self.missions[event.mission_id] = IncompleteMission(
                    mission_id=event.mission_id,
                    good=event.commodity_localised,
                    count=event.count,
                    faction=event.faction,
                    system=event.destination_system,
                )
        elif isinstance(event, (MissionCompletedEvent, MissionAbandonedEvent)):
            self.missions.pop(event.mission_id, None)
        elif isinstance(event, CargoDepotEvent):
            if event.update_type == CargoDepotUpdateType.DELIVER:
                mission = self.missions.get(event.mission_id)
                if mission:
                    remaining = event.total_items_to_deliver - event.items_delivered
                    if remaining > 0:
                        mission.count = remaining
                    else:
                        self.missions.pop(event.mission_id)
