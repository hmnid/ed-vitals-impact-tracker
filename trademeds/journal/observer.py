from typing import Protocol
from .events import GameEvent


class JournalObserver(Protocol):
    """Protocol defining the contract for journal event observers.

    Any class that wants to observe journal events must implement this protocol
    by providing a handle_event method that accepts a GameEvent.
    """

    def handle_event(self, event: GameEvent) -> None: ...
