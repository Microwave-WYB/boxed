from enum import Enum, auto
from typing import Any


class Ordering(Enum):
    Less = auto()
    Equal = auto()
    Greater = auto()


def cmp(a: Any, b: Any) -> Ordering:
    if a < b:
        return Ordering.Less
    elif a > b:
        return Ordering.Greater
    else:
        return Ordering.Equal
