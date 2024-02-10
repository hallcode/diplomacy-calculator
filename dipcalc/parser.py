from dataclasses import dataclass
from enum import Enum, auto


class UnitType(Enum):
    ARMY = "A"
    FLEET = "F"


class OrderStatus(Enum):
    UNDECIDED = auto()
    INFINITE_DEPS = auto()
    INVALID = auto()
    FAILED = auto()
    SUCCEEDED = auto()


class OrderType(Enum):
    ATTACK = "A"
    SUPPORT = "S"
    HOLD = "H"
    CONVOY = "C"


@dataclass
class Faction:
    code: str
    name: str
    capitals_held: int = 0
    total_units: int = 0


@dataclass
class Territory:
    code: str
    name: str
    armies: bool
    fleets: bool
    capital: bool = False
    parent: str = None
    strength: int = 0


@dataclass
class Order:
    faction: Faction
    unit: UnitType
    territory: Territory
    type: OrderType
    target: list[Territory]
    status: OrderStatus = OrderStatus.UNDECIDED
    strength: int = 0
