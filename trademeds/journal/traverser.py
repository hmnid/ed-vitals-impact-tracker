import os
import json
from datetime import datetime
from typing import Dict, Type
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

class JournalEventTraverser:
    def __init__(self, journal_path: str):
        self.journal_path = journal_path
        self.observers = []
        self._event_parsers: Dict[str, Type] = {
            'LoadGame': LoadGameEvent,
            'MissionAccepted': MissionAcceptedEvent,
            'MissionCompleted': MissionCompletedEvent,
            'Market': MarketEvent,
            'MarketBuy': MarketBuyEvent,
            'MarketSell': MarketSellEvent,
        }

    def add_observer(self, observer):
        self.observers.append(observer)

    def _parse_event(self, event_type: str, raw_event: dict):
        if event_type not in self._event_parsers:
            return None

        # Convert timestamp string to datetime
        raw_event['timestamp'] = datetime.fromisoformat(raw_event['timestamp'].replace('Z', '+00:00'))

        # Special handling for MissionCompleted event due to nested structure
        if event_type == 'MissionCompleted':
            faction_effects = []
            for fe in raw_event['FactionEffects']:
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
            raw_event['faction_effects'] = faction_effects
            del raw_event['FactionEffects']

        # Convert snake_case field names
        converted_event = {}
        for key, value in raw_event.items():
            snake_key = ''.join(['_' + c.lower() if c.isupper() else c.lower() for c in key]).lstrip('_')
            converted_event[snake_key] = value

        return self._event_parsers[event_type](**converted_event)

    def traverse(self, max_sessions: int = 5):
        sessions_found = 0

        for dr in sorted(os.listdir(self.journal_path), reverse=True):
            if not dr.startswith('Journal.'):
                continue

            if sessions_found >= max_sessions:
                break

            with open(os.path.join(self.journal_path, dr)) as f:
                for line in reversed(f.readlines()):
                    raw_event = json.loads(line.strip())
                    event_type = raw_event['event']
                    
                    parsed_event = self._parse_event(event_type, raw_event)
                    if parsed_event:
                        if isinstance(parsed_event, LoadGameEvent):
                            sessions_found += 1
                        
                        for observer in self.observers:
                            observer.handle_event(parsed_event)