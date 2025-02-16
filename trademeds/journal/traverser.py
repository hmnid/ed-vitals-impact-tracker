import os
import json
from typing import Optional
from .parser import JournalEventParser
from .events import GameEvent


class JournalEventTraverser:
    def __init__(self, journal_path: str):
        self.journal_path = journal_path
        self.observers = []
        self.parser = JournalEventParser()

    def add_observer(self, observer):
        self.observers.append(observer)

    def traverse(self, max_sessions: int = 5):
        sessions_found = 0

        for dr in sorted(os.listdir(self.journal_path), reverse=True):
            if not dr.startswith("Journal."):
                continue

            if sessions_found >= max_sessions:
                break

            with open(os.path.join(self.journal_path, dr)) as f:
                for line in reversed(f.readlines()):
                    raw_event = json.loads(line.strip())

                    parsed_event = self.parser.parse(raw_event)
                    if parsed_event:
                        if parsed_event.event == "LoadGame":
                            sessions_found += 1

                        for observer in self.observers:
                            observer.handle_event(parsed_event)
