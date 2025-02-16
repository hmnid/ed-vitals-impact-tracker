import os
import json
from datetime import datetime

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