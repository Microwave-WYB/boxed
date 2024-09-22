from abc import ABC
from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps
from re import T
from typing import Optional

from boxed.error import UnwrapError


class Option[T](ABC):
    """
    Option[T] represents an optional value.
    Every Option is either Some and contains a value of type T, or Null.

    Examples
    --------
    >>> Option.from_(1)
    Some(1)
    >>> Option.from_(None)
    Null()
    >>> Some(1).unwrap()
    1
    >>> Null().unwrap()
    Traceback (most recent call last):
        ...
    boxed.error.UnwrapError
    >>> Some(1).unwrap_or(2)
    1
    >>> Null().unwrap_or(2)
    2
    >>> Some(1).unwrap_or_else(lambda: 2)
    1
    >>> Null().unwrap_or_else(lambda: 2)
    2
    """

    def __init__(self, value: Optional[T]) -> None:
        self.value = value

    @staticmethod
    def from_(value: Optional[T]) -> "Option[T]":
        """
        >>> Option.from_(1)
        Some(1)
        >>> Option.from_(None)
        Null()
        """
        match value:
            case None:
                return Null()
            case _:
                return Some(value)

    def unwrap(self) -> T:
        """
        >>> Some(1).unwrap()
        1
        >>> Null().unwrap()
        Traceback (most recent call last):
            ...
        boxed.error.UnwrapError
        """
        match self.value:
            case None:
                raise UnwrapError
            case _:
                return self.value

    def unwrap_or(self, default: T, /) -> T:
        """
        >>> Some(1).unwrap_or(2)
        1
        >>> Null().unwrap_or(2)
        2
        """
        match self.value:
            case None:
                return default
            case _:
                return self.value

    def unwrap_or_else(self, f: Callable[[], T], /) -> T:
        """
        >>> Some(1).unwrap_or_else(lambda: 2)
        1
        >>> Null().unwrap_or_else(lambda: 2)
        2
        """
        match self.value:
            case None:
                return f()
            case _:
                return self.value

    def expect(self, msg: str, /) -> T:
        """
        >>> Some(1).expect("Error")
        1
        >>> Null().expect("Error")
        Traceback (most recent call last):
            ...
        boxed.error.UnwrapError: Error
        """
        match self.value:
            case None:
                raise UnwrapError(msg)
            case _:
                return self.value

    def is_some(self) -> bool:
        """
        >>> Some(1).is_some()
        True
        >>> Null().is_some()
        False
        """
        return self.value is not None

    def is_none(self) -> bool:
        """
        >>> Some(1).is_none()
        False
        >>> Null().is_none()
        True
        """
        return self.value is None

    def map(self, mapper: Callable[[T], T], /) -> "Option[T]":
        """
        >>> Some(1).map(lambda x: x + 1)
        Some(2)
        >>> Null().map(lambda x: x + 1)
        Null()
        """
        match self.value:
            case None:
                return Null()
            case _:
                return Some(mapper(self.value))

    def and_then[U](self, mapper: Callable[[T], "Option[U]"], /) -> "Option[U]":
        """
        >>> Some(1).and_then(lambda x: Some(x + 1))
        Some(2)
        >>> Some(1).and_then(lambda x: Null())
        Null()
        """
        match self.value:
            case None:
                return Null()
            case _:
                return mapper(self.value)

    def or_(self, optb: "Option[T]", /) -> "Option[T]":
        """
        >>> Some(1).or_(Some(2))
        Some(1)
        >>> Some(1).or_(Null())
        Some(1)
        >>> Null().or_(Some(2))
        Some(2)
        >>> Null().or_(Null())
        Null()
        """
        match self.value:
            case None:
                return optb
            case _:
                return self

    def or_else(self, f: Callable[[], "Option[T]"], /) -> "Option[T]":
        """
        >>> Some(1).or_else(lambda: Null())
        Some(1)
        >>> Null().or_else(lambda: Some(2))
        Some(2)
        """
        match self.value:
            case None:
                return f()
            case _:
                return self

    def __bool__(self) -> bool:
        return self.is_some()

    def __eq__(self, other: object, /) -> bool:
        match self, other:
            case (Some(a), Some(b)):
                return a == b
            case (Null(), Null()):
                return True
            case _:
                return False

    def __repr__(self) -> str:
        match self.value:
            case None:
                return "Null()"
            case _:
                return f"Some({self.value!r})"

    def __or__(self, optb: "Option[T]", /) -> "Option[T]":
        return self.or_(optb)

    def __rshift__[U](self, mapper: Callable[[T], "Option[U]"], /) -> "Option[U]":
        return self.and_then(mapper)


@dataclass
class Some[T](Option[T]):
    value: T

    def __repr__(self) -> str:
        return f"Some({self.value!r})"


class Null[T: None](Option[T]):  # named as `Null` to avoid conflict with `None`
    def __init__(self) -> None:
        super().__init__(None)

    def __repr__(self) -> str:
        return "Null()"


def option[**P, T](f: Callable[P, Optional[T]]) -> Callable[P, Option[T]]:
    """
    Convert a function returning an Optional into an Option

    >>> @option
    ... def parse_int(s: str) -> Optional[int]:
    ...     return int(s) if s.isdigit() else None
    >>> parse_int("123")
    Some(123)
    >>> parse_int("abc")
    Null()
    """

    @wraps(f)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Option[T]:
        value = f(*args, **kwargs)
        return Option.from_(value)

    return wrapper
