from enum import Enum


class RecordStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    DISCONTINUED = "discontinued"