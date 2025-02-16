import argparse
import os
import os.path
import json
from functools import partial
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime


dataclass = partial(dataclass, kw_only=True)


journal_path = os.path.join(os.environ['USERPROFILE'], 'Saved Games\\Frontier Developments\\Elite Dangerous\\')


@dataclass
class Market:
    market_id: int
    station_name: str
    system_name: str
    is_carrier: bool


@dataclass
class MissionFactionEffect:
    faction: str
    effect_localised: str
    effect: str
    trend: str


@dataclass
class Mission:
    mission_id: int
    title: str
    technical_name: str
    faction: str
    effects: list = field(default_factory=list)
    complete: bool = False


@dataclass
class CargoMission(Mission):
    good: str
    count: int
    system: str
    station: str | None


@dataclass
class DonationMission(Mission):
    donated: int


@dataclass
class CargoSession:
    started_at: datetime
    sold: dict[int, dict[str, int]]
    bought: dict[int, dict[str, int]]
    missions: dict[int, CargoMission]


class CargoSessionBuilder:
    def __init__(self):
        self.missions: dict[int, dict[str, int]]
        self.sold: dict[int, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.bought: dict[int, dict[str, int]] = defaultdict(lambda: defaultdict(int))
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


def localise_mission_faction_effect(t):
    if t == '$MISSIONUTIL_Interaction_Summary_Outbreak_down;':
        return 'OUTBREAK_DOWN'
    if t == '$MISSIONUTIL_Interaction_Summary_EP_up;':
        return 'ECONOMY_POWER_UP'
    if t == '$MISSIONUTIL_Interaction_Summary_SP_up;':
        return 'SECURITY_UP'
    return t

def trend_to_emoji(t): return ''


def missions_repr(missions):
    MissionType = str

    @dataclass
    class MissionSummary:
        count: int = 0
        effects: dict[str, int] = field(default_factory=lambda: defaultdict(int))
        aux_effects: dict[str, dict[str, int]] = field(default_factory=lambda: defaultdict(lambda: defaultdict(int)))


    @dataclass
    class CargoMissionSummary(MissionSummary):
        goods: dict[str, int] = field(default_factory=lambda: defaultdict(int))


    @dataclass
    class DonationMissionSummary(MissionSummary):
        donated: int = 0

    type_to_summary = {CargoMission: CargoMissionSummary, DonationMission: DonationMissionSummary}
    aggr = defaultdict(dict)
    for mission in missions.values():
        if mission.technical_name not in aggr[mission.faction]:
            aggr[mission.faction][mission.technical_name] = type_to_summary[type(mission)]()

        mtype_aggr = aggr[mission.faction][mission.technical_name]
        mtype_aggr.count += 1
        if isinstance(mission, CargoMission):
            mtype_aggr.goods[mission.good] += mission.count
        elif isinstance(mission, DonationMission):
            mtype_aggr.donated += mission.donated
        else:
            raise ValueError('Unknown mission type')

        for faction_effect in mission.effects:
            effect_aggr = mtype_aggr.effects
            if faction_effect.faction != mission.faction:
                effect_aggr = mtype_aggr.aux_effects[faction_effect.faction]

            effect_aggr[faction_effect.effect] += 1

    for faction, mission_types in aggr.items():
        print(' ' * 8 + f'Faction <{faction}>:')
        for mission_type, summary in mission_types.items():
            faction_effects = '; '.join([f'{localise_mission_faction_effect(effect)} x {count}' for effect, count in summary.effects.items()])
            print(' ' * 12 + f'{mission_type} x {summary.count}: {faction_effects}')
            if isinstance(summary, CargoMissionSummary):
                for good, amount in summary.goods.items():
                    print(' ' * 16 + f'{good}: {amount}')
            elif isinstance(summary, DonationMissionSummary):
                print(' ' * 16 + f'Donated: {summary.donated} cr')


class JournalEventTraverser:
    def __init__(self, journal_path: str):
        self.journal_path = journal_path
        self.observers = []

    def add_observer(self, observer):
        self.observers.append(observer)

    def traverse(self, max_sessions: int = 5):
        sessions_found = 0

        for dr in sorted(os.listdir(self.journal_path), reverse=True):
            if not dr.startswith('Journal.'):
                continue

            if sessions_found >= max_sessions:
                break

            with open(os.path.join(self.journal_path, dr)) as f:
                for line in reversed(f.readlines()):
                    event = json.loads(line.strip())
                    event_type = event['event']

                    if event_type == 'LoadGame':
                        sessions_found += 1
                    
                    for observer in self.observers:
                        observer.handle_event(event_type, event)


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


class SessionView:
    def __init__(self, markets: dict[int, Market]):
        self.markets = markets

    def display_sessions(self, sessions: list[CargoSession]):
        for session in sessions:
            self.display_session(session)
            print('')

    def display_session(self, session: CargoSession):
        print(f'VITAL Session {session.started_at.isoformat()}')
        self._display_sales(session)
        self._display_missions(session)

    def _display_sales(self, session: CargoSession):
        if not session.sold:
            return

        for market_id, goods in session.sold.items():
            market = self.markets[market_id]
            market_name = market.station_name
            system_name = market.system_name
            location = f'Carrier {market_name}' if market.is_carrier else f'{system_name} > {market_name}'
            print(f'    MarketSell at {location}:')

            total = 0
            for good, count in goods.items():
                total += count
                print(f'        {good}: {count}')
            print(' ' * 8 + f'total: {total}')

    def _display_missions(self, session: CargoSession):
        if not session.missions:
            return
        print(f'    Missions:')
        missions_repr(session.missions)  # Using existing missions_repr function


def main():
    parser = argparse.ArgumentParser(description="Обработка сессий.")
    parser.add_argument('--sessions', type=int, default=5, help='Количество сессий для просмотра')
    parser.add_argument('--merges', type=int, default=0, help='Количество сессий для слияния')
    args = parser.parse_args()

    # Setup components
    traverser = JournalEventTraverser(journal_path)
    collector = VitalsCargoSessionCollector(merges=args.merges)
    traverser.add_observer(collector)

    # Collect data
    traverser.traverse(max_sessions=args.sessions)

    # Display results
    view = SessionView(collector.markets)
    view.display_sessions(collector.sessions[:args.sessions])

if __name__ == "__main__":
    main()
