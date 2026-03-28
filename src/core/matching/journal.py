"""
Herald Crypto Exchange - Command Journal

Append-only sequenced command journal for deterministic replay.
All accepted stateful trading commands are journaled before execution (HC-002).
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import List, Optional, Dict, Any, Iterator
from uuid import UUID, uuid4


class CommandType(Enum):
    PLACE_ORDER = auto()
    CANCEL_ORDER = auto()
    MODIFY_ORDER = auto()
    MASS_CANCEL = auto()


@dataclass(frozen=True)
class JournalEntry:
    """An immutable, sequenced journal entry for replay."""
    sequence_number: int
    command_type: CommandType
    timestamp: datetime
    payload: Dict[str, Any]
    entry_id: UUID = field(default_factory=uuid4)
    shard_id: str = ""
    checksum: str = ""


class CommandJournal:
    """
    Append-only command journal for a matching engine shard.

    Hard Constraints:
    - HC-002: All accepted commands sequenced and replayable
    """

    def __init__(self, shard_id: str):
        self.shard_id = shard_id
        self._entries: List[JournalEntry] = []
        self._sequence: int = 0
        self._snapshots: List[int] = []

    def append(self, command_type: CommandType, payload: Dict[str, Any]) -> JournalEntry:
        self._sequence += 1
        entry = JournalEntry(
            sequence_number=self._sequence,
            command_type=command_type,
            timestamp=datetime.utcnow(),
            payload=payload,
            shard_id=self.shard_id,
        )
        self._entries.append(entry)
        return entry

    def replay_from(self, sequence_number: int) -> Iterator[JournalEntry]:
        for entry in self._entries:
            if entry.sequence_number >= sequence_number:
                yield entry

    def get_entry(self, sequence_number: int) -> Optional[JournalEntry]:
        for entry in self._entries:
            if entry.sequence_number == sequence_number:
                return entry
        return None

    def mark_snapshot(self) -> int:
        self._snapshots.append(self._sequence)
        return self._sequence

    def latest_snapshot(self) -> Optional[int]:
        return self._snapshots[-1] if self._snapshots else None

    @property
    def current_sequence(self) -> int:
        return self._sequence

    @property
    def entry_count(self) -> int:
        return len(self._entries)
