from dataclasses import dataclass
from datetime import datetime
from functools import partial
from typing import List, Optional

# Make all dataclasses keyword-only by default
dataclass = partial(dataclass, kw_only=True)

@dataclass
class GameEvent:
    timestamp: datetime
    event: str

@dataclass
class LoadGameEvent(GameEvent):
    """Represents a new game session start."""
    pass  # Only inherits timestamp and event from GameEvent

@dataclass
class MissionAcceptedEvent(GameEvent):
    faction: str
    name: str
    localised_name: str
    mission_id: int
    expiry: datetime
    influence: str
    reputation: str
    wing: Optional[bool] = None
    # Commodity mission fields
    commodity: Optional[str] = None
    commodity_localised: Optional[str] = None
    count: Optional[int] = None
    target_faction: Optional[str] = None
    destination_system: Optional[str] = None
    destination_station: Optional[str] = None
    reward: Optional[int] = None
    # Donation mission fields
    donation: Optional[str] = None

@dataclass
class FactionEffect:
    effect: str
    effect_localised: str
    trend: str

@dataclass
class FactionEffectGroup:
    faction: str
    effects: List[FactionEffect]
    influence: List[dict]  # Could be further typed if needed
    reputation_trend: str
    reputation: str

@dataclass
class MissionCompletedEvent(GameEvent):
    faction: str
    name: str
    localised_name: str
    mission_id: int
    faction_effects: List[FactionEffectGroup]
    donation: Optional[str] = None
    donated: Optional[int] = None
    commodity: Optional[str] = None
    commodity_localised: Optional[str] = None
    count: Optional[int] = None
    target_faction: Optional[str] = None
    destination_system: Optional[str] = None
    destination_station: Optional[str] = None
    reward: Optional[int] = None

@dataclass
class MarketEvent(GameEvent):
    market_id: int
    station_name: str
    station_type: str
    star_system: str

@dataclass
class MarketBuyEvent(GameEvent):
    market_id: int
    type: str
    type_localised: str
    count: int
    buy_price: int
    total_cost: int

@dataclass
class MarketSellEvent(GameEvent):
    market_id: int
    type: str
    type_localised: str
    count: int
    sell_price: int
    total_sale: int
    avg_price_paid: int 