import os
import argparse
from .journal import JournalEventTraverser
from .observers.cargo import VitalsCargoSessionCollector
from .observers.incomplete_cargo import IncompleteCargoTracker
from .viewers.session import SessionView

journal_path = os.path.join(
    os.environ["USERPROFILE"], "Saved Games\\Frontier Developments\\Elite Dangerous\\"
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Process Elite Dangerous sessions.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Session summary command
    sessions_parser = subparsers.add_parser("sessions", help="Show session summary")
    sessions_parser.add_argument(
        "--sessions",
        type=int,
        default=5,
        help="Number of game sessions to process (each session starts when you log into the game world / LoadGame event)",
    )
    sessions_parser.add_argument(
        "--merges",
        type=int,
        default=0,
        help="Number of sessions to combine into one (useful when you need to relog during a trading run)",
    )

    # Incomplete cargo command
    pending_cargo_parser = subparsers.add_parser("pending-cargo", help="Show incomplete cargo missions")
    pending_cargo_parser.add_argument(
        "--depth",
        type=int,
        default=10,
        help="Number of recent sessions to analyze",
    )

    args = parser.parse_args()

    if args.command == "sessions":
        show_sessions(args.sessions, args.merges)
    elif args.command == "pending-cargo":
        show_incomplete_cargo(args.depth)


def show_sessions(sessions: int, merges: int) -> None:
    traverser = JournalEventTraverser(journal_path)
    collector = VitalsCargoSessionCollector(merges=merges)
    traverser.add_observer(collector)

    traverser.traverse(max_sessions=sessions)

    view = SessionView(collector.markets)
    view.display_sessions(collector.sessions[:sessions])


def show_incomplete_cargo(depth: int) -> None:
    traverser = JournalEventTraverser(journal_path)
    collector = IncompleteCargoTracker(depth=depth)
    traverser.add_observer(collector)

    traverser.traverse(max_sessions=depth)

    # TODO: Add proper viewer for incomplete cargo
    for mission in collector.missions.values():
        print(f"{mission.good}: {mission.count} remaining (to {mission.system} for {mission.faction})")
