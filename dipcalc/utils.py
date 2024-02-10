from enum import Enum

TRUTH_VALUES = (
    "y",
    "Y",
    1,
    "1",
    "yes",
    "YES",
    "Yes",
    "TRUE",
    "true",
    "True",
    "T",
    "t",
    True,
)

FALSE_VALUES = (
    "n",
    "N",
    0,
    "0",
    "",
    None,
    "false",
    "F",
    "f",
    False,
    "False",
    "FALSE",
    "no",
    "NO",
    "No",
)

PLACEMENT_REGEX = r"^(\w{2})\s+([fFaA])\s+(\w+)$"
ORDER_REGEX = r"^(\w{2})\s+(\w+)\s+([mascMASC])\s*:\s+((?:\s*[\w]+){1,2})$"


class Unit(Enum):
    ARMY = "A"
    FLEET = "F"
