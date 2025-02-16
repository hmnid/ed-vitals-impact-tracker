import os
import argparse
from .journal import JournalEventTraverser
from .observers.cargo import VitalsCargoSessionCollector
from .viewers.session import SessionView

journal_path = os.path.join(
    os.environ["USERPROFILE"], "Saved Games\\Frontier Developments\\Elite Dangerous\\"
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Process Elite Dangerous sessions.")
    parser.add_argument(
        "--sessions",
        type=int,
        default=5,
        help="Number of game sessions to process (each session starts when you log into the game world / LoadGame event)",
    )
    parser.add_argument(
        "--merges",
        type=int,
        default=0,
        help="Number of sessions to combine into one (useful when you have relogged during a vitals run for some reason)",
    )
    args = parser.parse_args()

    # Setup components
    traverser = JournalEventTraverser(journal_path)
    collector = VitalsCargoSessionCollector(merges=args.merges)
    traverser.add_observer(collector)

    # Collect data
    traverser.traverse(max_sessions=args.sessions)

    # Display results
    view = SessionView(collector.markets)
    view.display_sessions(collector.sessions[: args.sessions])


if __name__ == "__main__":
    main()
