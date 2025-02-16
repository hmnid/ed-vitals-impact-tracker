import os
import argparse
from .observers.base import JournalEventTraverser
from .observers.cargo import VitalsCargoSessionCollector
from .viewers.session import SessionView

journal_path = os.path.join(os.environ['USERPROFILE'], 'Saved Games\\Frontier Developments\\Elite Dangerous\\')

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