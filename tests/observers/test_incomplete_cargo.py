from datetime import datetime, timezone
from trademeds.observers.incomplete_cargo import IncompleteCargoTracker
from trademeds.journal.events import (
    MissionAcceptedEvent,
    MissionCompletedEvent,
    MissionAbandonedEvent,
    CargoDepotEvent,
    CargoDepotUpdateType,
    LoadGameEvent,
)


def test_tracks_new_cargo_mission():
    tracker = IncompleteCargoTracker()
    
    tracker.handle_event(make_mission_accepted(123))
    
    assert len(tracker.missions) == 1
    mission = tracker.missions[123]
    assert mission.mission_id == 123
    assert mission.good == "Gold"
    assert mission.count == 100
    assert mission.faction == "Federation"
    assert mission.system == "Sol"


def test_removes_completed_mission():
    tracker = IncompleteCargoTracker()
    
    tracker.handle_event(make_mission_accepted(123))
    assert len(tracker.missions) == 1
    
    tracker.handle_event(make_mission_completed(123))
    assert len(tracker.missions) == 0


def test_removes_abandoned_mission():
    tracker = IncompleteCargoTracker()
    
    tracker.handle_event(make_mission_accepted(123))
    assert len(tracker.missions) == 1
    
    tracker.handle_event(make_mission_abandoned(123))
    assert len(tracker.missions) == 0


def test_updates_remaining_count():
    tracker = IncompleteCargoTracker()
    
    tracker.handle_event(make_mission_accepted(123))
    tracker.handle_event(make_cargo_depot(
        mission_id=123,
        delivered_count=40,
        total_count=100,
    ))
    
    assert tracker.missions[123].count == 60  # 100 - 40 = 60 remaining


def test_removes_fully_delivered_mission():
    tracker = IncompleteCargoTracker()
    
    tracker.handle_event(make_mission_accepted(123))
    assert len(tracker.missions) == 1
    
    tracker.handle_event(make_cargo_depot(
        mission_id=123,
        delivered_count=100,
        total_count=100,
    ))
    assert len(tracker.missions) == 0


def test_ignores_collect_updates():
    tracker = IncompleteCargoTracker()
    
    tracker.handle_event(make_mission_accepted(123, count=50))
    tracker.handle_event(make_cargo_depot(
        mission_id=123,
        delivered_count=0,
        total_count=50,
        update_type=CargoDepotUpdateType.COLLECT,
    ))
    
    assert tracker.missions[123].count == 50  # Count should remain unchanged


def test_respects_session_depth():
    tracker = IncompleteCargoTracker(depth=2)
    
    # Session 3 (most recent) - should be tracked
    tracker.handle_event(make_mission_accepted(125, good="Platinum", count=75))
    tracker.handle_event(make_load_game())
    assert len(tracker.missions) == 1
    
    # Session 2 - should be tracked
    tracker.handle_event(make_mission_accepted(124, good="Silver", count=50))
    tracker.handle_event(make_load_game())
    assert len(tracker.missions) == 2
    
    # Session 1 (oldest) - should not be tracked
    tracker.handle_event(make_mission_accepted(123))
    tracker.handle_event(make_load_game())
    assert len(tracker.missions) == 2  # Still 2, because session 1 is too old


# Test helpers
def make_load_game():
    return LoadGameEvent.model_construct(
        timestamp=datetime.now(timezone.utc),
        event="LoadGame",
    )


def make_mission_accepted(mission_id: int, good: str = "Gold", count: int = 100):
    return MissionAcceptedEvent.model_construct(
        timestamp=datetime.now(timezone.utc),
        event="MissionAccepted",
        mission_id=mission_id,
        name="some_mission",
        localised_name="Some Mission",
        commodity=good,
        commodity_localised=good,
        count=count,
        faction="Federation",
        destination_system="Sol",
    )


def make_mission_completed(mission_id: int):
    return MissionCompletedEvent.model_construct(
        timestamp=datetime.now(timezone.utc),
        event="MissionCompleted",
        mission_id=mission_id,
    )


def make_mission_abandoned(mission_id: int):
    return MissionAbandonedEvent.model_construct(
        timestamp=datetime.now(timezone.utc),
        event="MissionAbandoned",
        mission_id=mission_id,
        name="some_mission",
        localised_name="Some Mission",
    )


def make_cargo_depot(
    mission_id: int,
    delivered_count: int,
    total_count: int,
    update_type: CargoDepotUpdateType = CargoDepotUpdateType.DELIVER,
):
    return CargoDepotEvent.model_construct(
        timestamp=datetime.now(timezone.utc),
        event="CargoDepot",
        mission_id=mission_id,
        update_type=update_type,
        cargo_type="Gold",
        cargo_type_localised="Gold",
        count=delivered_count,  # In a real event this might differ, but for tests it's fine
        start_market_id=1,
        end_market_id=2,
        items_collected=0,
        items_delivered=delivered_count,
        total_items_to_deliver=total_count,
        progress=delivered_count/total_count,
    ) 