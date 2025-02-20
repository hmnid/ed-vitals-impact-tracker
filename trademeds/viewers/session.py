from collections import defaultdict
from dataclasses import dataclass, field
from typing import Type
from ..models.entities import (
    Market,
    CargoSession,
    CargoMission,
    DonationMission,
    Mission,
    GenericMission,
)


class SessionView:
    def __init__(self, markets: dict[int, Market]) -> None:
        self.markets = markets

    def display_sessions(self, sessions: list[CargoSession]) -> None:
        for session in sessions:
            self.display_session(session)
            print("")

    def display_session(self, session: CargoSession) -> None:
        print(
            f"VITAL Session {session.started_at.isoformat()} - {session.ended_at.isoformat()}"
        )
        self._display_sales(session)
        self._display_missions(session)

    def _display_sales(self, session: CargoSession) -> None:
        if not session.sold:
            return

        for market_id, goods in session.sold.items():
            market = self.markets[market_id]
            market_name = market.station_name
            system_name = market.system_name
            location = (
                f"Carrier {market_name}"
                if market.is_carrier
                else f"{system_name} > {market_name}"
            )
            print(f"    MarketSell at {location}:")

            total = 0
            for good, count in goods.items():
                total += count
                print(f"        {good}: {count}")
            print(" " * 8 + f"total: {total}")

    def _display_missions(self, session: CargoSession) -> None:
        if not session.missions:
            return
        print(f"    Missions:")
        self._missions_repr(session.missions)

    def _localise_mission_faction_effect(self, t: str) -> str:
        if t == "$MISSIONUTIL_Interaction_Summary_Outbreak_down;":
            return "OUTBREAK_DOWN"
        if t == "$MISSIONUTIL_Interaction_Summary_EP_up;":
            return "ECONOMY_POWER_UP"
        if t == "$MISSIONUTIL_Interaction_Summary_SP_up;":
            return "SECURITY_UP"
        return t

    def _missions_repr(self, missions: dict[int, Mission]) -> None:
        @dataclass
        class MissionSummary:
            count: int = 0
            effects: dict[str, int] = field(default_factory=lambda: defaultdict(int))
            aux_effects: dict[str, dict[str, int]] = field(
                default_factory=lambda: defaultdict(lambda: defaultdict(int))
            )

        @dataclass
        class CargoMissionSummary(MissionSummary):
            goods: dict[str, int] = field(default_factory=lambda: defaultdict(int))

        @dataclass
        class DonationMissionSummary(MissionSummary):
            donated: int = 0

        @dataclass
        class GenericMissionSummary(MissionSummary):
            pass

        type_to_summary: dict[Type[Mission], Type[MissionSummary]] = {
            CargoMission: CargoMissionSummary,
            DonationMission: DonationMissionSummary,
            GenericMission: GenericMissionSummary,
        }
        aggr: dict[str, dict[str, MissionSummary]] = defaultdict(dict)

        for mission in missions.values():
            if mission.technical_name not in aggr[mission.faction]:
                aggr[mission.faction][mission.technical_name] = type_to_summary[
                    type(mission)
                ]()

            mtype_aggr = aggr[mission.faction][mission.technical_name]
            mtype_aggr.count += 1
            if isinstance(mission, CargoMission):
                assert isinstance(mtype_aggr, CargoMissionSummary)
                mtype_aggr.goods[mission.good] += mission.count
            elif isinstance(mission, DonationMission):
                assert isinstance(mtype_aggr, DonationMissionSummary)
                mtype_aggr.donated += mission.donated
            elif isinstance(mission, GenericMission):
                pass
            else:
                raise ValueError("Unknown mission type")

            for faction_effect in mission.effects:
                effect_aggr = mtype_aggr.effects
                if faction_effect.faction != mission.faction:
                    effect_aggr = mtype_aggr.aux_effects[faction_effect.faction]

                effect_aggr[faction_effect.effect] += 1

        for faction, mission_types in aggr.items():
            print(" " * 8 + f"Faction <{faction}>:")
            for mission_type, summary in mission_types.items():
                faction_effects = "; ".join(
                    [
                        f"{self._localise_mission_faction_effect(effect)} x {count}"
                        for effect, count in summary.effects.items()
                    ]
                )
                print(" " * 12 + f"{mission_type} x {summary.count}: {faction_effects}")
                if isinstance(summary, CargoMissionSummary):
                    for good, amount in summary.goods.items():
                        print(" " * 16 + f"{good}: {amount}")
                elif isinstance(summary, DonationMissionSummary):
                    print(" " * 16 + f"Donated: {summary.donated} cr")
