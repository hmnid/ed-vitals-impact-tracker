from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from dataclasses import dataclass, field
from enum import Enum


class GameEvent(BaseModel):
    timestamp: datetime = Field(alias="timestamp")
    event: str = Field(alias="event")


class LoadGameEvent(GameEvent):
    """Represents a new game session start."""

    pass


class FactionEffect(BaseModel):
    effect: str = Field(alias="Effect")
    effect_localised: str = Field(alias="Effect_Localised")
    trend: str = Field(alias="Trend")


class FactionEffectGroup(BaseModel):
    faction: str = Field(alias="Faction")
    effects: List[FactionEffect] = Field(alias="Effects")
    influence: List[dict] = Field(alias="Influence")
    reputation_trend: str = Field(alias="ReputationTrend")
    reputation: str = Field(alias="Reputation")


class MissionAcceptedEvent(GameEvent):
    faction: str = Field(alias="Faction")
    name: str = Field(alias="Name")
    localised_name: str = Field(alias="LocalisedName")
    mission_id: int = Field(alias="MissionID")
    expiry: datetime = Field(alias="Expiry")
    influence: str = Field(alias="Influence")
    reputation: str = Field(alias="Reputation")
    wing: Optional[bool] = Field(None, alias="Wing")
    # Commodity mission fields
    commodity: Optional[str] = Field(None, alias="Commodity")
    commodity_localised: Optional[str] = Field(None, alias="Commodity_Localised")
    count: Optional[int] = Field(None, alias="Count")
    target_faction: Optional[str] = Field(None, alias="TargetFaction")
    destination_system: Optional[str] = Field(None, alias="DestinationSystem")
    destination_station: Optional[str] = Field(None, alias="DestinationStation")
    reward: Optional[int] = Field(None, alias="Reward")
    # Donation mission fields
    donation: Optional[str] = Field(None, alias="Donation")


class MissionCompletedEvent(GameEvent):
    faction: str = Field(alias="Faction")
    name: str = Field(alias="Name")
    localised_name: str = Field(alias="LocalisedName")
    mission_id: int = Field(alias="MissionID")
    faction_effects: List[FactionEffectGroup] = Field(alias="FactionEffects")
    donation: Optional[str] = Field(None, alias="Donation")
    donated: Optional[int] = Field(None, alias="Donated")
    commodity: Optional[str] = Field(None, alias="Commodity")
    commodity_localised: Optional[str] = Field(None, alias="Commodity_Localised")
    count: Optional[int] = Field(None, alias="Count")
    target_faction: Optional[str] = Field(None, alias="TargetFaction")
    destination_system: Optional[str] = Field(None, alias="DestinationSystem")
    destination_station: Optional[str] = Field(None, alias="DestinationStation")
    reward: Optional[int] = Field(None, alias="Reward")


class MarketEvent(GameEvent):
    market_id: int = Field(alias="MarketID")
    station_name: str = Field(alias="StationName")
    station_type: str = Field(alias="StationType")
    star_system: str = Field(alias="StarSystem")


class MarketBuyEvent(GameEvent):
    market_id: int = Field(alias="MarketID")
    type: str = Field(alias="Type")
    type_localised: str | None = Field(
        None, alias="Type_Localised"
    )  # Some commodities like 'tea' or 'coffee' don't have localised names
    count: int = Field(alias="Count")
    buy_price: int = Field(alias="BuyPrice")
    total_cost: int = Field(alias="TotalCost")


class MarketSellEvent(GameEvent):
    market_id: int = Field(alias="MarketID")
    type: str = Field(alias="Type")
    type_localised: str | None = Field(
        None, alias="Type_Localised"
    )  # Keeping this optional as MarketBuyEvent just in case even though I don't know for sure
    count: int = Field(alias="Count")
    sell_price: int = Field(alias="SellPrice")
    total_sale: int = Field(alias="TotalSale")
    avg_price_paid: int = Field(alias="AvgPricePaid")


class MissionAbandonedEvent(GameEvent):
    """Represents a mission being abandoned by the player."""

    mission_id: int = Field(alias="MissionID")
    name: str = Field(alias="Name")
    localised_name: str = Field(alias="LocalisedName")


class CargoDepotUpdateType(Enum):
    DELIVER = "Deliver"
    COLLECT = "Collect"


class CargoDepotEvent(GameEvent):
    """Represents a cargo delivery or collection for a mission."""

    mission_id: int = Field(alias="MissionID")
    update_type: CargoDepotUpdateType = Field(alias="UpdateType")
    cargo_type: str = Field(alias="CargoType")
    cargo_type_localised: str | None = Field(alias="CargoType_Localised", default=None)
    count: int = Field(alias="Count")
    start_market_id: int = Field(alias="StartMarketID")
    end_market_id: int = Field(alias="EndMarketID")
    items_collected: int = Field(alias="ItemsCollected")
    items_delivered: int = Field(alias="ItemsDelivered")
    total_items_to_deliver: int = Field(alias="TotalItemsToDeliver")
    progress: float = Field(alias="Progress")
