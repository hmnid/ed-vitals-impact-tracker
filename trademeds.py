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


def session_repr(session: CargoSession, markets: dict[int, Market]):
    print(f'VITAL Session {session.started_at.isoformat()}')
    if session.sold:
        for market_id, goods in session.sold.items():
            market = markets[market_id]
            market_name = market.station_name
            system_name = market.system_name
            location = f'Carrier {market_name}' if market.is_carrier else f'{system_name} > {market_name}'
            print(f'    MarketSell at {location}:')

            total = 0
            for good, count in goods.items():
                total += count
                print(f'        {good}: {count}')
            print(' ' * 8 + f'total: {total}')

    if session.missions:
        print(f'    Missions:')
        if True:
            missions_repr(session.missions)
        else:
            missions_summary = defaultdict(lambda: {'amount': 0, 'count': 0, 'effects': defaultdict(lambda:defaultdict(int))})
            for mission in session.missions.values():
                mission_type = mission.technical_name
                if isinstance(mission, CargoMission):
                    mission_type = f'{mission_type} x {mission.good}'
                    missions_summary[mission_type]['amount'] += mission.count
                else:
                    missions_summary[mission_type]['amount'] += mission.donated

                missions_summary[mission_type]['count'] += 1
                for e in mission.effects:
                    missions_summary[mission_type]['effects'][e.faction][e.effect] += 1

            for mission_type, desc in missions_summary.items():
                print(f'        {mission_type} | Amount: {desc['amount']}; Missions: {desc['count']}; Effects:')
                for faction, effects in desc['effects'].items():
                    faction_effects = '; '.join([f'{localise_mission_faction_effect(effect)} x {count}' for effect, count in effects.items()])
                    print(f'            {faction}: {faction_effects}')

def main():
    parser = argparse.ArgumentParser(description="Обработка сессий.")
    
    parser.add_argument('--sessions', type=int, default=5, help='Количество сессий для просмотра')
    parser.add_argument('--merges', type=int, default=0, help='Количество сессий для слияния')
    
    args = parser.parse_args()

    markets: dict[int, Market] = {}
    sessions = []
    market_operations = CargoSessionBuilder()
    carriers = (3703579136,)
    supercruise_drops = []
    maxsessions = args.sessions
    merges_remain = args.merges

    for dr in sorted(os.listdir(journal_path), reverse=True):
        if not dr.startswith('Journal.'):
            continue

        if len(sessions) > maxsessions:
            break

        with open(os.path.join(journal_path, dr)) as f:
            for line in reversed(f.readlines()):
                data = json.loads(line.strip())
                if data['event'] == 'Market':
                    markets[data['MarketID']] = Market(
                        market_id=data['MarketID'],
                        station_name=data['StationName'],
                        system_name=data['StarSystem'],
                        is_carrier=data['StationType'] == 'FleetCarrier'
                    )
                if data['event'] == 'LoadGame':
                    if merges_remain:
                        merges_remain -= 1
                    else:
                        started_at = datetime.fromisoformat(data['timestamp'])
                        sessions.append(market_operations.build(started_at=started_at))
                if data['event'] == 'MarketSell':
                    market_id = data['MarketID']
                    market_operations.sell(market_id=market_id, good=data['Type'], count=data['Count'])
                if data['event'] == 'MissionCompleted':
                    mission = None
                    if 'Commodity' in data:
                        mission = CargoMission(
                            mission_id=data['MissionID'],
                            title=data['LocalisedName'],
                            technical_name=data['Name'],
                            faction=data['Faction'],
                            system=data['DestinationSystem'],
                            station=data.get('DestinationStation'),
                            effects=[
                                MissionFactionEffect(
                                    faction=feffect['Faction'],
                                    effect=effect['Effect'],
                                    effect_localised=effect['Effect_Localised'],
                                    trend=effect['Trend'],
                                )
                                for feffect in data['FactionEffects'] for effect in feffect['Effects']
                            ],
                            good=data['Commodity_Localised'],
                            count=data['Count'],
                        )
                    if 'Donated' in data:
                        mission = DonationMission(
                            mission_id=data['MissionID'],
                            title=data['LocalisedName'],
                            technical_name=data['Name'],
                            faction=data['Faction'],
                            effects=[
                                MissionFactionEffect(
                                    faction=feffect['Faction'],
                                    effect=effect['Effect'],
                                    effect_localised=effect['Effect_Localised'],
                                    trend=effect['Trend'],
                                )
                                for feffect in data['FactionEffects'] for effect in feffect['Effects']
                            ],
                            donated=data['Donated'],
                        )

                    if mission:
                        market_operations.complete_mission(mission)

    sessions = sessions[:maxsessions]

    for session in sessions:
        session_repr(session, markets=markets)
        print('')

if __name__ == "__main__":
    main()
