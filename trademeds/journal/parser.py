from typing import Dict, Type, Optional, Any
from .events import (
    GameEvent,
    LoadGameEvent,
    MissionAcceptedEvent,
    MissionCompletedEvent,
    MissionAbandonedEvent,
    MarketEvent,
    MarketBuyEvent,
    MarketSellEvent,
    CargoDepotEvent,
)


class JournalEventParser:
    def __init__(self) -> None:
        self._event_parsers: Dict[str, Type[GameEvent]] = {
            "LoadGame": LoadGameEvent,
            "MissionAccepted": MissionAcceptedEvent,
            "MissionCompleted": MissionCompletedEvent,
            "MissionAbandoned": MissionAbandonedEvent,
            "Market": MarketEvent,
            "MarketBuy": MarketBuyEvent,
            "MarketSell": MarketSellEvent,
            "CargoDepot": CargoDepotEvent,
        }

    def parse(self, raw_event: dict) -> Optional[GameEvent]:
        event_type = raw_event["event"]
        if event_type not in self._event_parsers:
            return None

        event_class = self._event_parsers[event_type]
        return event_class.model_validate(raw_event)
