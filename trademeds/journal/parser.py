from dataclasses import fields
from datetime import datetime
from typing import Dict, Type, Optional, Any
from .events import (
    LoadGameEvent,
    MissionAcceptedEvent,
    MissionCompletedEvent,
    MarketEvent,
    MarketBuyEvent,
    MarketSellEvent,
    FactionEffect,
    FactionEffectGroup
)

class JournalEventParser:
    def __init__(self):
        self._event_parsers: Dict[str, Type] = {
            'LoadGame': LoadGameEvent,
            'MissionAccepted': MissionAcceptedEvent,
            'MissionCompleted': MissionCompletedEvent,
            'Market': MarketEvent,
            'MarketBuy': MarketBuyEvent,
            'MarketSell': MarketSellEvent,
        }
        
        self._field_mapping = {
            'Commander': 'commander',
            'Ship': 'ship',
            'Ship_Localised': 'ship_localised',
            'ShipID': 'ship_id',
            'ShipName': 'ship_name',
            'ShipIdent': 'ship_ident',
            'GameMode': 'game_mode',
            'Credits': 'credits',
            'MarketID': 'market_id',
            'MissionID': 'mission_id',
            'Type': 'type',
            'Type_Localised': 'type_localised',
            'Count': 'count',
            'SellPrice': 'sell_price',
            'TotalSale': 'total_sale',
            'AvgPricePaid': 'avg_price_paid',
            'LocalisedName': 'localised_name',
            'Name': 'name',
            'Faction': 'faction',
            'Donation': 'donation',
            'Donated': 'donated',
            'FactionEffects': 'faction_effects',
            'Commodity': 'commodity',
            'Commodity_Localised': 'commodity_localised',
            'TargetFaction': 'target_faction',
            'DestinationSystem': 'destination_system',
            'DestinationStation': 'destination_station',
            'Reward': 'reward',
            'Wing': 'wing',
            'Expiry': 'expiry',
            'StationName': 'station_name',
            'StationType': 'station_type',
            'StarSystem': 'star_system',
            'BuyPrice': 'buy_price',
            'TotalCost': 'total_cost',
        }

    def parse(self, raw_event: dict) -> Optional[Any]:
        event_type = raw_event['event']
        if event_type not in self._event_parsers:
            return None

        # Make a copy to avoid modifying the input
        event_data = raw_event.copy()
        # Convert timestamps
        for field in ['timestamp', 'Expiry']:
            if field in event_data:
                event_data[field] = datetime.fromisoformat(event_data[field].replace('Z', '+00:00'))

        # Special handling for complex events
        if event_type == 'MissionCompleted':
            event_data = self._parse_mission_completed(event_data)

        # Map field names to Python convention
        mapped_field_name = self._map_field_names(event_data)
        
        # Get only the fields that are defined in the dataclass
        event_class = self._event_parsers[event_type]
        valid_fields = {field.name for field in fields(event_class)}
        filtered_data = {
            key: value for key, value in mapped_field_name.items()
            if key in valid_fields
        }
        
        return event_class(**filtered_data)

    def _parse_mission_completed(self, event_data: dict) -> dict:
        faction_effects = []
        for fe in event_data['FactionEffects']:
            effects = [
                FactionEffect(
                    effect=e['Effect'],
                    effect_localised=e['Effect_Localised'],
                    trend=e['Trend']
                )
                for e in fe['Effects']
            ]
            faction_effects.append(FactionEffectGroup(
                faction=fe['Faction'],
                effects=effects,
                influence=fe['Influence'],
                reputation_trend=fe['ReputationTrend'],
                reputation=fe['Reputation']
            ))
        event_data['faction_effects'] = faction_effects
        del event_data['FactionEffects']
        return event_data

    def _map_field_names(self, data: dict) -> dict:
        return {
            self._field_mapping.get(key, key.lower()): value 
            for key, value in data.items()
        } 