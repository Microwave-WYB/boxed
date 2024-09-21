from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps
from re import T
from typing import Optional

from boxed.error import UnwrapError


class _Option[T]:
    def __init__(self, value: Optional[T]) -> None:
        self._value = value

    def unwrap(self) -> T:
        if self._value is None:
            raise UnwrapError
        return self._value

    def unwrap_or(self, default: T, /) -> T:
        if self._value is None:
            return default
        return self._value

    def unwrap_or_else(self, f: Callable[[], T], /) -> T:
        if self._value is None:
            return f()
        return self._value

    def expect(self, msg: str, /) -> T:
        if self._value is None:
            raise UnwrapError(msg)
        return self._value

    def is_some(self) -> bool:
        return self._value is not None

    def is_none(self) -> bool:
        return self._value is None

    def map(self, mapper: Callable[[T], T], /) -> "_Option[T]":
        if self._value is None:
            return Null()
        return Some(mapper(self._value))

    def and_then[U](self, mapper: Callable[[T], "_Option[U]"], /) -> "_Option[U]":
        if self._value is None:
            return Null()
        return mapper(self._value)

    def or_(self, optb: "_Option[T]", /) -> "_Option[T]":
        if self._value is None:
            return optb
        return self

    def or_else(self, f: Callable[[], "_Option[T]"], /) -> "_Option[T]":
        if self._value is None:
            return f()
        return self

    def take(self) -> T:
        if self._value is None:
            raise ValueError
        tmp = self._value
        self._value = None
        return tmp


@dataclass
class Some[T](_Option[T]):
    value: T


@dataclass
class Null[T: None](_Option[T]): ...


type Option[T] = Some[T] | Null[None]


def as_option[T](value: Optional[T]) -> Option[T]:
    if value is None:
        return Null()
    return Some(value)


def option[**P, T](f: Callable[P, Optional[T]]) -> Callable[P, Option[T]]:
    @wraps(f)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Option[T]:
        value = f(*args, **kwargs)
        return as_option(value)

    return wrapper
