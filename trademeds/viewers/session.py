from ..models.entities import Market, CargoSession, CargoMission, DonationMission

def localise_mission_faction_effect(t):
    if t == '$MISSIONUTIL_Interaction_Summary_Outbreak_down;':
        return 'OUTBREAK_DOWN'
    if t == '$MISSIONUTIL_Interaction_Summary_EP_up;':
        return 'ECONOMY_POWER_UP'
    if t == '$MISSIONUTIL_Interaction_Summary_SP_up;':
        return 'SECURITY_UP'
    return t

def missions_repr(missions):
    from collections import defaultdict
    from dataclasses import dataclass, field

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
    
    for mission in missions:
        summary = type_to_summary[type(mission)]()
        summary.count += 1
        
        for effect in mission.effects:
            effect_name = localise_mission_faction_effect(effect.effect_localised)
            if effect.faction == mission.faction:
                summary.effects[effect_name] += 1
            else:
                summary.aux_effects[effect.faction][effect_name] += 1

        if isinstance(mission, CargoMission):
            summary.goods[mission.good] += mission.count
        elif isinstance(mission, DonationMission):
            summary.donated += mission.donated

        aggr[mission.mission_id][type(mission)] = summary

    for mission_id, summaries in aggr.items():
        print(f'Mission {mission_id}:')
        for summary_type, summary in summaries.items():
            print(f'    {summary_type.__name__}:')
            print(f'        count: {summary.count}')
            
            if summary.effects:
                print('        effects:')
                for effect, count in summary.effects.items():
                    print(f'            {effect}: {count}')
            
            if summary.aux_effects:
                print('        aux effects:')
                for faction, effects in summary.aux_effects.items():
                    print(f'            {faction}:')
                    for effect, count in effects.items():
                        print(f'                {effect}: {count}')
            
            if isinstance(summary, CargoMissionSummary) and summary.goods:
                print('        goods:')
                for good, count in summary.goods.items():
                    print(f'            {good}: {count}')
            
            if isinstance(summary, DonationMissionSummary) and summary.donated:
                print(f'        donated: {summary.donated}')

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
        missions_repr(session.missions) 