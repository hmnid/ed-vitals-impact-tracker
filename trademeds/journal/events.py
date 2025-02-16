from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class LoadGameEvent:
    timestamp: datetime
    commander: str
    ship: str
    ship_localised: str
    ship_id: int
    ship_name: str
    ship_ident: str
    credits: int
    game_mode: str

@dataclass
class MissionAcceptedEvent:
    timestamp: datetime
    faction: str
    name: str
    localised_name: str
    commodity: Optional[str]
    commodity_localised: Optional[str]
    count: Optional[int]
    destination_system: str
    destination_station: str
    expiry: datetime
    mission_id: int
    influence: str
    reputation: str

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
class MissionCompletedEvent:
    timestamp: datetime
    faction: str
    name: str
    localised_name: str
    mission_id: int
    donation: Optional[str]
    donated: Optional[int]
    faction_effects: List[FactionEffectGroup]

@dataclass
class MarketEvent:
    timestamp: datetime
    market_id: int
    station_name: str
    station_type: str
    star_system: str

@dataclass
class MarketBuyEvent:
    timestamp: datetime
    market_id: int
    type: str
    type_localised: str
    count: int
    buy_price: int
    total_cost: int

@dataclass
class MarketSellEvent:
    timestamp: datetime
    market_id: int
    type: str
    type_localised: str
    count: int
    sell_price: int
    total_sale: int
    avg_price_paid: int 