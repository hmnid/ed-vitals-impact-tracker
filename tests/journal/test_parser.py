from datetime import datetime, timezone
import pytest
from trademeds.journal.parser import JournalEventParser
from trademeds.journal.events import (
    LoadGameEvent,
    MarketEvent,
    MarketBuyEvent,
    MarketSellEvent,
    MissionCompletedEvent,
    FactionEffect,
    FactionEffectGroup,
    MissionAcceptedEvent,
    MissionAbandonedEvent,
    CargoDepotEvent,
    CargoDepotUpdateType,
)


class TestJournalParser:
    @pytest.fixture
    def parser(self):
        return JournalEventParser()

    def test_parse_load_game(self, parser):
        raw_event = {
            "timestamp": "2025-02-16T09:25:10Z",
            "event": "LoadGame",
            "FID": "F8508247",
            "Commander": "hmnid",
            "Horizons": True,
            "Odyssey": True,
            "Ship": "Type9",
            "Ship_Localised": "Type-9 Heavy",
            "ShipID": 17,
            "ShipName": "VITALS HELPING STOMP",
            "ShipIdent": "HM-28T",
            "FuelLevel": 57.887512,
            "FuelCapacity": 64.0,
            "GameMode": "Open",
            "Credits": 1883189403,
            "Loan": 0,
            "language": "English/UK",
            "gameversion": "4.0.0.1904",
            "build": "r308767/r0 ",
        }

        expected = LoadGameEvent.model_construct(
            timestamp=datetime(2025, 2, 16, 9, 25, 10, tzinfo=timezone.utc),
            event="LoadGame",
        )

        result = parser.parse(raw_event)
        assert result == expected

    def test_parse_mission_accepted_commodity_gather(self, parser):
        raw_event = {
            "timestamp": "2025-02-14T18:48:59Z",
            "event": "MissionAccepted",
            "Faction": "Terran Colonial Forces",
            "Name": "Mission_Delivery_Confederacy",
            "LocalisedName": "Deliver 36 units of Fish",
            "Commodity": "$Fish_Name;",
            "Commodity_Localised": "Fish",
            "Count": 36,
            "DestinationSystem": "Aknandan",
            "DestinationStation": "Gordon Terminal",
            "Expiry": "2025-02-15T18:48:59Z",
            "Influence": "++",
            "Reputation": "++",
            "MissionID": 1003255884,
        }

        expected = MissionAcceptedEvent.model_construct(
            timestamp=datetime(2025, 2, 14, 18, 48, 59, tzinfo=timezone.utc),
            event="MissionAccepted",
            faction="Terran Colonial Forces",
            name="Mission_Delivery_Confederacy",
            localised_name="Deliver 36 units of Fish",
            commodity="$Fish_Name;",
            commodity_localised="Fish",
            count=36,
            destination_system="Aknandan",
            destination_station="Gordon Terminal",
            expiry=datetime(2025, 2, 15, 18, 48, 59, tzinfo=timezone.utc),
            influence="++",
            reputation="++",
            mission_id=1003255884,
        )

        result = parser.parse(raw_event)
        assert result == expected

    def test_parse_mission_accepted_commodity_source_to_destination(self, parser):
        raw_event = {
            "timestamp": "2025-02-16T09:41:53Z",
            "event": "MissionAccepted",
            "Faction": "Terran Colonial Forces",
            "Name": "Mission_Delivery_Confederacy",
            "LocalisedName": "Support the confederacy by delivering 36 units of Fish",
            "Commodity": "$Fish_Name;",
            "Commodity_Localised": "Fish",
            "Count": 36,
            "TargetFaction": "Starlance Alpha",
            "DestinationSystem": "Aknandan",
            "DestinationStation": "Gordon Terminal",
            "Expiry": "2025-02-17T09:40:38Z",
            "Wing": False,
            "Influence": "++",
            "Reputation": "++",
            "Reward": 1368452,
            "MissionID": 1003484014,
        }

        expected = MissionAcceptedEvent.model_construct(
            timestamp=datetime(2025, 2, 16, 9, 41, 53, tzinfo=timezone.utc),
            event="MissionAccepted",
            faction="Terran Colonial Forces",
            name="Mission_Delivery_Confederacy",
            localised_name="Support the confederacy by delivering 36 units of Fish",
            commodity="$Fish_Name;",
            commodity_localised="Fish",
            count=36,
            target_faction="Starlance Alpha",
            destination_system="Aknandan",
            destination_station="Gordon Terminal",
            expiry=datetime(2025, 2, 17, 9, 40, 38, tzinfo=timezone.utc),
            wing=False,
            influence="++",
            reputation="++",
            reward=1368452,
            mission_id=1003484014,
        )

        result = parser.parse(raw_event)
        assert result == expected

    def test_parse_mission_accepted_donation(self, parser):
        raw_event = {
            "timestamp": "2025-02-16T09:40:48Z",
            "event": "MissionAccepted",
            "Faction": "Terran Colonial Forces",
            "Name": "Mission_AltruismCredits",
            "LocalisedName": "Donate 1,000,000 Cr to the cause",
            "Donation": "1000000",
            "Expiry": "2025-02-16T13:19:32Z",
            "Wing": False,
            "Influence": "++",
            "Reputation": "++",
            "MissionID": 1003483922,
        }

        expected = MissionAcceptedEvent.model_construct(
            timestamp=datetime(2025, 2, 16, 9, 40, 48, tzinfo=timezone.utc),
            event="MissionAccepted",
            faction="Terran Colonial Forces",
            name="Mission_AltruismCredits",
            localised_name="Donate 1,000,000 Cr to the cause",
            donation="1000000",
            expiry=datetime(2025, 2, 16, 13, 19, 32, tzinfo=timezone.utc),
            wing=False,
            influence="++",
            reputation="++",
            mission_id=1003483922,
        )

        result = parser.parse(raw_event)
        assert result == expected

    def test_parse_mission_completed_donation(self, parser):
        raw_event = {
            "timestamp": "2025-02-14T18:48:59Z",
            "event": "MissionCompleted",
            "Faction": "Terran Colonial Forces",
            "Name": "Mission_AltruismCredits_Outbreak_name",
            "LocalisedName": "Donate 300,000 Cr to Prevent a Medical Emergency",
            "MissionID": 1003255884,
            "Donation": "300000",
            "Donated": 300000,
            "FactionEffects": [
                {
                    "Faction": "Terran Colonial Forces",
                    "Effects": [
                        {
                            "Effect": "$MISSIONUTIL_Interaction_Summary_Outbreak_down;",
                            "Effect_Localised": "With fewer reported cases of illness...",
                            "Trend": "DownGood",
                        }
                    ],
                    "Influence": [
                        {
                            "SystemAddress": 9466779215257,
                            "Trend": "UpGood",
                            "Influence": "++",
                        }
                    ],
                    "ReputationTrend": "UpGood",
                    "Reputation": "+",
                }
            ],
        }

        expected = MissionCompletedEvent.model_construct(
            timestamp=datetime(2025, 2, 14, 18, 48, 59, tzinfo=timezone.utc),
            event="MissionCompleted",
            faction="Terran Colonial Forces",
            name="Mission_AltruismCredits_Outbreak_name",
            localised_name="Donate 300,000 Cr to Prevent a Medical Emergency",
            mission_id=1003255884,
            donation="300000",
            donated=300000,
            faction_effects=[
                FactionEffectGroup.model_construct(
                    faction="Terran Colonial Forces",
                    effects=[
                        FactionEffect.model_construct(
                            effect="$MISSIONUTIL_Interaction_Summary_Outbreak_down;",
                            effect_localised="With fewer reported cases of illness...",
                            trend="DownGood",
                        )
                    ],
                    influence=[
                        {
                            "SystemAddress": 9466779215257,
                            "Trend": "UpGood",
                            "Influence": "++",
                        }
                    ],
                    reputation_trend="UpGood",
                    reputation="+",
                )
            ],
        )

        result = parser.parse(raw_event)
        assert result == expected

    def test_parse_mission_completed_commodity(self, parser):
        raw_event = {
            "timestamp": "2025-02-16T10:12:32Z",
            "event": "MissionCompleted",
            "Faction": "Terran Colonial Forces",
            "Name": "Mission_Delivery_Confederacy_name",
            "LocalisedName": "Support the confederacy by delivering 36 units of Fish",
            "MissionID": 1003484014,
            "Commodity": "$Fish_Name;",
            "Commodity_Localised": "Fish",
            "Count": 36,
            "TargetFaction": "Starlance Alpha",
            "DestinationSystem": "Aknandan",
            "DestinationStation": "Gordon Terminal",
            "Reward": 194465,
            "FactionEffects": [
                {
                    "Faction": "Starlance Alpha",
                    "Effects": [
                        {
                            "Effect": "$MISSIONUTIL_Interaction_Summary_EP_up;",
                            "Effect_Localised": "The economic status of $#MinorFaction; has improved in the $#System; system.",
                            "Trend": "UpGood",
                        }
                    ],
                    "Influence": [
                        {
                            "SystemAddress": 2869978015193,
                            "Trend": "UpGood",
                            "Influence": "++",
                        }
                    ],
                    "ReputationTrend": "UpGood",
                    "Reputation": "+++++",
                },
                {
                    "Faction": "Terran Colonial Forces",
                    "Effects": [
                        {
                            "Effect": "$MISSIONUTIL_Interaction_Summary_EP_up;",
                            "Effect_Localised": "The economic status of $#MinorFaction; has improved in the $#System; system.",
                            "Trend": "UpGood",
                        }
                    ],
                    "Influence": [
                        {
                            "SystemAddress": 9466779215257,
                            "Trend": "UpGood",
                            "Influence": "++",
                        }
                    ],
                    "ReputationTrend": "UpGood",
                    "Reputation": "+++++",
                },
            ],
        }

        expected = MissionCompletedEvent.model_construct(
            timestamp=datetime(2025, 2, 16, 10, 12, 32, tzinfo=timezone.utc),
            event="MissionCompleted",
            faction="Terran Colonial Forces",
            name="Mission_Delivery_Confederacy_name",
            localised_name="Support the confederacy by delivering 36 units of Fish",
            mission_id=1003484014,
            commodity="$Fish_Name;",
            commodity_localised="Fish",
            count=36,
            target_faction="Starlance Alpha",
            destination_system="Aknandan",
            destination_station="Gordon Terminal",
            reward=194465,
            faction_effects=[
                FactionEffectGroup.model_construct(
                    faction="Starlance Alpha",
                    effects=[
                        FactionEffect.model_construct(
                            effect="$MISSIONUTIL_Interaction_Summary_EP_up;",
                            effect_localised="The economic status of $#MinorFaction; has improved in the $#System; system.",
                            trend="UpGood",
                        )
                    ],
                    influence=[
                        {
                            "SystemAddress": 2869978015193,
                            "Trend": "UpGood",
                            "Influence": "++",
                        }
                    ],
                    reputation_trend="UpGood",
                    reputation="+++++",
                ),
                FactionEffectGroup.model_construct(
                    faction="Terran Colonial Forces",
                    effects=[
                        FactionEffect.model_construct(
                            effect="$MISSIONUTIL_Interaction_Summary_EP_up;",
                            effect_localised="The economic status of $#MinorFaction; has improved in the $#System; system.",
                            trend="UpGood",
                        )
                    ],
                    influence=[
                        {
                            "SystemAddress": 9466779215257,
                            "Trend": "UpGood",
                            "Influence": "++",
                        }
                    ],
                    reputation_trend="UpGood",
                    reputation="+++++",
                ),
            ],
        )

        result = parser.parse(raw_event)
        assert result == expected

    def test_parse_market(self, parser):
        raw_event = {
            "timestamp": "2025-02-15T23:58:41Z",
            "event": "Market",
            "MarketID": 3228170496,
            "StationName": "Houssay Ring",
            "StationType": "Orbis",
            "StarSystem": "Sudz",
        }

        expected = MarketEvent.model_construct(
            timestamp=datetime(2025, 2, 15, 23, 58, 41, tzinfo=timezone.utc),
            event="Market",
            market_id=3228170496,
            station_name="Houssay Ring",
            station_type="Orbis",
            star_system="Sudz",
        )

        result = parser.parse(raw_event)
        assert result == expected

    def test_parse_market_buy(self, parser):
        raw_event = {
            "timestamp": "2025-02-15T23:10:31Z",
            "event": "MarketBuy",
            "MarketID": 3228400128,
            "Type": "performanceenhancers",
            "Type_Localised": "Performance Enhancers",
            "Count": 316,
            "BuyPrice": 5858,
            "TotalCost": 1851128,
        }

        expected = MarketBuyEvent.model_construct(
            timestamp=datetime(2025, 2, 15, 23, 10, 31, tzinfo=timezone.utc),
            event="MarketBuy",
            market_id=3228400128,
            type="performanceenhancers",
            type_localised="Performance Enhancers",
            count=316,
            buy_price=5858,
            total_cost=1851128,
        )

        result = parser.parse(raw_event)
        assert result == expected

    def test_parse_market_sell(self, parser):
        raw_event = {
            "timestamp": "2025-02-15T23:58:52Z",
            "event": "MarketSell",
            "MarketID": 3228170496,
            "Type": "performanceenhancers",
            "Type_Localised": "Performance Enhancers",
            "Count": 316,
            "SellPrice": 7188,
            "TotalSale": 2271408,
            "AvgPricePaid": 5858,
        }

        expected = MarketSellEvent.model_construct(
            timestamp=datetime(2025, 2, 15, 23, 58, 52, tzinfo=timezone.utc),
            event="MarketSell",
            market_id=3228170496,
            type="performanceenhancers",
            type_localised="Performance Enhancers",
            count=316,
            sell_price=7188,
            total_sale=2271408,
            avg_price_paid=5858,
        )

        result = parser.parse(raw_event)
        assert result == expected

    def test_parse_mission_abandoned(self, parser):
        raw_event = {
            "timestamp": "2025-02-16T09:41:07Z",
            "event": "MissionAbandoned",
            "Name": "Mission_Collect_Outbreak_name",
            "LocalisedName": "Outbreak aid needed 45 units of Onionhead Gamma Strain",
            "MissionID": 1003432117
        }

        expected = MissionAbandonedEvent.model_construct(
            timestamp=datetime(2025, 2, 16, 9, 41, 7, tzinfo=timezone.utc),
            event="MissionAbandoned",
            mission_id=1003432117,
            name="Mission_Collect_Outbreak_name",
            localised_name="Outbreak aid needed 45 units of Onionhead Gamma Strain"
        )

        result = parser.parse(raw_event)
        assert result == expected

    def test_unknown_event_returns_none(self, parser):
        raw_event = {
            "timestamp": "2025-02-14T18:32:41Z",
            "event": "UnknownEvent",
            "SomeData": "value",
        }

        result = parser.parse(raw_event)
        assert result is None

    def test_parse_cargo_depot_deliver(self, parser):
        raw_event = {
            "timestamp": "2025-02-14T21:01:48Z",
            "event": "CargoDepot",
            "MissionID": 1003268244,
            "UpdateType": "Deliver",
            "CargoType": "ProgenitorCells",
            "CargoType_Localised": "Progenitor Cells",
            "Count": 740,
            "StartMarketID": 0,
            "EndMarketID": 3228170496,
            "ItemsCollected": 0,
            "ItemsDelivered": 875,
            "TotalItemsToDeliver": 1170,
            "Progress": 0.000000
        }

        expected = CargoDepotEvent.model_construct(
            timestamp=datetime(2025, 2, 14, 21, 1, 48, tzinfo=timezone.utc),
            event="CargoDepot",
            mission_id=1003268244,
            update_type=CargoDepotUpdateType.DELIVER,
            cargo_type="ProgenitorCells",
            cargo_type_localised="Progenitor Cells",
            count=740,
            start_market_id=0,
            end_market_id=3228170496,
            items_collected=0,
            items_delivered=875,
            total_items_to_deliver=1170,
            progress=0.0
        )

        result = parser.parse(raw_event)
        assert result == expected

    def test_parse_cargo_depot_collect(self, parser):
        raw_event = {
            "timestamp": "2025-02-16T09:42:52Z",
            "event": "CargoDepot",
            "MissionID": 1003484014,
            "UpdateType": "Collect",
            "CargoType": "Fish",
            "Count": 36,
            "StartMarketID": 3228170496,
            "EndMarketID": 3544958720,
            "ItemsCollected": 36,
            "ItemsDelivered": 0,
            "TotalItemsToDeliver": 36,
            "Progress": 1.000000
        }

        expected = CargoDepotEvent.model_construct(
            timestamp=datetime(2025, 2, 16, 9, 42, 52, tzinfo=timezone.utc),
            event="CargoDepot",
            mission_id=1003484014,
            update_type=CargoDepotUpdateType.COLLECT,
            cargo_type="Fish",
            cargo_type_localised=None,
            count=36,
            start_market_id=3228170496,
            end_market_id=3544958720,
            items_collected=36,
            items_delivered=0,
            total_items_to_deliver=36,
            progress=1.0
        )

        result = parser.parse(raw_event)
        assert result == expected
